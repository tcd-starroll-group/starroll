import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
      {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue')
  },
  {
  path: '/register',
  name: 'Register',
  component: () => import('../views/RegisterView.vue')
  },
  {
  path: '/password-reset',
  name: 'PasswordReset',
  component: () => import('../views/PasswordResetView.vue')
  },
  {
  path: '/profile',
  name: 'Profile',
  component: () => import('../views/ProfileView.vue')
  },
  {
  path: '/star-detail',
  name: 'StarDetail',
  component: () => import('../views/StarDetailView.vue')
  }        

  ],
}
)



export default router

