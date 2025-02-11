<template>
  <div class="topic-item">
    <img 
      :src="avatarUrl" 
      :alt="topic.user_name" 
      class="user-avatar"
      :class="{ 'image-loading': isImageLoading }"
      @error="handleAvatarError"
      @load="handleImageLoad"
    >
    <div class="topic-content">
      <div class="topic-header">
        <span class="user-name">{{ topic.user_name }}</span>
        <span class="post-time">{{ topic.created_at }}</span>
        <span class="source">来自 {{ topic.source }}</span>
      </div>
      <div class="topic-text">{{ topic.text }}</div>
      <div v-if="topic.images" class="topic-images">
        <img 
          v-for="image in topicImages" 
          :key="image"
          :src="getImageUrl(image)"
          class="topic-image"
          :class="{ 'image-loading': isImageLoading }"
          @click="openImage(image)"
          @error="handleImageError"
          @load="handleImageLoad"
          alt="帖子图片"
        >
      </div>
      <div class="topic-stats">
        <span>转发: {{ topic.reposts_count }}</span>
        <span>评论: {{ topic.comments_count }}</span>
        <span>点赞: {{ topic.attitudes_count }}</span>
        <span>粉丝: {{ topic.user_followers_count }}</span>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { api } from '../services/api'

export default {
  name: 'TopicItem',
  props: {
    topic: {
      type: Object,
      required: true
    }
  },
  setup(props) {
    const isImageLoading = ref(true)
    const defaultAvatar = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%23999"><circle cx="12" cy="8" r="5"/><path d="M3,21c0-4.4,3.6-8,8-8h2c4.4,0,8,3.6,8,8"/></svg>'
    const defaultImage = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%23999"><path d="M21,19V5c0-1.1-0.9-2-2-2H5C3.9,3,3,3.9,3,5v14c0,1.1,0.9,2,2,2h14C20.1,21,21,20.1,21,19z M8.5,13.5l2.5,3l3.5-4.5l4.5,6H5l3.5-4.5z"/></svg>'

    const avatarUrl = computed(() => {
      return props.topic.user_avatar ? api.getProxyImageUrl(props.topic.user_avatar) : defaultAvatar
    })

    const topicImages = computed(() => {
      return props.topic.images ? props.topic.images.split('|') : []
    })

    const getImageUrl = (url) => {
      return api.getProxyImageUrl(url) || defaultImage
    }

    const handleAvatarError = (event) => {
      event.target.src = defaultAvatar
    }

    const handleImageError = (event) => {
      event.target.src = defaultImage
    }

    const handleImageLoad = () => {
      isImageLoading.value = false
    }

    const openImage = (url) => {
      window.open(url, '_blank')
    }

    return {
      isImageLoading,
      avatarUrl,
      topicImages,
      getImageUrl,
      handleAvatarError,
      handleImageError,
      handleImageLoad,
      openImage
    }
  }
}
</script>

<style scoped>
.topic-item {
  padding: 15px;
  border-bottom: 1px solid #eee;
  display: flex;
  gap: 15px;
}

.user-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  flex-shrink: 0;
  background-color: #f5f5f5;
  object-fit: cover;
}

.topic-content {
  flex: 1;
}

.topic-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
  color: #666;
  font-size: 14px;
}

.user-name {
  font-weight: bold;
  color: #1a73e8;
  font-size: 16px;
}

.post-time {
  color: #666;
  white-space: nowrap;
}

.source {
  color: #666;
}

.topic-text {
  margin-bottom: 10px;
  font-size: 15px;
  line-height: 1.6;
}

.topic-images {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin: 10px 0;
}

.topic-image {
  width: 150px;
  height: 150px;
  object-fit: cover;
  border-radius: 4px;
  cursor: pointer;
  transition: transform 0.2s;
  background-color: #f5f5f5;
}

.topic-image:hover {
  transform: scale(1.02);
}

.topic-stats {
  display: flex;
  gap: 15px;
  color: #666;
  font-size: 14px;
  margin-top: 10px;
}

.image-loading {
  opacity: 0.5;
}
</style>
