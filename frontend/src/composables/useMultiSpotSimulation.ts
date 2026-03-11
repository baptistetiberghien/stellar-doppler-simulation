import { reactive, ref, watch, type Ref } from "vue";
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
  let refKey = "";

  async function fetchRef(): Promise<void> {
    const { rotation_phase: _, ...rest } = params;
    const key = JSON.stringify(rest);
    if (key === refKey && refSpectrum.value) return;

    if (refInFlight) {
      refDirty = true;
      return;
    }

    refInFlight = true;
    refDirty = false;

    try {
      const payload = {
        ...params,
        rotation_phase: 0,
        n_spots: 1,
        min_spot_radius: 0.02,
        max_spot_radius: 0.05,
      };

      console.log("[fetchRef] API_URL", API_URL);
      console.log("[fetchRef] payload", payload);

      const res = await fetch(`${API_URL}/simulate-multispot`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      console.log("[fetchRef] status", res.status);

      const text = await res.text();
      console.log("[fetchRef] raw response", text);

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${text}`);
      }

      const data = JSON.parse(text);
      console.log("[fetchRef] parsed data", data);

      refSpectrum.value = data;
      refKey = key;

      console.log("[fetchRef] refSpectrum.value", refSpectrum.value);
    } catch (e) {
      console.error("[fetchRef] error", e);
    } finally {
      refInFlight = false;
    }

    if (refDirty) fetchRef();
  }

  watch(
    () => JSON.stringify(params),
    () => {
      if (inFlight) {
        dirty = true;
      } else {
        doFetch();
      }
    },
  );

  watch(
    () => {
      const { rotation_phase: _, ...rest } = params;
      return JSON.stringify(rest);
    },
    () => fetchRef(),
    { immediate: true },
  );

  return {
    params,
    result,
    refSpectrum,
    loading,
    error,
    fetchSimulation: doFetch,
  };
}
