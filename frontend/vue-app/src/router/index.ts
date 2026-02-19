import { createRouter, createWebHistory } from 'vue-router'
import SensorView from '../views/SensorView.vue'
import DiagnosticView from '../views/DiagnosticView.vue'

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
      path: '/',
      name: 'sensor',
      component: SensorView,
    },
    {
      path: '/diagnostic',
      name: 'diagnostic',
      component: DiagnosticView,
    },        

  ],
}
)




export default router

