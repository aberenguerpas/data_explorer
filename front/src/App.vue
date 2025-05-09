<script setup>
import { RouterView } from 'vue-router'
</script>

<template>
    <RouterView v-slot="{ Component }">
      <KeepAlive include="ResultsView">
        <component :is="Component" />
      </KeepAlive>
    </RouterView>
</template>