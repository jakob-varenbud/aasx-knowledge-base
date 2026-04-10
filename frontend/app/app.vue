<template>
  <div class="min-h-screen bg-[#0f1117] text-slate-200 flex flex-col font-sans">
    <header class="bg-[#0d1118] border-b border-slate-800">
      <nav class="max-w-4xl mx-auto h-14 px-6 flex items-center gap-8">
        <NuxtLink to="/" class="text-blue-400 font-semibold text-sm whitespace-nowrap hover:text-blue-300 transition-colors">
          AASX Knowledge Base
        </NuxtLink>

        <div class="flex gap-2 flex-1">
          <NuxtLink
            to="/"
            class="text-slate-400 hover:text-slate-200 transition-colors text-sm px-2 py-1 rounded"
            active-class="text-slate-200"
          >
            Suche
          </NuxtLink>
          <NuxtLink
            to="/upload"
            class="text-slate-400 hover:text-slate-200 transition-colors text-sm px-2 py-1 rounded"
            active-class="text-slate-200"
          >
            Indexieren
          </NuxtLink>
          <NuxtLink
            to="/chat"
            class="text-slate-400 hover:text-slate-200 transition-colors text-sm px-2 py-1 rounded"
            active-class="text-slate-200"
          >
            Chat
          </NuxtLink>
        </div>

        <div class="flex items-center gap-1.5 text-xs" :class="healthClass">
          <span class="w-2 h-2 rounded-full" :class="dotClass" />
          <span>{{ healthLabel }}</span>
        </div>
      </nav>
    </header>

    <main class="flex-1 max-w-4xl mx-auto w-full px-6 py-8">
      <NuxtPage />
    </main>
  </div>
</template>

<script setup lang="ts">
const { data: health, refresh } = await useFetch<{ status: string; chunks: number }>('/api/health', {
  default: () => ({ status: 'unknown', chunks: 0 }),
})

const healthClass = computed(() => {
  if (health.value?.status === 'ok') return 'text-green-300'
  if (health.value?.status === 'unknown') return 'text-slate-500'
  return 'text-red-300'
})

const dotClass = computed(() => {
  if (health.value?.status === 'ok') return 'bg-green-500'
  if (health.value?.status === 'unknown') return 'bg-slate-500'
  return 'bg-red-500'
})

const healthLabel = computed(() => {
  if (health.value?.status === 'ok') return `${health.value.chunks} Chunks`
  return 'Offline'
})

onMounted(() => {
  setInterval(() => refresh(), 30_000)
})
</script>
