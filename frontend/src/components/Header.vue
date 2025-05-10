<template>
  <header class="app-header">
    <div class="container">
      <h1 class="logo">Google OAuth Demo</h1>
      <div class="auth-section">
        <div v-if="isLoggedIn" class="user-info">
          <img v-if="user.picture" :src="user.picture" alt="Profile" class="user-avatar">
          <span class="user-name">{{ user.name || 'User' }}</span>
          <button @click="logout" class="logout-btn">Sign Out</button>
        </div>
        <div v-else>
          <button @click="redirectToLogin" class="login-btn">Sign In</button>
        </div>
      </div>
    </div>
  </header>
</template>

<script>
import { apiService } from '../services/api';

export default {
  name: 'AppHeader',
  data() {
    return {
      isLoggedIn: false,
      user: {}
    };
  },
  async mounted() {
    try {
      const response = await apiService.get('/api/me');
      this.user = response.data;
      this.isLoggedIn = true;
    } catch (err) {
      console.error('Not authenticated:', err);
      this.isLoggedIn = false;
    }
  },
  methods: {
    redirectToLogin() {
      window.location.href = '/login';
    },
    async logout() {
      try {
        await apiService.post('/api/logout');
      } catch (error) {
        console.error('Logout error:', error);
      } finally {
        // 쿠키 삭제 등의 클라이언트 측 정리 작업
        localStorage.removeItem('userInfo');
        this.isLoggedIn = false;
        this.user = {};
        window.location.href = '/login';
      }
    }
  }
};
</script>

<style scoped>
.app-header {
  background-color: #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 1rem 0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 1.5rem;
  font-weight: 600;
  color: #4285f4;
  margin: 0;
}

.auth-section {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}

.user-name {
  font-weight: 500;
}

.login-btn, .logout-btn {
  background-color: #4285f4;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 0.5rem 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.login-btn:hover, .logout-btn:hover {
  background-color: #3367d6;
}

.logout-btn {
  background-color: #f1f3f4;
  color: #333;
  margin-left: 0.75rem;
}

.logout-btn:hover {
  background-color: #e8eaed;
}
</style> 