import { reactive, ref, watch, nextTick, type Ref } from "vue";
import {
  DEFAULT_MULTISPOT_PARAMS,
  type MultiSpotParams,
  type MultiSpotResult,
} from "../types/simulation";

const API_URL = import.meta.env.VITE_API_URL ?? "";

export function useMultiSpotSimulation() {
  const params = reactive<MultiSpotParams>({ ...DEFAULT_MULTISPOT_PARAMS });
  const result: Ref<MultiSpotResult | null> = ref(null);
  const refSpectrum: Ref<MultiSpotResult | null> = ref(null);
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
      const res = await fetch(`${API_URL}/simulate-multispot`, {
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
  let refParamsKey = "";

  async function fetchRef(): Promise<void> {
    const { rotation_phase: _, ...rest } = params;
    const key = JSON.stringify({ ...rest, n_spots: 1, min_spot_radius: 0.02, max_spot_radius: 0.02 });
    if (key === refParamsKey && refSpectrum.value) return;

    if (refInFlight) {
      refDirty = true;
      return;
    }
    refInFlight = true;
    refDirty = false;

    try {
      const refParams = { ...params, n_spots: 1, min_spot_radius: 0.02, max_spot_radius: 0.02 };
      const res = await fetch(`${API_URL}/simulate-multispot`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(refParams),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      refSpectrum.value = await res.json();
      refParamsKey = key;
    } catch {
      // ignore
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
      await nextTick();
      fetchRef();
    },
  );

  return { params, result, refSpectrum, loading, error, fetchSimulation: doFetch, fetchRef };
}
