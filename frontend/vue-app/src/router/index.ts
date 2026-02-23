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
  ],
})

export default router
