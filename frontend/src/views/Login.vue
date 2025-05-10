<template>
  <div class="login-page">
    <div class="login-header">
      <h1>Google OAuth Demo</h1>
      <p>Sign in with your Google account to continue</p>
    </div>
    <LoginButton />
  </div>
</template>

<script>
import LoginButton from '../components/LoginButton.vue';

export default {
  name: 'LoginView',
  components: {
    LoginButton
  }
};
</script>

<style scoped>
.login-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 2rem;
  background-color: #f9f9f9;
}

.login-header {
  text-align: center;
  margin-bottom: 2rem;
}

h1 {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
  color: #333;
}

p {
  font-size: 1.1rem;
  color: #666;
  max-width: 600px;
}
</style> 