<template>
  <div class="home-page">
    <div v-if="loading" class="loading">
      <p>Loading...</p>
    </div>
    <div v-else-if="error" class="error">
      <h2>Authentication Error</h2>
      <p>{{ error }}</p>
      <button @click="redirectToLogin" class="login-btn">Go to Login</button>
    </div>
    <div v-else class="profile-container">
      <div class="profile-header">
        <h1>Welcome, {{ user.name || 'User' }}</h1>
        <img v-if="user.picture" :src="user.picture" alt="Profile picture" class="profile-image" />
      </div>
      
      <div class="profile-info">
        <h2>Your Profile</h2>
        <div class="info-item">
          <span class="label">Email:</span>
          <span class="value">{{ user.email }}</span>
        </div>
        <div class="info-item">
          <span class="label">User ID:</span>
          <span class="value">{{ user.user_id }}</span>
        </div>
        <div class="info-item">
          <span class="label">Role:</span>
          <span class="value">{{ user.role }}</span>
        </div>
      </div>
      
      <div class="actions">
        <button @click="fetchProtectedData" class="action-btn primary">
          Test Protected Endpoint
        </button>
        <button @click="logout" class="action-btn secondary">
          Sign Out
        </button>
      </div>
      
      <div v-if="protectedData" class="protected-data">
        <h3>Protected Data Response:</h3>
        <pre>{{ JSON.stringify(protectedData, null, 2) }}</pre>
      </div>
    </div>
  </div>
</template>

<script>
import { apiService } from '../services/api';

export default {
  name: 'HomeView',
  data() {
    return {
      user: {},
      loading: true,
      error: null,
      protectedData: null
    };
  },
  async mounted() {
    try {
      const response = await apiService.get('/api/me');
      this.user = response.data;
      this.loading = false;
      
      // URL 파라미터에서 로그인 상태 확인
      const urlParams = new URLSearchParams(window.location.search);
      if (urlParams.get('login') === 'success') {
        this.$emit('login-success');
        // 파라미터 제거하여 URL 정리
        window.history.replaceState({}, document.title, window.location.pathname);
      }
    } catch (err) {
      console.error('Authentication error:', err);
      this.error = 'You are not authenticated. Please log in.';
      this.loading = false;
    }
  },
  methods: {
    redirectToLogin() {
      window.location.href = '/login';
    },
    
    async fetchProtectedData() {
      try {
        const response = await apiService.get('/api/protected');
        this.protectedData = response.data;
      } catch (err) {
        console.error('Error fetching protected data:', err);
        this.protectedData = { error: 'Failed to fetch protected data' };
      }
    },
    
    async logout() {
      try {
        await apiService.post('/api/logout');
        this.$emit('logout-success');
      } catch (err) {
        console.error('Logout error:', err);
      }
      // 로그아웃 후 로그인 페이지로 이동
      this.redirectToLogin();
    }
  }
};
</script>

<style scoped>
.home-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

.loading, .error {
  text-align: center;
  padding: 3rem;
}

.profile-container {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

.profile-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.profile-image {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #fff;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.profile-info {
  margin-bottom: 2rem;
}

.info-item {
  display: flex;
  margin-bottom: 0.75rem;
}

.label {
  width: 100px;
  font-weight: 600;
  color: #555;
}

.value {
  flex: 1;
  color: #333;
}

.actions {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}

.action-btn {
  padding: 0.75rem 1.25rem;
  border: none;
  border-radius: 4px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.primary {
  background-color: #4285f4;
  color: white;
}

.primary:hover {
  background-color: #3367d6;
}

.secondary {
  background-color: #f1f3f4;
  color: #333;
}

.secondary:hover {
  background-color: #e8eaed;
}

.protected-data {
  margin-top: 2rem;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 4px;
  overflow: auto;
}

pre {
  margin: 0;
  white-space: pre-wrap;
}

.login-btn {
  margin-top: 1rem;
  padding: 0.75rem 1.5rem;
  background-color: #4285f4;
  color: white;
  border: none;
  border-radius: 4px;
  font-weight: 600;
  cursor: pointer;
}

.login-btn:hover {
  background-color: #3367d6;
}
</style> 