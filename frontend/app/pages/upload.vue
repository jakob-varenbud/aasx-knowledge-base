<template>
  <div>
    <h1 class="text-2xl font-bold mb-1">AASX-Datei indexieren</h1>
    <p class="text-slate-500 text-sm mb-7">Lade eine .aasx-Datei hoch, um sie in die Knowledge Base einzufügen</p>

    <div
      class="border-2 border-dashed rounded-xl p-10 text-center transition-colors mb-5"
      :class="dragging
        ? 'border-blue-500 bg-blue-500/5'
        : file
          ? 'border-green-500 bg-green-500/5'
          : 'border-slate-700'"
      @dragover.prevent="dragging = true"
      @dragleave.prevent="dragging = false"
      @drop.prevent="onDrop"
    >
      <input
        id="file-input"
        ref="fileInput"
        type="file"
        accept=".aasx"
        class="hidden"
        @change="onFileChange"
      />
      <label for="file-input" class="flex flex-col items-center gap-2 cursor-pointer">
        <template v-if="file">
          <span class="text-4xl">📄</span>
          <span class="text-slate-200 font-semibold text-sm">{{ file.name }}</span>
          <span class="text-slate-500 text-xs">{{ (file.size / 1024).toFixed(1) }} KB</span>
        </template>
        <template v-else>
          <span class="text-3xl text-slate-600">⬆</span>
          <span class="text-slate-400 text-sm">Datei hier ablegen oder <u>auswählen</u></span>
          <span class="text-slate-600 text-xs">.aasx</span>
        </template>
      </label>
    </div>

    <div class="flex gap-3 mb-5">
      <button
        :disabled="!file || loading"
        class="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white px-5 py-2.5 rounded-lg text-sm font-medium transition-colors"
        @click="upload"
      >
        {{ loading ? 'Wird indexiert …' : 'Indexieren' }}
      </button>
      <button
        v-if="file"
        :disabled="loading"
        class="border border-slate-700 hover:border-slate-400 disabled:opacity-50 disabled:cursor-not-allowed text-slate-400 px-4 py-2.5 rounded-lg text-sm transition-colors"
        @click="reset"
      >
        Zurücksetzen
      </button>
    </div>

    <div v-if="error" class="bg-red-950 border border-red-900 text-red-300 px-4 py-3 rounded-lg text-sm mb-4">
      {{ error }}
    </div>

    <div v-if="result" class="bg-green-950 border border-green-900 text-green-300 px-4 py-3 rounded-lg text-sm mb-4">
      <strong>Fertig!</strong> {{ result.chunks_indexed }} Chunks wurden indexiert.
    </div>

    <div v-if="loading" class="flex items-center gap-3 text-slate-500 text-sm">
      <span class="w-4 h-4 border-2 border-slate-700 border-t-blue-400 rounded-full animate-spin" />
      Datei wird hochgeladen und verarbeitet …
    </div>
  </div>
</template>

<script setup lang="ts">
const fileInput = ref<HTMLInputElement | null>(null)
const file = ref<File | null>(null)
const dragging = ref(false)
const loading = ref(false)
const error = ref('')
const result = ref<{ chunks_indexed: number } | null>(null)

function onFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  if (input.files?.[0]) setFile(input.files[0])
}

function onDrop(e: DragEvent) {
  dragging.value = false
  const dropped = e.dataTransfer?.files?.[0]
  if (dropped) setFile(dropped)
}

function setFile(f: File) {
  if (!f.name.endsWith('.aasx')) {
    error.value = 'Nur .aasx-Dateien sind erlaubt.'
    return
  }
  error.value = ''
  result.value = null
  file.value = f
}

function reset() {
  file.value = null
  error.value = ''
  result.value = null
  if (fileInput.value) fileInput.value.value = ''
}

async function upload() {
  if (!file.value) return
  loading.value = true
  error.value = ''
  result.value = null

  try {
    const form = new FormData()
    form.append('file', file.value)

    const data = await $fetch<{ chunks_indexed: number }>('/api/index', {
      method: 'POST',
      body: form,
    })
    result.value = data
    file.value = null
    if (fileInput.value) fileInput.value.value = ''
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : 'Upload fehlgeschlagen'
  } finally {
    loading.value = false
  }
}
</script>
