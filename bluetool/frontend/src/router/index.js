import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Upload from '../views/Upload.vue'
import Parse from '../views/Parse.vue'
import TestPoints from '../views/TestPoints.vue'
import TestCases from '../views/TestCases.vue'
import History from '../views/History.vue'

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/upload', name: 'Upload', component: Upload },
  { path: '/parse/:fileId', name: 'Parse', component: Parse, props: true },
  { path: '/test-points', name: 'TestPoints', component: TestPoints },
  { path: '/test-cases', name: 'TestCases', component: TestCases },
  { path: '/history', name: 'History', component: History }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
