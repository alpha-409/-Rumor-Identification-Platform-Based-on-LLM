<template>
  <div class="topics-container">
    <div class="controls">
      <div class="btn-group">
        <button 
          @click="fetchTopics" 
          :disabled="loading || autoRefreshing" 
          class="btn"
          title="手动获取最新数据"
        >
          {{ loading ? '获取中...' : '获取最新热门话题' }}
        </button>
        <button 
          @click="toggleAutoRefresh" 
          :class="['btn', 'btn-auto', { active: autoRefreshing }]"
          :title="autoRefreshing ? '点击停止自动更新' : '每10秒自动获取一次新数据'"
        >
          {{ autoRefreshing ? '停止自动更新' : '开启自动更新' }}
        </button>
      </div>
      <div class="refresh-info" v-if="autoRefreshing || refreshCount > 0">
        <div v-if="autoRefreshing" class="refresh-status">
          下次更新时间: {{ nextRefreshTime }}
        </div>
        <div v-if="refreshCount > 0" class="refresh-status">
          已自动更新 {{ refreshCount }} 次 | 累计获取 {{ totalTopics }} 条数据 | 已去重保存至CSV
        </div>
      </div>
    </div>

    <div v-if="error" class="error">
      {{ error }}
    </div>

    <div v-if="loading" class="loading">
      加载中...
    </div>

    <div v-else class="topics-list">
      <TopicItem 
        v-for="topic in topics" 
        :key="topic.id" 
        :topic="topic" 
      />
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { api } from '../services/api'
import TopicItem from './TopicItem.vue'

export default {
  name: 'TopicList',
  components: {
    TopicItem
  },
  setup() {
    const topics = ref([])
    const loading = ref(false)
    const error = ref(null)
    const autoRefreshing = ref(false)
    const refreshInterval = ref(null)
    const nextRefreshTime = ref('')
    const refreshCount = ref(0)
    const totalTopics = ref(0)

    const fetchTopics = async () => {
      loading.value = true
      error.value = null
      try {
        const response = await api.fetchHotTopics()
        topics.value = response.data
        if (autoRefreshing.value) {
          refreshCount.value++
          totalTopics.value += topics.value.length
        }
      } catch (err) {
        error.value = '获取数据失败: ' + (err.response?.data?.message || err.message)
        stopAutoRefresh()
      } finally {
        loading.value = false
        updateNextRefreshTime()
      }
    }

    const toggleAutoRefresh = () => {
      if (autoRefreshing.value) {
        stopAutoRefresh()
      } else {
        startAutoRefresh()
      }
    }

    const startAutoRefresh = () => {
      autoRefreshing.value = true
      refreshCount.value = 0
      totalTopics.value = 0
      fetchTopics()
      refreshInterval.value = setInterval(() => {
        fetchTopics()
      }, 10000)
      updateNextRefreshTime()
    }

    const stopAutoRefresh = () => {
      autoRefreshing.value = false
      if (refreshInterval.value) {
        clearInterval(refreshInterval.value)
        refreshInterval.value = null
      }
      nextRefreshTime.value = ''
    }

    const updateNextRefreshTime = () => {
      if (autoRefreshing.value) {
        const next = new Date(Date.now() + 10000)
        nextRefreshTime.value = next.toLocaleTimeString('zh-CN', {
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit'
        })
      }
    }

    onMounted(() => {
      fetchTopics()
    })

    onBeforeUnmount(() => {
      stopAutoRefresh()
    })

    return {
      topics,
      loading,
      error,
      autoRefreshing,
      nextRefreshTime,
      refreshCount,
      totalTopics,
      fetchTopics,
      toggleAutoRefresh
    }
  }
}
</script>

<style scoped>
.topics-container {
  width: 100%;
}

.controls {
  margin-bottom: 20px;
  text-align: center;
}

.btn-group {
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-bottom: 10px;
}

.btn {
  background-color: #1a73e8;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  min-width: 160px;
  transition: background-color 0.3s;
}

.btn:hover {
  background-color: #1557b0;
}

.btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.btn-auto {
  background-color: #34a853;
}

.btn-auto:hover {
  background-color: #2d8746;
}

.btn-auto.active {
  background-color: #dc3545;
}

.refresh-status {
  font-size: 14px;
  color: #666;
  margin-top: 5px;
  background-color: #f8f9fa;
  padding: 8px;
  border-radius: 4px;
  display: inline-block;
}

.refresh-info {
  display: flex;
  gap: 20px;
  justify-content: center;
  margin-top: 10px;
  flex-wrap: wrap;
}

.loading {
  text-align: center;
  padding: 20px;
  color: #666;
}

.error {
  color: #dc3545;
  text-align: center;
  padding: 10px;
  margin-bottom: 10px;
  background-color: #fff3f3;
  border-radius: 4px;
}

.topics-list {
  display: flex;
  flex-direction: column;
  gap: 1px;
  background-color: #f5f5f5;
}
</style>
