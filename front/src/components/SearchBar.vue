<script setup>
import { useSearchStore } from '@/stores/search'
import {storeToRefs} from 'pinia'
import { useRouter } from 'vue-router'

const store = useSearchStore()
const { InputSearch } = storeToRefs(store);

const route = useRouter()


let curr_path = route.currentRoute.value;

function clickSuggestion(text){
  InputSearch.value = text

  route.push({
        name: 'results',
        query: {
          q: store.InputSearch
        },
      })
}

</script>

<template>

<div class="p-4 mx-auto">
        <!--Suggestion-->
      <div v-if="curr_path.path!='/results'" class="flex flex-wrap mb-4">
        <div class="p-4 bg-white m-1 rounded-lg hover:shadow-md hover:shadow-slate-200 w-full md:w-2/5 grow cursor-pointer border"
        @click='clickSuggestion("Quiero estudiar los niveles de agua de los embalses de Barcelona")'>
        Quiero estudiar los niveles de agua de los embalses de Barcelona
        </div>
        <div class="p-4 bg-white m-1 rounded-lg hover:shadow-md hover:shadow-slate-200 w-full md:w-2/5 grow cursor-pointer border"
        @click='clickSuggestion("Puntos de recarga de coches eléctricos")'>
          Puntos de recarga de coches eléctricos
        </div>
        <div class="p-4 bg-white m-1 rounded-lg hover:shadow-md hover:shadow-slate-200 w-full md:w-2/5 grow cursor-pointer border"
        @click='clickSuggestion("Calidad del aire en Madrid")'>
        Calidad del aire en Madrid
        </div>
        <div class="p-4 bg-white m-1 rounded-lg hover:shadow-md hover:shadow-slate-200 w-full md:w-2/5 grow cursor-pointer border"
        @click='clickSuggestion("Salarios del sector TIC")'>
        Salarios del sector TIC
        </div>
      </div>
      <div
        class="relative flex items-center h-12 rounded-lg focus-within:shadow-lg bg-white overflow-hidden"
      >
        <div class="grid place-items-center h-full w-12 text-gray-300">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        </div>

        <input
          class="peer h-full w-full outline-none text-sm text-gray-700 pr-2"
          type="text"
          id="search"
          placeholder="Buscar datos..."
          autocomplete="off"
          v-model="InputSearch"
        />
      </div>

    </div>
</template>
