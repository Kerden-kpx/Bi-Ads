import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig(({ mode }) => {
  // 加载环境变量
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      }
    },
    server: {
      host: env.VITE_HOST || '0.0.0.0', // 从环境变量读取，默认监听所有网络接口
      port: parseInt(env.VITE_PORT) || 5173, // 从环境变量读取端口
      open: false,
    },
    build: {
      // 生产环境构建优化
      minify: 'terser',
      terserOptions: {
        compress: {
          drop_console: true, // 移除console
          drop_debugger: true
        }
      },
      // 代码分割策略
      rollupOptions: {
        output: {
          // 手动分割代码块
          manualChunks: {
            // Vue核心库
            'vue-vendor': ['vue', 'vue-router'],
            // Element Plus UI库
            'element-plus': ['element-plus', '@element-plus/icons-vue'],
            // 图表库
            'charts': ['chart.js', 'vue-chartjs'],
            // 工具库
            'utils': ['axios', 'dayjs']
          },
          // 用于从入口点创建的块的打包输出格式
          chunkFileNames: 'js/[name]-[hash].js',
          entryFileNames: 'js/[name]-[hash].js',
          assetFileNames: '[ext]/[name]-[hash].[ext]'
        }
      },
      // 增加chunk大小警告限制
      chunkSizeWarningLimit: 1000,
      // 启用CSS代码分割
      cssCodeSplit: true,
      // 构建后是否生成source map文件
      sourcemap: false
    },
    // 优化依赖预构建
    optimizeDeps: {
      include: [
        'vue',
        'vue-router',
        'element-plus',
        '@element-plus/icons-vue',
        'chart.js',
        'vue-chartjs',
        'axios',
        'dayjs'
      ]
    },
    // CSS相关配置
    css: {
      // CSS预处理器选项
      preprocessorOptions: {
        // 如果使用scss
        // scss: {
        //   additionalData: `@import "@/styles/variables.scss";`
        // }
      },
      // 开发过程中是否启用source map
      devSourcemap: false
    }
  }
})
