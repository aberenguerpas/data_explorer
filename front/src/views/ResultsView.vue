<template>
  <div class="max-w-6xl mx-auto m-20">   
        <div class="flex flex-col justify-start">
            <div class="flex flex-col items-center md:items-start">
                  <a href="https://inferia.io"><img
                  alt="InferIA logo"
                  class="cursor-pointer py-4"
                  src="@/assets/Inferia_negativo.png"
                  width="100"
                  /></a>

              <SearchBar class="mb-4 w-full" @keyup.enter="search"/>
            </div>
            <hr>
            <span class="m-4 text-center md:text-left" v-if="total > 0">Resultados: {{ total }}</span>

            <div v-if="loading==false" class="mt-4">
                <div v-if="total == 0" class="bg-white h-full rounded-2xl p-4">
                  <div v-html="intro" class="text-left text-xl p-4 text-gray-500"></div>
                </div>
                <div v-else>
                  <div v-if="type == 'keywords'" v-for="i in results">
                    <ResultItem :data="i" class="my-3"/>
                  </div>
                  
                  <div class="bg-white h-full rounded-2xl p-6 pt-10 md:my-4" v-else >
                    <p class="italic text-lg mx-4">{{intro}}</p>
                    <div class="p-4">
                      <div v-for="i in results">
                        <ComplexResultItem v-if="i['resultados']['total']['value'] > 0" :data="i"/>
                      </div>
                    </div>
                  </div>

                  <div v-if="additional!=''" class="bg-white h-full rounded-2xl">
                    <div v-html="additional" class="text-left text-lg p-10 text-stone-600 italic"></div>
                  </div>
              </div>
          </div>
          <div v-else class="m-12">
              <div class=" mx-auto w-16 h-16 border-4 border-dashed rounded-full animate-spin border-blue-300"></div>
          </div>
        </div>
      </div>
</template>

<style>
@media (min-width: 1024px) {
  .about {
    min-height: 100vh;
    display: flex;
    align-items: center;
  }
}
</style>

<script setup>
  import ResultItem from '../components/ResultItem.vue';
  import { useRoute } from 'vue-router';
  import { useRouter } from 'vue-router';
  import SearchBar from '@/components/SearchBar.vue';
  import {ref} from 'vue';
  import { onMounted } from 'vue';
  import { useSearchStore } from '@/stores/search'
  import ComplexResultItem from '@/components/ComplexResultItem.vue'

  const store = useSearchStore()
  const keyword = ref('')
  const results = ref()
  const total = ref(0)
  const intro = ref('')
  const additional = ref('')
  const route = useRoute()
  const router = useRouter()
  const type = ref('')
  const loading = ref(false)

  const getResults = async ()=>{
    
      keyword.value = route.query.q
      store.InputSearch = route.query.q
      loading.value = true
      const res = await fetch('https://demo.inferia.io/api/search?q='+keyword.value)
      const jsonResponse = await res.json()
    
      type.value = jsonResponse['type']
      if(jsonResponse['type'] == 'keywords'){
        total.value = jsonResponse['total']['value']
        results.value = jsonResponse['hits']
        intro.value = jsonResponse['intro']
        additional.value = jsonResponse['additional']
        loading.value = false
      }else{
        intro.value = jsonResponse['intro']
        additional.value = jsonResponse['additional']
        results.value = jsonResponse['hits']
        total.value = jsonResponse['total']
        loading.value = false
      }
  }

  const search = async ()=>{
    await router.push({
        name: 'results',
        query: {
          q: store.InputSearch
        },
      })
    await getResults()
  }

  onMounted(() => getResults())
</script>