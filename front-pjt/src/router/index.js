import NotFoundView from "@/views/NotFoundView.vue";
import { createRouter, createWebHistory } from "vue-router";
import NewsView from "@/views/NewsView.vue";
import NewsDetailView from "@/views/NewsDetailView.vue";
import DashBoardView from "@/views/DashBoardView.vue";
import LoginPage from "@/views/LoginPage.vue";
import SignUp from "@/views/SignUp.vue";

const router = createRouter({
  history: createWebHistory("/"),
  routes: [
    {
      path: "/",
      name: 'Home',
      component: LoginPage,
    },
    {
      path: "/login",
      name: 'Login',
      component: LoginPage,
    },

    {
      path: '/signup',
      name: 'SignUp',
      component: SignUp,
    },
    {
      path: "/news",
      name: "News",
      component: NewsView,
    },
    {
      path: "/news/:id",
      name: "newsDetail",
      component: NewsDetailView,
      props: true,
      meta: { requiresAuth: true },
    },
    {
      path: "/dashboard",
      name: "dashboard",
      component: DashBoardView,
      meta: { requiresAuth: true },
    },
    {
      path: "/:pathMatch(.*)*",
      component: NotFoundView,
    },
    {
      path: '/user/:userId/bookmarks',
      name: 'BookmarkList',
      component: () => import('@/views/BookmarkListView.vue'),
      meta: { requiresAuth: true }
    }
  ],
});

router.beforeEach((to, from, next) => {
  const isLoggedIn = !!localStorage.getItem("accessToken");

  if (to.meta.requiresAuth && !isLoggedIn) {
    next({ path: "/" }); // 로그인 페이지로 리다이렉트
  } else {
    next();
  }
});

export default router;