import { createRouter, createWebHistory } from 'vue-router'
import SensorView from '../views/SensorView.vue'
import DiagnosticView from '../views/DiagnosticView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
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
})

export default router
