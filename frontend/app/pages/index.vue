<template>
  <div>
    <h1 class="text-2xl font-bold mb-1">Semantische Suche</h1>
    <p class="text-slate-500 text-sm mb-7">Suche in indexierten AASX-Dateien via Embeddings</p>

    <form class="flex flex-col gap-3 mb-8" @submit.prevent="search">
      <div class="flex gap-3">
        <input
          v-model="query"
          type="text"
          placeholder="z.B. Seriennummer, Hersteller, Spannung …"
          autofocus
          class="flex-1 bg-slate-800 border border-slate-700 text-slate-200 placeholder-slate-500 px-4 py-2.5 rounded-lg text-sm outline-none focus:border-blue-500 transition-colors"
        />
        <button
          type="submit"
          :disabled="loading || !query.trim()"
          class="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white px-5 py-2.5 rounded-lg text-sm font-medium transition-colors whitespace-nowrap"
        >
          {{ loading ? 'Suche …' : 'Suchen' }}
        </button>
      </div>

      <div class="flex items-center gap-6">
        <label class="flex items-center gap-2 text-slate-400 text-sm">
          Ergebnisse
          <input
            v-model.number="nResults"
            type="number"
            min="1"
            max="20"
            class="w-14 bg-slate-800 border border-slate-700 text-slate-200 px-2 py-1 rounded-md text-sm outline-none"
          />
        </label>
        <label class="flex items-center gap-2 text-slate-400 text-sm">
          Filter (asset_id)
          <input
            v-model="filterAsset"
            type="text"
            placeholder="optional"
            class="w-44 bg-slate-800 border border-slate-700 text-slate-200 placeholder-slate-500 px-2 py-1 rounded-md text-sm outline-none"
          />
        </label>
      </div>
    </form>

    <div v-if="error" class="bg-red-950 border border-red-900 text-red-300 px-4 py-3 rounded-lg text-sm mb-6">
      {{ error }}
    </div>

    <template v-if="results.length">
      <p class="text-slate-500 text-xs mb-3">{{ results.length }} Ergebnis{{ results.length !== 1 ? 'se' : '' }}</p>

      <article
        v-for="(r, i) in results"
        :key="i"
        class="bg-[#131922] border border-slate-800 rounded-xl px-5 py-4 mb-3"
      >
        <div class="flex justify-between items-center mb-2">
          <span class="text-blue-400 font-semibold text-xs">#{{ i + 1 }}</span>
          <span class="text-slate-500 text-xs">Distanz: {{ r.distance.toFixed(4) }}</span>
        </div>
        <p class="text-slate-300 text-sm leading-relaxed whitespace-pre-wrap mb-3">{{ r.text }}</p>
        <dl class="grid grid-cols-[max-content_1fr] gap-x-3 gap-y-0.5 text-xs">
          <template v-for="(val, key) in r.metadata" :key="key">
            <dt class="text-slate-500">{{ key }}</dt>
            <dd class="text-slate-400 break-all">{{ val ?? '—' }}</dd>
          </template>
        </dl>
      </article>
    </template>

    <div v-else-if="searched && !loading" class="text-center text-slate-600 py-12 text-sm">
      Keine Ergebnisse gefunden.
    </div>
  </div>
</template>

<script setup lang="ts">
interface QueryResult {
  text: string
  metadata: Record<string, string | null>
  distance: number
}

const query = ref('')
const nResults = ref(5)
const filterAsset = ref('')
const loading = ref(false)
const error = ref('')
const results = ref<QueryResult[]>([])
const searched = ref(false)

async function search() {
  if (!query.value.trim()) return
  loading.value = true
  error.value = ''
  searched.value = false

  try {
    const body: Record<string, unknown> = {
      query: query.value,
      n_results: nResults.value,
    }
    if (filterAsset.value.trim()) {
      body.filter = { asset_id: filterAsset.value.trim() }
    }

    const data = await $fetch<{ results: QueryResult[] }>('/api/query', {
      method: 'POST',
      body,
    })
    results.value = data.results
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : 'Fehler bei der Anfrage'
    results.value = []
  } finally {
    loading.value = false
    searched.value = true
  }
}
</script>
