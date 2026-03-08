<script setup lang="ts">
import { onMounted } from "vue";
import StarView from "./components/StarView.vue";
import SpectrumPlot from "./components/SpectrumPlot.vue";
import ControlsPanel from "./components/ControlsPanel.vue";
import { useSimulation } from "./composables/useSimulation";
import type { SimulationParams } from "./types/simulation";

const { params, result, loading, error, fetchSimulation } = useSimulation();

function onParamUpdate(key: keyof SimulationParams, value: number) {
  (params as Record<string, number>)[key] = value;
}

onMounted(fetchSimulation);
</script>

<template>
  <div class="app-layout">
    <!-- Left column: star + controls -->
    <aside class="left-col">
      <div class="star-section">
        <StarView :params="params" :result="result" />
      </div>
      <ControlsPanel :params="params" @update:params="onParamUpdate" />
    </aside>

    <!-- Right column: spectrum (full height) -->
    <main class="right-col">
      <SpectrumPlot :result="result" />
      <div v-if="loading" class="status-badge loading">Computing…</div>
      <div v-if="error" class="status-badge error">{{ error }}</div>
    </main>
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  background: #0f0f1a;
  color: #e0e0e0;
}

.left-col {
  width: 320px;
  min-width: 260px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #222;
  overflow-y: auto;
}

.star-section {
  flex-shrink: 0;
  padding: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #13132a;
  overflow: hidden;
}

.right-col {
  flex: 1;
  position: relative;
  padding: 16px;
  display: flex;
  flex-direction: column;
}

.status-badge {
  position: absolute;
  top: 24px;
  right: 24px;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}
.loading {
  background: #1e3a5f;
  color: #93c5fd;
}
.error {
  background: #5f1e1e;
  color: #fca5a5;
}
</style>
