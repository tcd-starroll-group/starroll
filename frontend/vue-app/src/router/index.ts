import { createRouter, createWebHistory } from 'vue-router'
import ARView from '../views/ARView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'ar',
      component: ARView,
    },
    {
      path: '/userLogin',
      name: 'Login',
      component: () => import('../views/LoginView.vue'),
    },
    {
      path: '/add-blog',
      name: 'AddBlog',
      component: () => import('../views/AddBlogView.vue'), 
    },
    {
      path: '/Navigation',
      name: 'Navigation',
      component: () => import('../views/NavigationView.vue'),
    },
    {
      path: '/BlogIndex',
      name: 'BlogIndex',
      component: () => import('../views/BlogIndexView.vue'),
    },
    {
      path: '/Recognizer',
      name: 'Recognizer',
      component: () => import('../views/RecognizerView.vue'),
    },
    {
      path: '/userRegister',
      name: 'Register',
      component: () => import('../views/RegisterView.vue'),
    },
    {
      path: '/changePassword',
      name: 'ChangePassword',
      component: () => import('../views/ChangePasswordView.vue'),
    },
    {
      path: '/password-reset',
      name: 'PasswordReset',
      component: () => import('../views/PasswordResetView.vue'),
    },
    {
      path: '/profile',
      name: 'Profile',
      component: () => import('../views/ProfileView.vue'),
    },
    {
      path: '/star-detail',
      name: 'StarDetail',
      component: () => import('../views/StarDetailView.vue'),
    },
    {
      path: '/user-details',
      name: 'UserDetails',
      component: () => import('../views/UserDetailsView.vue'),
    },
  ],
})
export default router
