import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "simple",
      component: () => import("./pages/SimpleModel.vue"),
    },
    {
      path: "/advanced",
      name: "advanced",
      component: () => import("./pages/AdvancedModel.vue"),
    },
  ],
});

export default router;
