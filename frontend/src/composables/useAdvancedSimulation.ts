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

  return { params, result, loading, error, fetchSimulation: doFetch };
}
