<template>
  <div class="app">
    <AppHeader />
    <router-view @login-success="showLoginSuccessToast" @logout-success="showLogoutSuccessToast" />
    <Toast 
      :visible="toast.visible"
      :message="toast.message"
      :type="toast.type"
      @close="hideToast"
    />
  </div>
</template>

<script>
import AppHeader from './components/Header.vue';
import Toast from './components/Toast.vue';

export default {
  name: 'App',
  components: {
    AppHeader,
    Toast
  },
  data() {
    return {
      toast: {
        visible: false,
        message: '',
        type: 'info'
      }
    };
  },
  methods: {
    showToast(message, type = 'info') {
      this.toast = {
        visible: true,
        message,
        type
      };
    },
    hideToast() {
      this.toast.visible = false;
    },
    showLoginSuccessToast() {
      this.showToast('로그인되었습니다.', 'success');
    },
    showLogoutSuccessToast() {
      this.showToast('로그아웃되었습니다.', 'info');
    }
  }
};
</script>

<style>
/* Global CSS */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
    Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #333;
  background-color: #f5f5f5;
  line-height: 1.6;
}

.app {
  width: 100%;
  min-height: 100vh;
}

button {
  cursor: pointer;
  font-family: inherit;
}

a {
  color: #4285f4;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

h1, h2, h3, h4, h5, h6 {
  margin-bottom: 0.5rem;
  font-weight: 600;
  line-height: 1.25;
}
</style> 