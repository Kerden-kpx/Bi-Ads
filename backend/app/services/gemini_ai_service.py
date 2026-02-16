"""
Gemini AI 分析服务
"""
import json
from typing import Dict, Any, List, Optional
from google import genai
from app.core.config import settings


class GeminiAIService:
    """Gemini AI 服务类"""
    
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        """
        初始化 Gemini AI 服务
        
        Args:
            api_key: Gemini API 密钥（可选，默认使用配置）
            model_name: 模型名称（可选，默认使用配置）
        """
        self.api_key = api_key or settings.GEMINI_API_KEY
        
        # 获取所有可用的模型列表（用于自动轮换）
        if model_name:
            self.model_names = [model_name]
        else:
            self.model_names = settings.GEMINI_MODELS
        
        if not self.model_names:
            raise ValueError("未配置 GEMINI_MODEL，请在 .env 文件中设置")
        
        # 当前使用的模型（从第一个开始）
        self.current_model_index = 0
        self.model_name = self.model_names[0]
        
        if not self.api_key:
            raise ValueError("未配置 GEMINI_API_KEY，请在 .env 文件中设置")
        
        # 使用新版 Gemini API 创建客户端
        self.client = genai.Client(api_key=self.api_key)
    
    def analyze_impressions_reach_trend(
        self, 
        metrics_data: Dict[str, Any],
        date_range: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """分析展示和触达趋势数据"""
        prompt = self._build_impressions_reach_prompt(metrics_data, date_range)
        return self._analyze_with_gemini(prompt)
    
    def analyze_purchases_spend_trend(
        self, 
        metrics_data: Dict[str, Any],
        date_range: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """分析购买价值和花费趋势数据"""
        prompt = self._build_purchases_spend_prompt(metrics_data, date_range)
        return self._analyze_with_gemini(prompt)
    
    def analyze_google_top_funnel(
        self, 
        metrics_data: Dict[str, Any],
        date_range: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """分析Google Ads Top Funnel Overview数据"""
        prompt = self._build_google_top_funnel_prompt(metrics_data, date_range)
        return self._analyze_with_gemini(prompt)
    
    def analyze_google_conversion_cost(
        self, 
        metrics_data: Dict[str, Any],
        date_range: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """分析Google Ads Conversion Value & Cost Overview数据"""
        prompt = self._build_google_conversion_cost_prompt(metrics_data, date_range)
        return self._analyze_with_gemini(prompt)
    
    def _analyze_with_gemini(self, prompt: str) -> Dict[str, Any]:
        """使用 Gemini AI 进行分析的通用方法（支持模型自动轮换）"""
        last_error = None
        
        # 尝试所有配置的模型
        for attempt_index in range(len(self.model_names)):
            current_model = self.model_names[self.current_model_index]
            
            try:
                print(f"[Gemini AI] 尝试使用模型: {current_model} (第 {attempt_index + 1}/{len(self.model_names)} 次)")
                
                response = self.client.models.generate_content(
                    model=current_model,
                    contents=prompt
                )
                
                # 成功获取响应
                analysis_result = self._parse_analysis_response(response.text)
                analysis_result["generatedAt"] = self._get_current_timestamp()
                analysis_result["model"] = current_model
                
                print(f"[Gemini AI] ✓ 成功使用模型: {current_model}")
                return analysis_result
                
            except Exception as error:
                error_str = str(error)
                last_error = error
                
                # 检查是否是配额超限错误
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "quota" in error_str.lower():
                    print(f"[Gemini AI] ✗ 模型 {current_model} 配额已用完，尝试切换到下一个模型...")
                    
                    # 切换到下一个模型
                    self.current_model_index = (self.current_model_index + 1) % len(self.model_names)
                    
                    # 如果已经尝试了所有模型，抛出错误
                    if attempt_index == len(self.model_names) - 1:
                        raise Exception(f"所有配置的 {len(self.model_names)} 个模型配额都已用完，请稍后重试或升级到付费计划。详情：https://ai.google.dev/pricing")
                    
                    # 继续尝试下一个模型
                    continue
                else:
                    # 非配额错误，直接抛出
                    import traceback
                    traceback.print_exc()
                    raise Exception(f"Gemini AI 分析失败 (模型: {current_model}): {error_str}")
        
        # 如果所有模型都失败了
        import traceback
        traceback.print_exc()
        raise Exception(f"Gemini AI 分析失败: {str(last_error)}")
    
    def _get_date_description(self, date_range: Optional[Dict[str, str]]) -> str:
        """构建日期范围描述"""
        if date_range:
            return f"分析时间范围：{date_range.get('startDate', '')} 至 {date_range.get('endDate', '')}"
        return ""
    
    def _get_common_format_requirements(self) -> str:
        """获取公共的格式化要求"""
        return """
## 要求：

1. **trendAnalysis** 字段：
   - 使用 HTML 无序列表 <ul><li>...</li></ul> 格式
   - 每条格式：<li><strong>指标中文名（英文名）</strong>：总计XX，环比<span class="trend-down">小幅下降X.X%</span>。文字解读说明。</li>
   - 指标名称用 <strong> 加粗
   - 环比变化用 span 标签包裹：
     * 上升：<span class="trend-up">增长X.X%</span>（0-3%为小幅，3-8%为中等，8%+为大幅）
     * 下降：<span class="trend-down">下降X.X%</span>（0-3%为小幅，3-8%为中等，8%+为大幅）
     * 稳定：环比<span class="trend-stable">基本持平</span>

2. **keyFindings** 字段：
   - 只包含一个元素：总结段落
   - 综合分析整体趋势，指出核心问题和机会
   - 长度约100-150字

3. **recommendations** 字段：
   - 包含3-4条具体建议
   - 每条格式："<strong>1、建议标题</strong>：详细说明文字"
   - 使用中文序号（1、2、3、4、）开头
   - 标题部分用 <strong> 加粗，后面紧跟冒号
   - 建议要具体、可执行、有针对性

4. **JSON格式**：
   - 确保返回纯JSON，不要包含 ```json 或其他markdown标记
   - 所有字符串中的特殊字符必须正确转义
   - 数值类型使用数字而非字符串
   - 所有HTML内容都应该在一行内
   
**重要提醒**：JSON字符串内不能有未转义的控制字符，所有HTML内容都应该在一行内。"""
    
    def _build_impressions_reach_prompt(
        self, 
        metrics_data: Dict[str, Any],
        date_range: Optional[Dict[str, str]] = None
    ) -> str:
        """构建展示和触达分析提示词"""
        
        # 提取数据
        data = {
            'impressions': metrics_data.get('impressions', 0),
            'reach': metrics_data.get('reach', 0),
            'clicks': metrics_data.get('clicks', 0),
            'uniqueLinkClicks': metrics_data.get('uniqueLinkClicks', 0),
            'ctr': metrics_data.get('ctr', 0),
            'cpm': metrics_data.get('cpm', 0)
        }
        
        changes = {
            'impressions': metrics_data.get('impressionsChange', 0),
            'reach': metrics_data.get('reachChange', 0),
            'clicks': metrics_data.get('clicksChange', 0),
            'uniqueLinkClicks': metrics_data.get('uniqueLinkClicksChange', 0),
            'ctr': metrics_data.get('ctrChange', 0),
            'cpm': metrics_data.get('cpmChange', 0)
        }
        
        date_desc = self._get_date_description(date_range)
        
        prompt = f"""你是一位专业的Facebook广告数据分析专家。请基于以下汇总数据进行深入分析，并以JSON格式返回分析结果。

{date_desc}

# 汇总数据
- 总展示量（Impressions）：{data['impressions']:,}，环比变化 {changes['impressions']:+.2f}%
- 总触达（Reach）：{data['reach']:,}，环比变化 {changes['reach']:+.2f}%
- 总点击数（Clicks）：{data['clicks']:,}，环比变化 {changes['clicks']:+.2f}%
- 独立链接点击数（Unique Link Clicks）：{data['uniqueLinkClicks']:,}，环比变化 {changes['uniqueLinkClicks']:+.2f}%
- 平均点击率（CTR）：{data['ctr']:.2f}%，环比变化 {changes['ctr']:+.2f}%
- 千次曝光成本（CPM）：${data['cpm']:.2f}，环比变化 {changes['cpm']:+.2f}%

请严格按照以下模板格式进行分析，生成专业的数据分析报告：

## 参考模板示例：

**数据分析**
• 曝光量（Impressions）：总计403,645次，环比小幅下降0.2%。这表明广告的展示次数略有减少，基本保持稳定。
• 覆盖人数（Reach）：总计186,166人，环比下降7.99%。这是一个值得关注的信号，说明广告触达的独立用户数量减少了。
• 点击量（Clicks）：总计10,282次，环比下降3.46%。点击量的减少与覆盖人数的下降同步。
• 平均点击率（Avg. CTR）：为2.55%，环比下降3.26%。这是一个负面信号，表明广告内容对目标受众的吸引力有所减弱。
• 千次曝光成本（CPM）：为$15.64，环比小幅增长0.42%。这表明获取一千次曝光的成本基本保持稳定，没有显著增加。
• 独立链接点击量（Unique Link Clicks）：总计5,708次，环比下降6.79%。这表明真正点击广告并跳转到链接的独立用户数量有所减少，这是与点击量下降一致的趋势。

**总结**
最近一周内面临着流量和用户互动性的下滑。尽管曝光量基本持平，但覆盖人数、点击量和独立链接点击量均出现下降，尤其值得注意的是点击率（CTR）的下滑。这表明当前广告内容或受众定位的有效性可能正在减弱，导致单位成本下能吸引到的用户互动减少。但CPM的稳定增长说明市场竞争环境没有太大变化。

**下一步计划建议**
1、进行广告创意A/B测试：CTR的下降是当前面临的最大问题。应立即进行广告文案、图片或视频的A/B测试，寻找新的创意来提高用户兴趣和点击率。

2、重新评估受众定位：覆盖人数和点击量的下降可能意味着当前受众群体对广告的"疲劳度"增加。可以尝试拓展新的受众群体，或对现有受众进行更精细的细分，以寻找表现更好的目标用户。

3、关注转化数据：重点分析转化数据，确定哪些广告创意或受众在当前下滑趋势中依然能够带来有效的转化，并据此调整预算和策略。

---

## 你的任务：

请基于提供的实际数据，按照以上模板风格生成分析报告，返回JSON格式：

{{
  "summary": {{
    "totalImpressions": 数值,
    "totalReach": 数值,
    "totalClicks": 数值,
    "avgCTR": 数值
  }},
  "trendAnalysis": "详细的HTML格式数据分析段落（逐条分析：Impressions、Reach、Clicks、CTR、CPM、Unique Link Clicks）",
  "keyFindings": ["总结段落，概括整体趋势和核心发现"],
  "recommendations": ["建议1", "建议2", "建议3"]
}}

{self._get_common_format_requirements()}
"""
        return prompt
    
    def _build_purchases_spend_prompt(
        self, 
        metrics_data: Dict[str, Any],
        date_range: Optional[Dict[str, str]] = None
    ) -> str:
        """构建购买价值和花费分析提示词"""
        
        # 提取数据
        data = {
            'spend': metrics_data.get('spend', 0),
            'purchasesValue': metrics_data.get('purchasesValue', 0),
            'purchaseRoas': metrics_data.get('purchaseRoas', 0),
            'addsToCart': metrics_data.get('addsToCart', 0),
            'addsPaymentInfo': metrics_data.get('addsPaymentInfo', 0),
            'purchases': metrics_data.get('purchases', 0)
        }
        
        changes = {
            'spend': metrics_data.get('spendChange', 0),
            'purchasesValue': metrics_data.get('purchasesValueChange', 0),
            'purchaseRoas': metrics_data.get('purchaseRoasChange', 0),
            'addsToCart': metrics_data.get('addsToCartChange', 0),
            'addsPaymentInfo': metrics_data.get('addsPaymentInfoChange', 0),
            'purchases': metrics_data.get('purchasesChange', 0)
        }
        
        date_desc = self._get_date_description(date_range)
        
        prompt = f"""你是一位专业的Facebook广告数据分析专家。请基于以下购买价值和花费数据进行深入分析，并以JSON格式返回分析结果。

{date_desc}

# 汇总数据
- 花费（Spend）：${data['spend']:,.2f}，环比变化 {changes['spend']:+.2f}%
- 购买价值（Purchases Value）：${data['purchasesValue']:,.2f}，环比变化 {changes['purchasesValue']:+.2f}%
- 购买ROAS（Purchase ROAS）：{data['purchaseRoas']:.2f}，环比变化 {changes['purchaseRoas']:+.2f}%
- 加入购物车（Adds to Cart）：{data['addsToCart']:,}次，环比变化 {changes['addsToCart']:+.2f}%
- 添加支付信息（Adds Payment Info）：{data['addsPaymentInfo']:,}次，环比变化 {changes['addsPaymentInfo']:+.2f}%
- 购买量（Purchases）：{data['purchases']:,}次，环比变化 {changes['purchases']:+.2f}%

请严格按照以下模板格式进行分析，生成专业的数据分析报告：

## 参考模板示例：

**数据分析**
• 花费（Spend）：总计$6,311.18，环比小幅增长0.22%。广告预算基本保持稳定。
• 购买价值（Purchases Value）：总计$17,230.91，环比小幅增长0.13%。广告带来的总收入基本保持稳定。
• 购买ROAS（Purchase ROAS）：为2.73，环比小幅下降0.09%。广告支出回报率基本持平。
• 加入购物车（Adds to Cart）：总计1,062次，环比大幅下降9.31%。这是转化漏斗中上游的重要指标，其下降表明进入漏斗的用户数量减少。
• 添加支付信息（Adds Payment Info）：总计116次，环比大幅增长10.48%。这是用户转化路径中非常关键的一步，其大幅增长是一个积极的信号。
• 购买量（Purchases）：总计284次，环比小幅增长5.19%。最终购买量的增长是广告投放的直接成果，这表明转化漏斗的最终环节表现良好。

**总结** 
本周广告数据，尽管"加入购物车"这一上游转化指标出现了显著下滑，但"添加支付信息"和最终的"购买量"却实现了增长。这表明广告成功吸引了更少但质量更高的潜在客户。这些客户的购买意愿更强，从而在转化漏斗的后端表现出更高的效率。总购买价值和ROAS基本保持稳定，这进一步佐证了广告花费的效率并未受损，而是通过更精准的流量投放，实现了更高的转化质量。

**下一步计划**
 1、深入分析转化漏斗： 重点关注从"加入购物车"到"购买"这一环节。虽然进入漏斗的用户少了，但最终购买的人却多了。根据数据优化广告策略。
2、优化广告创意和受众： "加入购物车"的下降可能与广告创意吸引力减弱或受众定位不精准有关。可以尝试对广告创意进行A/B测试，并重新评估受众，以吸引更多对产品有兴趣的潜在客户。
3、重新优化分配预算，还有产品预算倾斜；
4、持续监控数据： 关注未来几周的"加入购物车"数据，看是否能够通过优化策略使其回升，同时保持"添加支付信息"和"购买量"的增长势头。

---

## 你的任务：

请基于提供的实际数据，按照以上模板风格生成分析报告，返回JSON格式：

{{
  "summary": {{
    "totalSpend": 数值,
    "totalPurchasesValue": 数值,
    "purchaseRoas": 数值,
    "totalPurchases": 数值
  }},
  "trendAnalysis": "详细的HTML格式数据分析段落（逐条分析：Spend、Purchases Value、Purchase ROAS、Adds to Cart、Adds Payment Info、Purchases）",
  "keyFindings": ["总结段落，特别关注转化漏斗变化（加入购物车→添加支付信息→购买）"],
  "recommendations": ["建议1（关注转化漏斗优化）", "建议2（广告创意和受众）", "建议3（预算分配）", "建议4（数据监控）"]
}}

{self._get_common_format_requirements()}

**特别提示**：重点分析转化漏斗的上游（加入购物车）、中游（添加支付信息）和下游（购买）之间的关系和趋势变化。
"""
        return prompt
    
    def _build_google_top_funnel_prompt(
        self, 
        metrics_data: Dict[str, Any],
        date_range: Optional[Dict[str, str]] = None
    ) -> str:
        """构建Google Ads Top Funnel Overview分析提示词"""
        
        # 提取数据并转换为正确的类型
        data = {
            'impressions': float(metrics_data.get('impressions', 0)),
            'clicks': float(metrics_data.get('clicks', 0)),
            'avgCpc': float(metrics_data.get('avgCpc', 0)),
            'ctr': float(metrics_data.get('ctr', 0))
        }
        
        # 提取变化值并转换为数字类型（可能是字符串）
        def to_float(value):
            """安全地转换为浮点数"""
            if value is None:
                return 0.0
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str):
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return 0.0
            return 0.0
        
        changes = {
            'impressions': to_float(metrics_data.get('impressionsChange', 0)),
            'clicks': to_float(metrics_data.get('clicksChange', 0)),
            'avgCpc': to_float(metrics_data.get('avgCpcChange', 0)),
            'ctr': to_float(metrics_data.get('ctrChange', 0))
        }
        
        date_desc = self._get_date_description(date_range)
        
        prompt = f"""你是一位专业的Google Ads广告数据分析专家。请基于以下Top Funnel Overview数据进行深入分析，并以JSON格式返回分析结果。

{date_desc}

# 汇总数据
- 曝光量（Impressions）：{data['impressions']:,.0f}次，较上周变化 {changes['impressions']:+.2f}%
- 点击量（Clicks）：{data['clicks']:,.0f}次，较上周变化 {changes['clicks']:+.2f}%
- 平均每次点击费用（Avg. CPC）：${data['avgCpc']:.2f}，较上周变化 {changes['avgCpc']:+.2f}%
- 平均点击率（Avg. CTR）：{data['ctr']:.2f}%，较上周变化 {changes['ctr']:+.2f}%

请严格按照以下模板格式进行分析，生成专业的数据分析报告：

## 参考模板示例：

**数据分析**
• 曝光量（Impressions）：112,714次，较上周增长7.48%。这表明您的广告被展示的次数略有增加。
• 点击量（Clicks）：1,769次，较上周增长9.05%。用户对广告的互动意愿有所增强。
• 平均每次点击费用（Avg. CPC）：$0.70，较上周增长1.45%。这意味着您获取每次点击的成本略有上升，但基本保持稳定。
• 平均点击率（Avg. CTR）：1.57%，较上周增长10.81%。这是一个积极的信号，表示您的广告内容对目标受众的吸引力有所提升，用户更愿意点击。

**总结**
整体来看，广告在上周表现稳健，并呈现出积极的优化趋势。曝光量和点击量均有小幅增长，显示了广告的持续触达能力。最值得关注的是，平均点击率（CTR）实现了10.81%的显著增长，达到1.57%。这表明您的广告创意或关键词定位更加精准地吸引了用户。同时，平均每次点击费用（CPC）虽然略有增长，但幅度很小，基本保持在稳定水平，这意味着您在提高CTR的同时，有效地控制了成本。

**下一步计划建议**
1、密切关注转化数据，确保点击质量：结合转化数据分析，虽然CTR上升是好事，但最终目标是转化。务必结合转化次数、转化价值和ROAS等数据进行综合分析，确保这些新增的点击是高质量的，能够带来后续的转化行为。如果CTR提升但转化未相应提升，可能需要优化着陆页或广告与着陆页的匹配度。

2、合理控制CPC，维持成本效益：检查当前的竞价策略是否与您的业务目标相符。如果未来CPC出现显著上涨，可以考虑调整竞价策略或出价上限。

3、优化关键词和广告创意：持续进行A/B测试，找出表现最佳的广告文案和关键词组合，进一步提升CTR和转化率。

4、监控竞争环境：关注竞争对手的广告策略变化，及时调整自己的投放策略以保持竞争优势。

---

## 你的任务：

请基于提供的实际数据，按照以上模板风格生成分析报告，返回JSON格式：

{{
  "summary": {{
    "totalImpressions": 数值,
    "totalClicks": 数值,
    "avgCpc": 数值,
    "avgCTR": 数值
  }},
  "trendAnalysis": "详细的HTML格式数据分析段落（逐条分析：Impressions、Clicks、Avg. CPC、Avg. CTR）",
  "keyFindings": ["总结段落，概括整体趋势和核心发现"],
  "recommendations": ["建议1", "建议2", "建议3", "建议4"]
}}

{self._get_common_format_requirements()}

**特别提示**：重点分析曝光量、点击量、CPC和CTR之间的关系，以及这些指标如何影响广告的整体效果和成本效益。
"""
        return prompt
    
    def _build_google_conversion_cost_prompt(
        self, 
        metrics_data: Dict[str, Any],
        date_range: Optional[Dict[str, str]] = None
    ) -> str:
        """构建Google Ads Conversion Value & Cost Overview分析提示词"""
        
        # 提取数据并转换为正确的类型
        # 安全转换函数
        def to_float(value):
            """安全地转换为浮点数"""
            if value is None:
                return 0.0
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str):
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return 0.0
            return 0.0
        
        data = {
            'purchasesValue': to_float(metrics_data.get('purchasesValue', 0)),
            'spend': to_float(metrics_data.get('spend', 0)),
            'purchases': to_float(metrics_data.get('purchases', 0)),
            'roas': to_float(metrics_data.get('roas', 0))
        }
        
        changes = {
            'purchasesValue': to_float(metrics_data.get('purchasesValueChange', 0)),
            'spend': to_float(metrics_data.get('spendChange', 0)),
            'purchases': to_float(metrics_data.get('purchasesChange', 0)),
            'roas': to_float(metrics_data.get('roasChange', 0))
        }
        
        date_desc = self._get_date_description(date_range)
        
        prompt = f"""你是一位专业的Google Ads广告数据分析专家。请基于以下Conversion Value & Cost Overview数据进行深入分析，并以JSON格式返回分析结果。

{date_desc}

# 汇总数据
- 转化价值（Conversion Value）：${data['purchasesValue']:,.2f}，较上周变化 {changes['purchasesValue']:+.2f}%
- 成本（Cost）：${data['spend']:,.2f}，较上周变化 {changes['spend']:+.2f}%
- 转化次数（Conversions）：{data['purchases']:,.0f}次，较上周变化 {changes['purchases']:+.2f}%
- 广告支出回报率（ROAS）：{data['roas']:.2f}，较上周变化 {changes['roas']:+.2f}%

请严格按照以下模板格式进行分析，生成专业的数据分析报告：

## 参考模板示例：

**数据分析**
• 转化价值（Conversion Value）：$3,983.46，较上周下降41.13%。广告带来的总转化收入显著减少。
• 成本（Cost）：$1,230.67，较上周下降10.37%。广告花费有所减少。
• 转化次数（Conversions）：67次，较上周下降26.32%。广告促成的转化行为数量减少了。
• 广告支出回报率（ROAS）：3.24，较上周下降34.33%。ROAS出现了显著下降，表明广告效率降低。

**总结**
广告在过去一周的转化表现出现了明显的下滑。尽管广告成本有所下降（10.37%），但转化次数（-26.32%）和转化价值（-41.13%）的跌幅更为显著。因此，广告支出回报率（ROAS）也大幅下降了34.33%，降至3.24。这表明您每投入一美元广告费所获得的回报减少了，广告效率明显下降。

**下一步计划建议**
1、优化ROAS，提升效率：重新评估目标CPA/ROAS，根据实际情况调整您的目标每次转化费用或目标ROAS。基于设备、地理位置、时段、受众等细分数据，进行更精细的出价调整。

2、重新审视广告内容和受众定位：强化再营销广告，针对那些已经访问过网站但未转化的用户进行精准投放，提供额外的激励。

3、持续监控和A/B测试：密切关注每日的ROAS和转化趋势，尤其是在进行调整后。对任何优化措施进行A/B测试，确保更改是有效的。

4、优化转化路径：检查着陆页的加载速度、用户体验和转化流程，确保没有技术问题阻碍用户完成转化。

---

## 你的任务：

请基于提供的实际数据，按照以上模板风格生成分析报告，返回JSON格式：

{{
  "summary": {{
    "totalConversionValue": 数值,
    "totalCost": 数值,
    "totalConversions": 数值,
    "roas": 数值
  }},
  "trendAnalysis": "详细的HTML格式数据分析段落（逐条分析：Conversion Value、Cost、Conversions、ROAS）",
  "keyFindings": ["总结段落，概括整体转化表现和效率变化"],
  "recommendations": ["建议1", "建议2", "建议3", "建议4"]
}}

{self._get_common_format_requirements()}

**特别提示**：重点分析转化价值、成本、转化次数和ROAS之间的关系，特别关注ROAS的变化趋势以及成本效益。如果ROAS下降，需要深入分析是转化价值下降还是成本上升导致的，并提供针对性的优化建议。
"""
        return prompt
    
    def _clean_json_text(self, text: str) -> str:
        """清理 JSON 文本"""
        import re
        # 移除 markdown 代码块标记
        cleaned = text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        # 清理 ASCII 控制字符
        cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', cleaned)
        return cleaned.strip()
    
    def _parse_analysis_response(self, response_text: str) -> Dict[str, Any]:
        """解析 Gemini 返回的分析结果"""
        try:
            cleaned_text = self._clean_json_text(response_text)
            result = json.loads(cleaned_text)
            
            # 验证必要字段
            required_fields = ["summary", "trendAnalysis", "keyFindings", "recommendations"]
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"缺少必要字段: {field}")
            
            return result
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"JSON解析失败: {str(e)}")
            print(f"原始响应（前500字符）: {response_text[:500]}")
            
            # 尝试提取 JSON
            fallback = self._extract_fallback_json(response_text)
            if fallback:
                return fallback
            
            # 返回默认结构
            return {
                "summary": {"totalImpressions": 0, "totalReach": 0, "totalClicks": 0, "avgCTR": 0},
                "trendAnalysis": "<p>AI分析服务暂时不可用，请稍后重试。</p>",
                "keyFindings": ["系统正在优化中，请稍后重新生成分析报告"],
                "recommendations": ["建议：稍后重试，或联系技术支持"]
            }
    
    def _extract_fallback_json(self, text: str) -> Optional[Dict[str, Any]]:
        """从非标准格式的响应中提取 JSON"""
        try:
            import re
            json_match = re.search(r'\{[\s\S]*"summary"[\s\S]*"trendAnalysis"[\s\S]*"keyFindings"[\s\S]*"recommendations"[\s\S]*\}', text)
            if json_match:
                return json.loads(self._clean_json_text(json_match.group(0)))
        except:
            pass
        return None
    
    def _get_current_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()


# 创建全局服务实例（延迟初始化）
_gemini_service_instance = None


def get_gemini_service() -> GeminiAIService:
    """获取 Gemini AI 服务实例（单例模式）"""
    global _gemini_service_instance
    if _gemini_service_instance is None:
        _gemini_service_instance = GeminiAIService()
    return _gemini_service_instance

