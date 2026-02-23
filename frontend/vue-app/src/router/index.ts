import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
      {
    path: '/userLogin',
    name: 'Login',
    component: () => import('../views/LoginView.vue')
  },
  {
  path: '/userRegister',
  name: 'Register',
  component: () => import('../views/RegisterView.vue')
  },
    {
  path: '/changePassword',
  name: 'ChangePassword',
  component: () => import('../views/ChangePasswordView.vue')
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
  },
  {
  path: '/user-details',
  name: 'UserDetails',
  component: () => import('../views/UserDetailsView.vue')
  }    


  ],
}
)



export default router

