<script setup lang="ts">
import { onMounted } from "vue";
import StarView from "../components/StarView.vue";
import SpectrumPlot from "../components/SpectrumPlot.vue";
import ResidualPlot from "../components/ResidualPlot.vue";
import ControlsPanel from "../components/ControlsPanel.vue";
import { useSimulation } from "../composables/useSimulation";
import type { SimulationParams } from "../types/simulation";

const { params, result, refSpectrum, loading, error, fetchSimulation } = useSimulation();

function onParamUpdate(key: keyof SimulationParams, value: number) {
  (params as Record<string, number>)[key] = value;
}

onMounted(fetchSimulation);
</script>

<template>
  <div class="page-layout">
    <aside class="left-col">
      <div class="star-section">
        <StarView :params="params" :result="result" />
      </div>
      <ControlsPanel :params="params" @update:params="onParamUpdate" />
    </aside>

    <main class="right-col">
      <div class="section-label">Integrated spectrum</div>
      <div class="plot-area spectrum-area">
        <SpectrumPlot :result="result" />
      </div>

      <div class="section-label">Spectral diagnostics — Residual spectrum</div>
      <div class="plot-area residual-area">
        <ResidualPlot :result="result" :refSpectrum="refSpectrum" />
      </div>
      <p class="residual-caption">
        Difference between the current spectrum and a reference without spot.
        Highlights the spectral perturbation as the spot crosses the visible disk.
      </p>

      <div v-if="loading" class="status-badge loading">Computing…</div>
      <div v-if="error" class="status-badge error">{{ error }}</div>
    </main>
  </div>
</template>

<style scoped>
.page-layout {
  display: flex;
  flex: 1;
  overflow: hidden;
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
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.section-label {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #556;
  margin-top: 4px;
}

.plot-area {
  display: flex;
  flex-direction: column;
  min-height: 120px;
}
.spectrum-area { flex: 3; }
.residual-area { flex: 2; }

.residual-caption {
  font-size: 11px;
  color: #556;
  line-height: 1.4;
  margin: 0;
  flex-shrink: 0;
}

.status-badge {
  position: absolute;
  top: 20px;
  right: 20px;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}
.loading { background: #1e3a5f; color: #93c5fd; }
.error   { background: #5f1e1e; color: #fca5a5; }
</style>
