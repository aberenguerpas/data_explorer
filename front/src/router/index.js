import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/results',
      name: 'results',
      component: () => import('../views/ResultsView.vue')
    },
    {
      path: '/dataset/:datasetId',
      name: 'dataset',
      component: () => import('../views/DatasetView.vue'),
      meta: {
        reload: true,
      }
    }
  ],
  scrollBehavior() {
      return {x: 0, y: 0}
  }
})

export default router
