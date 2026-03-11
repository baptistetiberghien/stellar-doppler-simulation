import { reactive, ref, watch, type Ref } from "vue";
import {
  DEFAULT_ADVANCED_PARAMS,
  type AdvancedSimulationParams,
  type SimulationResult,
} from "../types/simulation";

const API_URL = import.meta.env.VITE_API_URL ?? "";

export function useAdvancedSimulation() {
  const params = reactive<AdvancedSimulationParams>({ ...DEFAULT_ADVANCED_PARAMS });
  const result: Ref<SimulationResult | null> = ref(null);
  const refSpectrum: Ref<SimulationResult | null> = ref(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  let inFlight = false;
  let dirty = false;

  async function doFetch(): Promise<void> {
    if (inFlight) { dirty = true; return; }
    inFlight = true;
    dirty = false;
    loading.value = true;
    error.value = null;

    try {
      const res = await fetch(`${API_URL}/simulate-advanced`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...params }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      result.value = await res.json();
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : "Unknown error";
    } finally {
      inFlight = false;
      loading.value = false;
    }
    if (dirty) doFetch();
  }

  let refInFlight = false;
  let refDirty = false;
  let refKey = "";

  async function fetchRef(): Promise<void> {
    const { spot_lon_deg: _, ...rest } = params;
    const key = JSON.stringify(rest);
    if (key === refKey && refSpectrum.value) return;

    if (refInFlight) { refDirty = true; return; }
    refInFlight = true;
    refDirty = false;

    try {
      const res = await fetch(`${API_URL}/simulate-advanced`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...params, spot_radius: 0.01 }),
      });
      if (!res.ok) return;
      refSpectrum.value = await res.json();
      refKey = key;
    } catch { /* ignore */ } finally {
      refInFlight = false;
    }
    if (refDirty) fetchRef();
  }

  watch(() => JSON.stringify(params), () => {
    if (inFlight) { dirty = true; } else { doFetch(); }
  });

  watch(
    () => { const { spot_lon_deg: _, ...rest } = params; return JSON.stringify(rest); },
    () => fetchRef(),
    { immediate: true },
  );

  return { params, result, refSpectrum, loading, error, fetchSimulation: doFetch };
}
