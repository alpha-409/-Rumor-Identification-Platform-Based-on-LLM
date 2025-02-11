import axios from 'axios'

export const api = {
  async fetchHotTopics() {
    const response = await axios.get('/api/fetch-hot-topics')
    return response.data
  },

  getProxyImageUrl(url) {
    if (!url) return null
    return `/api/proxy-image?url=${encodeURIComponent(url)}`
  }
}
