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
    {
      path: "/stochastic",
      name: "stochastic",
      component: () => import("./pages/StochasticModel.vue"),
    },
  ],
});

export default router;
