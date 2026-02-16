<template>
  <div id="app">
    <Sidebar />
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script>
import Sidebar from './components/common/Sidebar.vue'

export default {
  name: 'App',
  components: {
    Sidebar
  }
}
</script>
