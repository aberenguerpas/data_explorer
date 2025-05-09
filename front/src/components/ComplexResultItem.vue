<template>
    <div>
        <!-- Card header -->
        <div class="justify-between items-center">
            <p class="font-extrabold text-gray-600 text-md capitalize">{{ props['data']['consulta'] }}</p>
            <p class="text-gray-600 text-md ">{{ props['data']['desc'] }}</p>
        </div>
        <!-- Card body -->
        <div class="flex items-end justify-between whitespace-normal">
            <!-- Paragraph -->
            <div class=" flex flex-col flex-wrap md:flex-row text-stone-600">
                <div v-for="i in props['data']['resultados']['hits']" class="mb-2">
                    <div class="mx-0 md:m-2 bg-stone-100 hover:bg-stone-200 rounded-lg px-4 py-2 cursor-pointer " @click="goDetails(i['fields']['id_custom'][0])">
                        <p class="text-sm capitalize">{{ i['fields']['title'][0] }}</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
  </template>
  
  <script setup>
  import { useRouter } from 'vue-router';
  const props = defineProps(['data'])
  const router = useRouter()

  const goDetails = async(id)=>{
      router.push('/dataset/'+id)
  }
  </script>
  