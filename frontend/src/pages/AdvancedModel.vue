<script setup lang="ts">
import { onMounted, ref } from "vue";
import StarView from "../components/StarView.vue";
import SpectrumPlot from "../components/SpectrumPlot.vue";
import ResidualPlot from "../components/ResidualPlot.vue";
import AdvancedControlsPanel from "../components/AdvancedControlsPanel.vue";
import { useAdvancedSimulation } from "../composables/useAdvancedSimulation";
import type { AdvancedSimulationParams } from "../types/simulation";

const { params, result, refSpectrum, loading, error, fetchSimulation } = useAdvancedSimulation();

function onParamUpdate(key: keyof AdvancedSimulationParams, value: number) {
  (params as Record<string, number>)[key] = value;
}

const showInfo = ref(false);

onMounted(fetchSimulation);
</script>

<template>
  <div class="page-layout">
    <aside class="left-col">
      <div class="star-section">
        <StarView :params="params" :result="result" />
      </div>
      <AdvancedControlsPanel :params="params" @update:params="onParamUpdate" />
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

      <!-- Info toggle -->
      <button class="info-toggle" @click="showInfo = !showInfo">
        {{ showInfo ? '✕ Hide model info' : 'ℹ Model explanation' }}
      </button>

      <div v-if="showInfo" class="info-panel">
        <h4>Advanced model — spot line depth</h4>

        <section>
          <h5>A. Simple model (other page)</h5>
          <p>The spot acts as a <strong>dark mask</strong>: it removes all flux
            from the covered pixels. The spectral line depth is
            identical everywhere on the surface.</p>
        </section>

        <section>
          <h5>B. This model</h5>
          <p>The spot has <strong>two independent effects</strong>:</p>
          <ul>
            <li><strong>Photometric contrast</strong> — the spot emits a fraction
              <code>spot_contrast</code> of the local photospheric continuum.
              <br/>(0 = totally dark, 1 = same brightness, &gt;1 = facular brightening)
            </li>
            <li><strong>Spectral line depth</strong> — the spot produces a local
              spectral line with depth <code>spot_line_depth</code>, which can
              differ from the photospheric <code>line_depth</code>.
            </li>
          </ul>
        </section>

        <section>
          <h5>C. Mathematical formulation</h5>
          <div class="math-block">
            <p><em>Photosphere pixel:</em></p>
            <code>I_phot(λ) = C(μ) × [1 − line_depth × G(λ − λ₀ − Δλ)]</code>
            <p><em>Spot pixel:</em></p>
            <code>I_spot(λ) = spot_contrast × C(μ) × [1 − spot_line_depth × G(λ − λ₀ − Δλ)]</code>
            <p>where C(μ) = limb-darkening weight and G is the Gaussian kernel.</p>
          </div>
        </section>

        <section>
          <h5>D. Physical motivation</h5>
          <p>Stellar spots are regions with different <strong>temperature</strong>
            and <strong>magnetic field</strong>. This affects both the continuum
            brightness (photometric) and the line formation conditions (spectral).
            A cooler spot may have <em>deeper</em> lines (higher opacity) or
            <em>shallower</em> lines (different ionisation balance), depending
            on the species. Separating these two effects allows realistic
            modelling of stellar activity signatures.</p>
        </section>
      </div>

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
  width: 340px;
  min-width: 280px;
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
  overflow-y: auto;
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

.info-toggle {
  align-self: flex-start;
  padding: 6px 14px;
  font-size: 12px;
  font-weight: 600;
  background: #1a2540;
  color: #6ea8fe;
  border: 1px solid #2563eb44;
  border-radius: 5px;
  cursor: pointer;
  transition: background 0.15s;
  flex-shrink: 0;
}
.info-toggle:hover { background: #1e3050; }

.info-panel {
  background: #111827;
  border: 1px solid #1f2937;
  border-radius: 8px;
  padding: 16px 20px;
  font-size: 13px;
  line-height: 1.6;
  color: #d1d5db;
  flex-shrink: 0;
}
.info-panel h4 { margin: 0 0 12px; font-size: 15px; color: #93c5fd; }
.info-panel h5 { margin: 12px 0 4px; font-size: 13px; color: #6ea8fe; }
.info-panel p { margin: 4px 0; }
.info-panel ul { margin: 4px 0 4px 18px; padding: 0; }
.info-panel li { margin-bottom: 6px; }
.info-panel code {
  background: #1a2540;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 12px;
  color: #a5d8ff;
}
.math-block {
  background: #0d1117;
  border-radius: 6px;
  padding: 10px 14px;
  margin: 6px 0;
}
.math-block code {
  display: block;
  margin: 4px 0;
  background: none;
  padding: 0;
  font-size: 12px;
  color: #7dd3fc;
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
