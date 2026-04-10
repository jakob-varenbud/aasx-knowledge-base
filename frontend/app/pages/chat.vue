<template>
  <div class="flex flex-col h-[calc(100vh-7rem)]">
    <h1 class="text-2xl font-bold mb-1">Chat</h1>
    <p class="text-slate-500 text-sm mb-5">Stelle Fragen zu deinen indexierten AASX-Dateien</p>

    <!-- Nachrichtenverlauf -->
    <div ref="scrollContainer" class="flex-1 overflow-y-auto flex flex-col gap-4 mb-4 pr-1">
      <div v-if="messages.length === 0" class="text-center text-slate-600 py-16 text-sm">
        Stell eine Frage zu deinen AASX-Daten …
      </div>

      <template v-for="(msg, i) in messages" :key="i">
        <!-- User-Nachricht -->
        <div v-if="msg.role === 'user'" class="flex justify-end">
          <div class="bg-blue-600 text-white px-4 py-2.5 rounded-2xl rounded-br-sm text-sm max-w-[75%] leading-relaxed">
            {{ msg.content }}
          </div>
        </div>

        <!-- Assistent-Nachricht -->
        <div v-else class="flex flex-col gap-2 max-w-[85%]">
          <div class="bg-[#131922] border border-slate-800 text-slate-200 px-4 py-3 rounded-2xl rounded-bl-sm text-sm leading-relaxed whitespace-pre-wrap">
            {{ msg.content }}
          </div>

          <!-- Quellen -->
          <details v-if="msg.sources?.length" class="text-xs">
            <summary class="text-slate-500 cursor-pointer hover:text-slate-400 transition-colors select-none">
              {{ msg.sources.length }} Quellen anzeigen
            </summary>
            <div class="mt-2 flex flex-col gap-2">
              <div
                v-for="(src, j) in msg.sources"
                :key="j"
                class="bg-[#0d1118] border border-slate-800 px-3 py-2 rounded-lg text-slate-400 whitespace-pre-wrap"
              >
                {{ src }}
              </div>
            </div>
          </details>
        </div>
      </template>

      <!-- Lade-Indikator -->
      <div v-if="loading" class="flex gap-1.5 px-1">
        <span v-for="n in 3" :key="n" class="w-2 h-2 rounded-full bg-slate-600 animate-bounce" :style="{ animationDelay: `${(n - 1) * 0.15}s` }" />
      </div>
    </div>

    <!-- Fehler -->
    <div v-if="error" class="bg-red-950 border border-red-900 text-red-300 px-4 py-3 rounded-lg text-sm mb-3">
      {{ error }}
    </div>

    <!-- Eingabe -->
    <form class="flex gap-3" @submit.prevent="send">
      <input
        v-model="input"
        type="text"
        placeholder="Frage stellen …"
        :disabled="loading"
        autofocus
        class="flex-1 bg-slate-800 border border-slate-700 text-slate-200 placeholder-slate-500 px-4 py-2.5 rounded-lg text-sm outline-none focus:border-blue-500 transition-colors disabled:opacity-50"
        @keydown.enter.prevent="send"
      />
      <button
        type="submit"
        :disabled="loading || !input.trim()"
        class="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white px-5 py-2.5 rounded-lg text-sm font-medium transition-colors whitespace-nowrap"
      >
        Senden
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
interface Message {
  role: 'user' | 'assistant'
  content: string
  sources?: string[]
}

const input = ref('')
const loading = ref(false)
const error = ref('')
const messages = ref<Message[]>([])
const scrollContainer = ref<HTMLElement | null>(null)

async function send() {
  const text = input.value.trim()
  if (!text || loading.value) return

  input.value = ''
  error.value = ''
  messages.value.push({ role: 'user', content: text })
  await scrollToBottom()

  loading.value = true
  try {
    const data = await $fetch<{ answer: string; sources: string[] }>('/api/chat', {
      method: 'POST',
      body: { message: text, n_results: 5 },
    })
    messages.value.push({ role: 'assistant', content: data.answer, sources: data.sources })
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : 'Fehler bei der Anfrage'
  } finally {
    loading.value = false
    await scrollToBottom()
  }
}

async function scrollToBottom() {
  await nextTick()
  if (scrollContainer.value) {
    scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight
  }
}
</script>
