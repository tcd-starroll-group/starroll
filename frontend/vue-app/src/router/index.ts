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
      path: '/login',
      redirect: '/userLogin',
    },
    {
      path: '/blog-detail',
      name: 'BlogDetail',
      component: () => import('../views/BlogDetailView.vue'),
    },
    {
      path: '/add-blog',
      name: 'AddBlog',
      component: () => import('../views/AddBlogView.vue'),
    },
    {
      path: '/navigation',
      name: 'navigation',
      component: () => import('../views/NavigationView.vue'),
    },
    {
      path: '/star-blogs',
      name: 'StarBlogs',
      component: () => import('../views/StarBlogsView.vue'),
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
      path: '/user-details',
      name: 'UserDetails',
      component: () => import('../views/UserDetailsView.vue'),
    },
    {
      path: '/chat/:roomId',
      name: 'ChatRoom',
      component: () => import('../views/ChatRoomView.vue'),
    },
    {
      path: '/search',
      name: 'Search',
      component: () => import('../views/SearchView.vue'),
    },
  ],
})

// ARView needs body overflow:hidden (100vh canvas, no scroll).
// Every other page should be scrollable.
router.afterEach((to) => {
  document.body.style.overflow = to.path === '/' ? 'hidden' : 'auto'
})

// When entering ARView, reset any scroll offset that could misalign the canvas.
router.beforeEach((to) => {
  if (to.path === '/') {
    window.scrollTo(0, 0)
  }
})

export default router
