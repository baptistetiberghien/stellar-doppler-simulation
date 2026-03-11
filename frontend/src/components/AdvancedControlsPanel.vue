<script setup lang="ts">
import { ref, onUnmounted } from "vue";
import type { AdvancedSimulationParams } from "../types/simulation";

const props = defineProps<{
  params: AdvancedSimulationParams;
}>();

const emit = defineEmits<{
  (e: "update:params", key: keyof AdvancedSimulationParams, value: number): void;
}>();

function set(key: keyof AdvancedSimulationParams, raw: string) {
  emit("update:params", key, parseFloat(raw));
}

// --- Animation ---
const playing = ref(false);
let animFrame = 0;
let lastTime = 0;
const DEGREES_PER_SECOND = 30;

function tick(timestamp: number) {
  if (!playing.value) return;
  if (lastTime === 0) lastTime = timestamp;
  const dt = Math.min((timestamp - lastTime) / 1000, 0.1);
  lastTime = timestamp;

  let lon = props.params.spot_lon_deg + DEGREES_PER_SECOND * dt;
  if (lon > 360) lon -= 360;
  if (lon < -180) lon += 360;
  emit("update:params", "spot_lon_deg", Math.round(lon * 100) / 100);

  animFrame = requestAnimationFrame(tick);
}

function togglePlay() {
  playing.value = !playing.value;
  if (playing.value) {
    lastTime = 0;
    animFrame = requestAnimationFrame(tick);
  } else {
    cancelAnimationFrame(animFrame);
  }
}

onUnmounted(() => cancelAnimationFrame(animFrame));

interface SliderDef {
  key: keyof AdvancedSimulationParams;
  label: string;
  min: number;
  max: number;
  step: number;
  unit?: string;
}

const sliders: SliderDef[] = [
  { key: "inclination_deg", label: "Inclination", min: 0, max: 90, step: 1, unit: "°" },
  { key: "veq", label: "v_eq", min: 0.5, max: 80, step: 0.5, unit: "km/s" },
  { key: "spot_lat_deg", label: "Spot latitude", min: -90, max: 90, step: 1, unit: "°" },
  { key: "spot_lon_deg", label: "Spot longitude", min: -180, max: 360, step: 1, unit: "°" },
  { key: "spot_radius", label: "Spot radius", min: 0.02, max: 0.45, step: 0.01 },
  { key: "line_sigma", label: "Line width σ", min: 0.001, max: 0.04, step: 0.001, unit: "nm" },
  { key: "line_depth", label: "Photosphere line depth", min: 0.05, max: 0.95, step: 0.01 },
  { key: "spot_line_depth", label: "Spot line depth", min: 0.0, max: 1.0, step: 0.01 },
  { key: "spot_contrast", label: "Spot contrast", min: 0.0, max: 1.5, step: 0.01 },
];
</script>

<template>
  <div class="controls-panel">
    <h3>Parameters</h3>

    <div class="anim-row">
      <button class="play-btn" :class="{ active: playing }" @click="togglePlay">
        {{ playing ? "⏸ Pause" : "▶ Play" }}
      </button>
    </div>

    <div v-for="s in sliders" :key="s.key" class="slider-group"
         :class="{ highlight: s.key === 'spot_line_depth' || s.key === 'spot_contrast' }">
      <label>
        <span class="slider-label">{{ s.label }}</span>
        <span class="slider-value">{{ (params[s.key] as number).toFixed(s.step < 0.01 ? 3 : s.step < 1 ? 2 : 0) }}{{ s.unit ?? '' }}</span>
      </label>
      <input
        type="range"
        :min="s.min"
        :max="s.max"
        :step="s.step"
        :value="params[s.key]"
        @input="set(s.key, ($event.target as HTMLInputElement).value)"
      />
    </div>
  </div>
</template>

<style scoped>
.controls-panel {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

h3 {
  margin: 0 0 4px;
  font-size: 16px;
  color: #ccc;
}

.anim-row {
  display: flex;
  gap: 8px;
  margin-bottom: 6px;
}

.play-btn {
  flex: 1;
  padding: 10px 0;
  border: none;
  border-radius: 6px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  background: #2563eb;
  color: #fff;
  transition: background 0.15s;
}
.play-btn:hover { background: #1d4ed8; }
.play-btn.active { background: #dc2626; }
.play-btn.active:hover { background: #b91c1c; }

.slider-group {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.slider-group.highlight {
  background: #1a2540;
  margin: 0 -8px;
  padding: 6px 8px;
  border-radius: 6px;
  border-left: 3px solid #2563eb;
}

label {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #aaa;
}

.slider-label { font-weight: 500; }
.slider-value { font-family: monospace; color: #6ea8fe; }

input[type="range"] {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  height: 6px;
  border-radius: 3px;
  background: #333;
  outline: none;
}
input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #2563eb;
  cursor: pointer;
  border: 2px solid #1a1a2e;
}
input[type="range"]::-moz-range-thumb {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #2563eb;
  cursor: pointer;
  border: 2px solid #1a1a2e;
}
</style>
