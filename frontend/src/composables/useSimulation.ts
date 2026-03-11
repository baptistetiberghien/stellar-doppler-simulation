import { reactive, ref, watch, nextTick, type Ref } from "vue";
import {
  DEFAULT_PARAMS,
  type SimulationParams,
  type SimulationResult,
} from "../types/simulation";

const API_URL = import.meta.env.VITE_API_URL ?? "";

export function useSimulation() {
  const params = reactive<SimulationParams>({ ...DEFAULT_PARAMS });
  const result: Ref<SimulationResult | null> = ref(null);
  const refSpectrum: Ref<SimulationResult | null> = ref(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  let inFlight = false;
  let dirty = false;

  async function doFetch(): Promise<void> {
    if (inFlight) {
      dirty = true;
      return;
    }

    inFlight = true;
    dirty = false;
    loading.value = true;
    error.value = null;

    try {
      const res = await fetch(`${API_URL}/simulate`, {
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

  // Reference spectrum: same star, negligible spot.
  // Cached — only re-fetched when stellar params (other than lon) change.
  let refInFlight = false;
  let refDirty = false;
  let refParamsKey = "";

  async function fetchRef(): Promise<void> {
    const { spot_lon_deg: _, ...rest } = params;
    const key = JSON.stringify({ ...rest, spot_radius: 0.01 });
    if (key === refParamsKey && refSpectrum.value) return;

    if (refInFlight) {
      refDirty = true;
      return;
    }
    refInFlight = true;
    refDirty = false;

    try {
      const refParams = { ...params, spot_radius: 0.01 };
      const res = await fetch(`${API_URL}/simulate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(refParams),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      refSpectrum.value = await res.json();
      refParamsKey = key;
    } catch {
      // ignore — residual plot will simply stay blank
    } finally {
      refInFlight = false;
    }
    if (refDirty) fetchRef();
  }

  watch(
    () => JSON.stringify(params),
    async () => {
      if (inFlight) {
        dirty = true;
      } else {
        doFetch();
      }
      // Always ensure refSpectrum exists
      await nextTick();
      fetchRef();
    },
  );

  return { params, result, refSpectrum, loading, error, fetchSimulation: doFetch, fetchRef };
}
