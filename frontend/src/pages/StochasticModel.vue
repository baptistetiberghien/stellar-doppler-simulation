<script setup lang="ts">
import { onMounted, ref } from "vue";
import MultiSpotStarView from "../components/MultiSpotStarView.vue";
import SpectrumPlot from "../components/SpectrumPlot.vue";
import ResidualPlot from "../components/ResidualPlot.vue";
import MultiSpotControlsPanel from "../components/MultiSpotControlsPanel.vue";
import { useMultiSpotSimulation } from "../composables/useMultiSpotSimulation";
import type { MultiSpotParams } from "../types/simulation";

const { params, result, refSpectrum, loading, error, fetchSimulation } =
  useMultiSpotSimulation();

function onParamUpdate(key: keyof MultiSpotParams, value: number) {
  (params as Record<string, number>)[key] = value;
}

function onRegenerate() {
  params.seed = params.seed + 1;
}

// Adapt MultiSpotResult → SimulationResult shape for SpectrumPlot / ResidualPlot
import { computed } from "vue";
import type { SimulationResult } from "../types/simulation";

const spectrumResult = computed<SimulationResult | null>(() => {
  if (!result.value) return null;
  return {
    wavelength: result.value.wavelength,
    flux: result.value.flux,
    spot_x: null,
    spot_y: null,
    spot_visible: false,
  };
});

const spectrumRef = computed<SimulationResult | null>(() => {
  if (!refSpectrum.value) return null;
  return {
    wavelength: refSpectrum.value.wavelength,
    flux: refSpectrum.value.flux,
    spot_x: null,
    spot_y: null,
    spot_visible: false,
  };
});

const showInfo = ref(true);

onMounted(fetchSimulation);
</script>

<template>
  <div class="page-layout">
    <aside class="left-col">
      <div class="star-section">
        <MultiSpotStarView :params="params" :result="result" />
      </div>
      <MultiSpotControlsPanel
        :params="params"
        @update:params="onParamUpdate"
        @regenerate="onRegenerate"
      />
    </aside>

    <main class="right-col">
      <div class="section-label">Integrated spectrum</div>
      <div class="plot-area spectrum-area">
        <SpectrumPlot :result="spectrumResult" />
      </div>

      <div class="section-label">Spectral diagnostics — Residual spectrum</div>
      <div class="plot-area residual-area">
        <ResidualPlot :result="spectrumResult" :refSpectrum="spectrumRef" />
      </div>

      <!-- Explanation -->
      <button class="info-toggle" @click="showInfo = !showInfo">
        {{ showInfo ? '✕ Hide' : 'ℹ Stochastic model explanation' }}
      </button>

      <div v-if="showInfo" class="info-panel">
        <h4>Stochastic spot model</h4>
        <p>This version replaces a single manually placed spot with a
          <strong>random population of spots</strong> distributed over the
          stellar surface.</p>
        <p>The goal is to move from a purely illustrative single-spot model
          toward a more <strong>statistical description of stellar activity</strong>,
          which is closer in spirit to statistical Doppler imaging.</p>

        <h5>Spot generation</h5>
        <ul>
          <li><strong>Longitude</strong> — uniform in [0°, 360°)</li>
          <li><strong>Latitude</strong> — uniform on the sphere via
            <code>lat = arcsin(u)</code> with <code>u</code> uniform in [-1, 1],
            which avoids polar bias</li>
          <li><strong>Radius</strong> — uniform between min and max</li>
        </ul>
        <p>Each realization is fully determined by the <strong>random seed</strong>,
          ensuring reproducibility.</p>

        <h5>Why this matters</h5>
        <p>Real stars have dozens to hundreds of active regions. Their cumulative
          spectroscopic signature cannot be understood from a single spot.
          This page lets you explore how the <strong>integrated line profile
          and residual spectrum</strong> depend on the spot population statistics
          rather than on one specific configuration.</p>
      </div>

      <div v-if="loading" class="status-badge loading">Computing…</div>
      <div v-if="error" class="status-badge error">{{ error }}</div>
    </main>
  </div>
</template>

<style scoped>
.page-layout { display: flex; flex: 1; overflow: hidden; }
.left-col {
  width: 340px; min-width: 280px; flex-shrink: 0;
  display: flex; flex-direction: column;
  border-right: 1px solid #222; overflow-y: auto;
}
.star-section {
  flex-shrink: 0; padding: 12px;
  display: flex; align-items: center; justify-content: center;
  background: #13132a; overflow: hidden;
}
.right-col {
  flex: 1; position: relative;
  padding: 12px 16px;
  display: flex; flex-direction: column; gap: 4px;
  overflow-y: auto; min-width: 0;
}
.section-label {
  font-size: 11px; font-weight: 600; text-transform: uppercase;
  letter-spacing: 0.5px; color: #556; margin-top: 4px;
}
.plot-area { display: flex; flex-direction: column; min-height: 120px; }
.spectrum-area { flex: 3; }
.residual-area { flex: 2; }

.info-toggle {
  align-self: flex-start;
  padding: 6px 14px; font-size: 12px; font-weight: 600;
  background: #1a2540; color: #6ea8fe;
  border: 1px solid #2563eb44; border-radius: 5px;
  cursor: pointer; transition: background 0.15s; flex-shrink: 0;
}
.info-toggle:hover { background: #1e3050; }

.info-panel {
  background: #111827; border: 1px solid #1f2937;
  border-radius: 8px; padding: 16px 20px;
  font-size: 13px; line-height: 1.6; color: #d1d5db; flex-shrink: 0;
}
.info-panel h4 { margin: 0 0 10px; font-size: 15px; color: #93c5fd; }
.info-panel h5 { margin: 12px 0 4px; font-size: 13px; color: #6ea8fe; }
.info-panel p { margin: 4px 0; }
.info-panel ul { margin: 4px 0 4px 18px; padding: 0; }
.info-panel li { margin-bottom: 4px; }
.info-panel code {
  background: #1a2540; padding: 2px 6px; border-radius: 3px;
  font-size: 12px; color: #a5d8ff;
}

.status-badge {
  position: absolute; top: 20px; right: 20px;
  padding: 4px 12px; border-radius: 4px;
  font-size: 12px; font-weight: 600;
}
.loading { background: #1e3a5f; color: #93c5fd; }
.error   { background: #5f1e1e; color: #fca5a5; }
</style>
