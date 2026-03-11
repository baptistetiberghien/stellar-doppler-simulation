<script setup lang="ts">
import { useRoute } from "vue-router";

const route = useRoute();
</script>

<template>
  <div class="app-shell">
    <nav class="top-nav">
      <router-link to="/" class="nav-link" :class="{ active: route.path === '/' }">
        Simple model
      </router-link>
      <router-link to="/advanced" class="nav-link" :class="{ active: route.path === '/advanced' }">
        Advanced model
      </router-link>
      <router-link to="/stochastic" class="nav-link" :class="{ active: route.path === '/stochastic' }">
        Stochastic spots
      </router-link>
    </nav>
    <router-view />
  </div>
</template>

<style scoped>
.app-shell {
  height: 100vh;
  width: 100vw;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #0f0f1a;
  color: #e0e0e0;
}

.top-nav {
  flex-shrink: 0;
  display: flex;
  gap: 0;
  background: #13132a;
  border-bottom: 1px solid #222;
  padding: 0 12px;
}

.nav-link {
  padding: 10px 20px;
  font-size: 13px;
  font-weight: 600;
  color: #888;
  text-decoration: none;
  border-bottom: 2px solid transparent;
  transition: color 0.15s, border-color 0.15s;
}
.nav-link:hover {
  color: #ccc;
}
.nav-link.active {
  color: #6ea8fe;
  border-bottom-color: #2563eb;
}
</style>
