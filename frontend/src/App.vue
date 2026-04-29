<template>
  <div id="app">
    <router-view v-slot="{ Component }">
      <transition 
        name="fade" 
        mode="out-in"
      >
        <component :is="Component" />
      </transition>
    </router-view>
  </div>
</template>

<script setup>
// Configuración global si es necesaria
</script>

<style>
/* Reset básico y transiciones */
body {
  margin: 0;
  padding: 0;
  background-color: #0f172a;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
