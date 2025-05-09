<template>
  <div class="item">
    <div class="h-full">
        <!-- Card -->
        <div class="mx-auto bg-white shadow-lg rounded-lg">
            <div class="px-6 py-5">
                <div class="flex items-start">
                    <!-- Icon -->
                    <svg class="fill-current flex-shrink-0 mr-5" width="30" height="30" viewBox="0 0 30 30">
                        <path class="text-blue-300" d="m16 14.883 14-7L14.447.106a1 1 0 0 0-.895 0L0 6.883l16 8Z" />
                        <path class="text-blue-200" d="M16 14.619v15l13.447-6.724A.998.998 0 0 0 30 22V7.619l-14 7Z" />
                        <path class="text-blue-400" d="m16 14.619-16-8V21c0 .379.214.725.553.895L16 29.619v-15Z" />
                    </svg>
                    <!-- Card content -->
                    <div class="flex-grow truncate">
                        <!-- Card header -->
                        <div class="w-full sm:flex justify-between items-center mb-3">
                            <!-- Title -->
                            <h2 class="text-md leading-snug font-extrabold text-gray-600 truncate mb-1 sm:mb-0">{{ props['data']['fields']['title'][0] }}</h2>
                        </div>
                        <!-- Card body -->
                        <div class="flex items-end justify-between whitespace-normal text-md">
                            <!-- Paragraph -->
                            <div class="text-stone-500 line-clamp-3">
                                <p class="mb-2">{{ props['data']['fields']['description'][0] }}</p>
                            </div>
                            <!-- More link -->
                            <button class="flex-shrink-0 flex items-center justify-center text-blue-600 w-10 h-10 rounded-full bg-gradient-to-b from-blue-50 to-blue-100 hover:from-white hover:to-blue-50 focus:outline-none focus-visible:from-white focus-visible:to-white transition duration-150 ml-2" @click="goDetails">
                                <span class="block font-bold"><span class="sr-only">Read more</span> -></span>
                            </button>
                        </div>
                    </div>
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
const goDetails = async()=>{
    await router.push('/dataset/'+props['data']['fields']['id_custom'])
    //router.go(0)
}
</script>


