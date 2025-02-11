<template>
  <div class="container">
    <header class="header">
      <h1>谣言识别和舆情分析平台</h1>
      <p>实时获取微博热门话题，进行谣言识别和舆情分析</p>
    </header>
    
    <TopicList />
  </div>
</template>

<script>
import TopicList from './components/TopicList.vue'

export default {
  name: 'App',
  components: {
    TopicList
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Microsoft YaHei', sans-serif;
  line-height: 1.6;
  padding: 20px;
  background-color: #f5f5f5;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.header {
  text-align: center;
  margin-bottom: 30px;
}

.header h1 {
  color: #1a73e8;
  margin-bottom: 10px;
}

.header p {
  color: #666;
  font-size: 16px;
}
</style>
