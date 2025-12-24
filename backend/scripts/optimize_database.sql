-- ==========================================
-- 数据库性能优化脚本
-- 用于创建索引、优化查询性能
-- ==========================================

-- 1. Google Ads 表索引优化
-- ==========================================

-- 日期索引（用于日期范围查询）
CREATE INDEX IF NOT EXISTS idx_google_ads_createtime 
ON google_ads (createtime);

-- 复合索引（用于按日期和广告系列查询）
CREATE INDEX IF NOT EXISTS idx_google_ads_campaign_date 
ON google_ads (campaign_id, createtime);

-- 优化统计查询
CREATE INDEX IF NOT EXISTS idx_google_ads_stats 
ON google_ads (createtime, campaign_id, impression, Clicks, Cost);


-- 2. Facebook Ads 表索引优化
-- ==========================================

-- 日期索引（用于日期范围查询）
CREATE INDEX IF NOT EXISTS idx_facebook_ads_createtime 
ON facebook_ads (createtime);

-- 账户ID索引（用于多账户查询）
CREATE INDEX IF NOT EXISTS idx_facebook_ads_account 
ON facebook_ads (account_id, createtime);

-- 复合索引（用于广告系列和日期查询）
CREATE INDEX IF NOT EXISTS idx_facebook_ads_campaign_date 
ON facebook_ads (campaign_id, createtime);

-- 广告组索引
CREATE INDEX IF NOT EXISTS idx_facebook_ads_adset_date 
ON facebook_ads (adset_id, createtime);

-- 广告ID索引
CREATE INDEX IF NOT EXISTS idx_facebook_ads_ad_date 
ON facebook_ads (ad_id, createtime);

-- 优化统计查询（包含常用字段）
CREATE INDEX IF NOT EXISTS idx_facebook_ads_stats 
ON facebook_ads (createtime, account_id, impression, spend, purchases);


-- 3. 清理过期数据（可选）
-- ==========================================

-- 删除超过1年的历史数据（根据实际需求调整）
-- DELETE FROM google_ads WHERE createtime < DATE_SUB(CURDATE(), INTERVAL 365 DAY);
-- DELETE FROM facebook_ads WHERE createtime < DATE_SUB(CURDATE(), INTERVAL 365 DAY);


-- 4. 数据库优化建议
-- ==========================================

-- 分析表以更新统计信息
ANALYZE TABLE google_ads;
ANALYZE TABLE facebook_ads;

-- 优化表（整理碎片）
OPTIMIZE TABLE google_ads;
OPTIMIZE TABLE facebook_ads;


-- 5. 查看索引使用情况
-- ==========================================

-- 查看 Google Ads 表索引
SHOW INDEX FROM google_ads;

-- 查看 Facebook Ads 表索引
SHOW INDEX FROM facebook_ads;


-- 6. 性能监控查询
-- ==========================================

-- 查看慢查询日志设置
SHOW VARIABLES LIKE 'slow_query%';

-- 查看查询缓存设置
SHOW VARIABLES LIKE 'query_cache%';

-- 查看InnoDB缓冲池大小
SHOW VARIABLES LIKE 'innodb_buffer_pool_size';


-- ==========================================
-- 执行说明：
-- 1. 在数据库客户端中运行此脚本
-- 2. 建议在非高峰时段执行
-- 3. 索引创建可能需要几分钟（取决于数据量）
-- 4. 定期执行 ANALYZE 和 OPTIMIZE 以保持性能
-- ==========================================

