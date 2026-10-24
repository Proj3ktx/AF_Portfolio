// Composables
import { createRouter, createWebHistory } from 'vue-router'
import Home from "@/views/Home.vue"
import Resume from "@/views/Resume.vue"
import PortfolioItem from "@/views/PortfolioItem.vue"

const routes = [
  { 
    path: '/', 
    name: 'Home',
    component: Home
  },
  { 
    path: '/resume', 
    name: 'Resume',
    component: Resume
  },
  { 
    path: '/item/:name', 
    name: 'item',
    component: PortfolioItem,
    props: true
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
})

export default router
