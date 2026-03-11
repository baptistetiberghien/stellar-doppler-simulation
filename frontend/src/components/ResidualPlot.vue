<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from "vue";
import type { SimulationResult } from "../types/simulation";

const props = defineProps<{
  result: SimulationResult | null;
  refSpectrum: SimulationResult | null;
}>();

const container = ref<HTMLDivElement | null>(null);
const canvas = ref<HTMLCanvasElement | null>(null);
const width = ref(600);
const height = ref(200);

const PAD = { top: 20, right: 16, bottom: 40, left: 54 };

function drawPlot() {
  const ctx = canvas.value?.getContext("2d");
  if (!ctx || !props.result || !props.refSpectrum) return;

  const wavelength = props.result.wavelength;
  const flux = props.result.flux;
  const refFlux = props.refSpectrum.flux;
  const n = wavelength.length;
  if (n < 2 || refFlux.length !== n) return;

  const xMin = wavelength[0]!;
  const xMax = wavelength[n - 1]!;

  // R(λ) = F(λ) - F_ref(λ)
  const residual: number[] = new Array(n);
  let rMin = Infinity;
  let rMax = -Infinity;
  for (let i = 0; i < n; i++) {
    const f = flux[i] ?? 0;
    const rf = refFlux[i] ?? 0;
    const r = f - rf;
    residual[i] = r;
    if (r < rMin) rMin = r;
    if (r > rMax) rMax = r;
  }

  // Symmetric y-range centred on 0 with a minimum extent
  const absMax = Math.max(Math.abs(rMin), Math.abs(rMax), 0.002);
  const yMin = -absMax * 1.15;
  const yMax = absMax * 1.15;

  const W = width.value;
  const H = height.value;
  const dpr = window.devicePixelRatio || 1;
  canvas.value!.width = W * dpr;
  canvas.value!.height = H * dpr;
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, W, H);

  const plotW = W - PAD.left - PAD.right;
  const plotH = H - PAD.top - PAD.bottom;

  function toX(v: number) {
    return PAD.left + ((v - xMin) / (xMax - xMin)) * plotW;
  }
  function toY(v: number) {
    return PAD.top + (1 - (v - yMin) / (yMax - yMin)) * plotH;
  }

  // Grid lines
  ctx.strokeStyle = "#2a2a3e";
  ctx.lineWidth = 0.5;
  const nTicksY = 4;
  for (let i = 0; i <= nTicksY; i++) {
    const v = yMin + (i / nTicksY) * (yMax - yMin);
    const py = toY(v);
    ctx.beginPath(); ctx.moveTo(PAD.left, py); ctx.lineTo(W - PAD.right, py); ctx.stroke();
  }
  const nTicksX = 6;
  for (let i = 0; i <= nTicksX; i++) {
    const v = xMin + (i / nTicksX) * (xMax - xMin);
    const px = toX(v);
    ctx.beginPath(); ctx.moveTo(px, PAD.top); ctx.lineTo(px, PAD.top + plotH); ctx.stroke();
  }

  // Zero reference line
  ctx.strokeStyle = "#555";
  ctx.lineWidth = 1;
  ctx.setLineDash([4, 4]);
  const y0 = toY(0);
  ctx.beginPath(); ctx.moveTo(PAD.left, y0); ctx.lineTo(W - PAD.right, y0); ctx.stroke();
  ctx.setLineDash([]);

  // Y=0 label
  ctx.fillStyle = "#666";
  ctx.font = "10px monospace";
  ctx.textAlign = "left";
  ctx.fillText("0", W - PAD.right + 4, y0 + 3);

  // X-axis labels
  ctx.fillStyle = "#aaa";
  ctx.font = "11px monospace";
  ctx.textAlign = "center";
  for (let i = 0; i <= nTicksX; i++) {
    const v = xMin + (i / nTicksX) * (xMax - xMin);
    ctx.fillText(v.toFixed(2), toX(v), PAD.top + plotH + 16);
  }

  // Y-axis labels
  ctx.textAlign = "right";
  for (let i = 0; i <= nTicksY; i++) {
    const v = yMin + (i / nTicksY) * (yMax - yMin);
    const label = v >= 0 ? `+${v.toFixed(4)}` : v.toFixed(4);
    ctx.fillText(label, PAD.left - 5, toY(v) + 4);
  }

  // Axis titles
  ctx.fillStyle = "#888";
  ctx.font = "11px sans-serif";
  ctx.textAlign = "center";
  ctx.fillText("Wavelength (nm)", PAD.left + plotW / 2, H - 4);
  ctx.save();
  ctx.translate(12, PAD.top + plotH / 2);
  ctx.rotate(-Math.PI / 2);
  ctx.fillText("Flux difference", 0, 0);
  ctx.restore();

  // Residual curve — fill the area between 0 and the curve
  ctx.beginPath();
  ctx.moveTo(toX(xMin), y0);
  for (let i = 0; i < n; i++) {
    const wl = wavelength[i] ?? xMin;
    ctx.lineTo(toX(wl), toY(residual[i]!));
  }
  ctx.lineTo(toX(xMax), y0);
  ctx.closePath();
  ctx.fillStyle = "rgba(239, 68, 68, 0.15)";
  ctx.fill();

  // Residual line
  ctx.beginPath();
  ctx.moveTo(toX(xMin), toY(residual[0]!));
  for (let i = 1; i < n; i++) {
    const wl = wavelength[i] ?? xMin;
    ctx.lineTo(toX(wl), toY(residual[i]!));
  }
  ctx.strokeStyle = "#ef4444";
  ctx.lineWidth = 1.5;
  ctx.stroke();
}

const resizeObserver = new ResizeObserver(() => {
  if (container.value) {
    width.value = container.value.clientWidth;
    height.value = container.value.clientHeight;
  }
});

onMounted(() => {
  if (container.value) {
    resizeObserver.observe(container.value);
    width.value = container.value.clientWidth;
    height.value = container.value.clientHeight;
  }
});

onUnmounted(() => resizeObserver.disconnect());

watch([() => props.result, () => props.refSpectrum, width, height], drawPlot, { flush: "post" });
</script>

<template>
  <div ref="container" class="residual-container">
    <canvas ref="canvas" :style="{ width: width + 'px', height: height + 'px' }" />
    <div v-if="!result || !refSpectrum" class="placeholder">
      Waiting for reference spectrum…
    </div>
  </div>
</template>

<style scoped>
.residual-container {
  width: 100%;
  flex: 1;
  min-height: 100px;
  position: relative;
  background: #1a1a2e;
  border-radius: 8px;
  overflow: hidden;
}
canvas {
  display: block;
}
.placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #555;
  font-size: 13px;
  font-style: italic;
}
</style>
