import { reactive, ref, watch, type Ref } from "vue";
import {
  DEFAULT_PARAMS,
  type SimulationParams,
  type SimulationResult,
} from "../types/simulation";

const API_URL = import.meta.env.VITE_API_URL ?? "";
const MIN_INTERVAL_MS = 120;

export function useSimulation() {
  const params = reactive<SimulationParams>({ ...DEFAULT_PARAMS });
  const result: Ref<SimulationResult | null> = ref(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  let controller: AbortController | null = null;
  let lastSentAt = 0;
  let pendingTimer: ReturnType<typeof setTimeout> | null = null;
  let dirty = false;

  async function doFetch(): Promise<void> {
    controller?.abort();
    controller = new AbortController();
    lastSentAt = Date.now();
    dirty = false;

    loading.value = true;
    error.value = null;

    const snapshot = JSON.stringify({ ...params });

    try {
      const res = await fetch(`${API_URL}/simulate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: snapshot,
        signal: controller.signal,
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      result.value = await res.json();
    } catch (e: unknown) {
      if (e instanceof DOMException && e.name === "AbortError") return;
      error.value = e instanceof Error ? e.message : "Unknown error";
    } finally {
      loading.value = false;
    }

    // If params changed while we were waiting, fire again
    if (dirty) scheduleNext();
  }

  function scheduleNext(): void {
    if (pendingTimer) return;
    const elapsed = Date.now() - lastSentAt;
    const delay = Math.max(0, MIN_INTERVAL_MS - elapsed);
    pendingTimer = setTimeout(() => {
      pendingTimer = null;
      doFetch();
    }, delay);
  }

  function requestSimulation(): void {
    dirty = true;
    const elapsed = Date.now() - lastSentAt;
    if (elapsed >= MIN_INTERVAL_MS && !pendingTimer) {
      doFetch();
    } else {
      scheduleNext();
    }
  }

  watch(
    () => JSON.stringify(params),
    () => requestSimulation(),
  );

  return { params, result, loading, error, fetchSimulation: doFetch };
}
