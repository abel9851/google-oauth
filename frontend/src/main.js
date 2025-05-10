import { createApp } from 'vue';
import { createRouter, createWebHistory } from 'vue-router';
import App from './App.vue';

import Home from './views/Home.vue';
import Login from './views/Login.vue';

// Create router
const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: Home,
    },
    {
      path: '/login',
      component: Login,
    },
    // Redirect all other routes to home
    {
      path: '/:pathMatch(.*)*',
      redirect: '/'
    }
  ]
});

// Create and mount the Vue app
const app = createApp(App);
app.use(router);
app.mount('#app'); 