import { createRouter, createWebHistory } from "vue-router";
import Dashboard from "@/views/Dashboard.vue";
import Tables from "@/views/Tables.vue";
import Billing from "@/views/Billing.vue";
import Profile from "@/views/Profile.vue";
import SignIn from "@/views/SignIn.vue";
import SignUp from "@/views/SignUp.vue";
import AIAssistant from "@/views/AIAssistant.vue";
import ReportDetail from "../views/ReportDetail.vue";
import Forum from "../views/Forum.vue";
import PostDetail from "../views/PostDetail.vue";

const routes = [
  {
    path: "/",
    name: "/",
    redirect: "/dashboard",
  },
  {
    path: "/",
    name: "/",
    redirect: "/forum", // 将默认路径改为论坛页，方便调试
  },
  {
    path: "/forum",
    name: "Forum",
    component: Forum,
  },
  // 2. 添加新的动态路由规则
  {
    path: '/post/:id', // :id 是一个动态参数
    name: 'PostDetail',
    component: PostDetail,
    props: true // 这会将路由参数（如id）作为 props 传递给组件
  },
  {
    path: "/dashboard",
    name: "Dashboard",
    component: Dashboard,
  },
  {
    path: '/ai-assistant',
    name: 'AIAssistant',
    component: AIAssistant,
  },
  {
    path: "/tables",
    name: "Tables",
    component: Tables,
  },
  {
    path: "/billing",
    name: "Billing",
    component: Billing,
  },
  {
    path: "/profile",
    name: "Profile",
    component: Profile,
  },
  {
    path: "/sign-in",
    name: "Sign In",
    component: SignIn,
  },
  {
    path: "/sign-up",
    name: "Sign Up",
    component: SignUp,
  },
  {
    path: '/report-detail',
    name: 'ReportDetail',
    component: ReportDetail
  }

];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
  linkActiveClass: "active",
});

export default router;
