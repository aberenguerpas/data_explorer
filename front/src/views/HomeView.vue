<template>
  <main class="flex flex-col justify-center items-center h-screen">
    <div class="mb-4 text-center">
      <div class="flex justify-center">
        <a href="https://inferia.io"><img
          alt="InferIA logo"
          class="justify-center"
          src="@/assets/Inferia_negativo.png"
          width="200"
        /></a>
      </div>
        <span class="text-xs color-gray mb-8">Demo datos.gob.es - V1.0.3</span>
    </div>
    <SearchBar class="m-2 w-4/5" @keyup.enter="search"/>
  </main>
</template>

<script setup>
  import SearchBar from '@/components/SearchBar.vue';
  import { useRouter } from 'vue-router'
  import { useSearchStore } from '@/stores/search'
  
  const route = useRouter()
  const store = useSearchStore()

  const search = ()=>{
    route.push({
        name: 'results',
        query: {
          q: store.InputSearch
        },
      })
  }
</script>
