import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useSearchStore = defineStore('searchStore', () => {
  const InputSearch = ref('')

  return { InputSearch }
})
