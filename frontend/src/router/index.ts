import { createRouter, createWebHashHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import MainLayout from '../layouts/MainLayout.vue'
import NewsView from '../views/NewsView.vue'
import UsersView from '../views/UsersView.vue'
import NewsCollectorView from '../views/NewsCollectorView.vue'
import DraftBoxView from '../views/DraftBoxView.vue'
import PublishedNewsView from '../views/PublishedNewsView.vue'
import MenuView from '../views/MenuView.vue'
import CategoryView from '../views/CategoryView.vue'
import WriteNewsView from '../views/WriteNewsView.vue'
import SettingsView from '../views/SettingsView.vue'
import NotFoundView from '../views/NotFoundView.vue'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: '/',
      name: 'login',
      component: LoginView
    },
    {
      path: '/main',
      component: MainLayout,
      children: [
        {
          path: '/news',
          name: 'news',
          component: NewsView
        },
        {
          path: '/news-summary',
          name: 'news-summary',
          component: NewsView
        },
        {
          path: '/news-collector',
          name: 'news-collector',
          component: NewsCollectorView
        },
        {
          path: '/draft-box',
          name: 'draft-box',
          component: DraftBoxView
        },
        {
          path: '/published-news',
          name: 'published-news',
          component: PublishedNewsView
        },
        {
          path: '/users',
          name: 'users',
          component: UsersView
        },
        {
          path: '/menu',
          name: 'menu',
          component: MenuView
        },
        {
          path: '/categories',
          name: 'categories',
          component: CategoryView
        },
        {
          path: '/write-news',
          name: 'write-news',
          component: WriteNewsView
        },
        {
          path: '/settings',
          name: 'settings',
          component: SettingsView
        },
        {
          path: '/404',
          name: 'not-found',
          component: NotFoundView
        },
        {
          path: '/:pathMatch(.*)*',
          name: 'catch-all',
          component: NotFoundView
        }
      ]
    }
  ]
})

export default router