<template>
  <div class="skeleton-loading">
    <!-- 卡片骨架屏 -->
    <div v-for="i in cardCount" :key="i" class="skeleton-card">
      <div class="skeleton-header">
        <div class="skeleton-title"></div>
      </div>
      <div class="skeleton-content">
        <div v-for="row in rowsPerCard" :key="row" class="skeleton-row">
          <div class="skeleton-cell" v-for="col in columnsPerRow" :key="col"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SkeletonLoading',
  props: {
    // 卡片数量
    cardCount: {
      type: Number,
      default: 3
    },
    // 每个卡片的行数
    rowsPerCard: {
      type: Number,
      default: 5
    },
    // 每行的列数
    columnsPerRow: {
      type: Number,
      default: 4
    }
  }
}
</script>

<style scoped>
.skeleton-loading {
  width: 100%;
  padding: 20px 0;
}

.skeleton-card {
  background: #ffffff;
  border-radius: 8px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.skeleton-header {
  padding: 20px 24px;
  border-bottom: 1px solid #ebeef5;
}

.skeleton-title {
  width: 200px;
  height: 24px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}

.skeleton-content {
  padding: 24px;
}

.skeleton-row {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

.skeleton-row:last-child {
  margin-bottom: 0;
}

.skeleton-cell {
  flex: 1;
  height: 40px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}

/* 为不同的单元格添加随机延迟，使动画更自然 */
.skeleton-cell:nth-child(1) {
  animation-delay: 0s;
}

.skeleton-cell:nth-child(2) {
  animation-delay: 0.1s;
}

.skeleton-cell:nth-child(3) {
  animation-delay: 0.2s;
}

.skeleton-cell:nth-child(4) {
  animation-delay: 0.3s;
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

/* 响应式设计 */
@media screen and (max-width: 768px) {
  .skeleton-header {
    padding: 16px;
  }

  .skeleton-content {
    padding: 16px;
  }

  .skeleton-row {
    flex-direction: column;
    gap: 12px;
  }

  .skeleton-cell {
    height: 32px;
  }
}
</style>

