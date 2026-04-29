<template>
  <div class="min-h-screen bg-[#0f172a] text-white p-6 md:p-12">
    <!-- Header -->
    <header class="mb-12">
      <h1 class="text-4xl md:text-5xl font-extrabold bg-clip-text text-transparent bg-gradient-to-r from-violet-400 to-indigo-400 mb-2">
        Jose App
      </h1>
      <p class="text-slate-400 text-lg">Panel de gestión centralizada</p>
    </header>

    <!-- Menu Grid -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <!-- Clientes Card -->
      <router-link to="/clientes" class="group relative overflow-hidden rounded-3xl bg-slate-800/50 border border-slate-700/50 p-8 hover:border-violet-500/50 transition-all duration-300 backdrop-blur-xl">
        <div class="absolute -right-4 -top-4 w-32 h-32 bg-violet-600/10 rounded-full blur-3xl group-hover:bg-violet-600/20 transition-all duration-500"></div>
        <div class="flex flex-col h-full relative z-10">
          <div class="w-14 h-14 bg-violet-500/20 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
            <Users class="text-violet-400 w-8 h-8" />
          </div>
          <h2 class="text-2xl font-bold mb-3">Clientes</h2>
          <p class="text-slate-400 leading-relaxed">
            Gestión de base de datos, contactos y ubicaciones.
          </p>
          <div class="mt-auto pt-6 flex items-center text-violet-400 font-semibold text-sm">
            Explorar <ChevronRight class="ml-1 w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </div>
        </div>
      </router-link>

      <!-- Pedidos Card -->
      <router-link to="/pedidos" class="group relative overflow-hidden rounded-3xl bg-slate-800/50 border border-slate-700/50 p-8 hover:border-indigo-500/50 transition-all duration-300 backdrop-blur-xl">
        <div class="absolute -right-4 -top-4 w-32 h-32 bg-indigo-600/10 rounded-full blur-3xl group-hover:bg-indigo-600/20 transition-all duration-500"></div>
        <div class="flex flex-col h-full relative z-10">
          <div class="w-14 h-14 bg-indigo-500/20 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
            <ShoppingCart class="text-indigo-400 w-8 h-8" />
          </div>
          <h2 class="text-2xl font-bold mb-3">Pedidos</h2>
          <p class="text-slate-400 leading-relaxed">
            Control de órdenes, estados y seguimiento de entregas.
          </p>
          <div class="mt-auto pt-6 flex items-center text-indigo-400 font-semibold text-sm">
            Gestionar <ChevronRight class="ml-1 w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </div>
        </div>
      </router-link>

      <!-- Productos Card -->
      <router-link to="/productos" class="group relative overflow-hidden rounded-3xl bg-slate-800/50 border border-slate-700/50 p-8 hover:border-emerald-500/50 transition-all duration-300 backdrop-blur-xl">
        <div class="absolute -right-4 -top-4 w-32 h-32 bg-emerald-600/10 rounded-full blur-3xl group-hover:bg-emerald-600/20 transition-all duration-500"></div>
        <div class="flex flex-col h-full relative z-10">
          <div class="w-14 h-14 bg-emerald-500/20 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
            <Package class="text-emerald-400 w-8 h-8" />
          </div>
          <h2 class="text-2xl font-bold mb-3">Productos</h2>
          <p class="text-slate-400 leading-relaxed">
            Catálogo de artículos, inventario y listas de precios.
          </p>
          <div class="mt-auto pt-6 flex items-center text-emerald-400 font-semibold text-sm">
            Ver catálogo <ChevronRight class="ml-1 w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </div>
        </div>
      </router-link>
    </div>

    <!-- Stats or Footer Info -->
    <div class="mt-12 p-8 rounded-3xl bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700/50 flex flex-wrap gap-12 items-center">
      <div class="flex items-center gap-4">
        <div class="p-3 bg-blue-500/10 rounded-xl">
          <Activity class="text-blue-400 w-6 h-6" />
        </div>
        <div>
          <p class="text-xs text-slate-400 uppercase tracking-wider font-bold">Estado del Sistema</p>
          <p class="text-emerald-400 font-medium">Operativo</p>
        </div>
      </div>
      
      <div class="flex items-center gap-4">
        <div class="p-3 bg-purple-500/10 rounded-xl">
          <Cloud class="text-purple-400 w-6 h-6" />
        </div>
        <div>
          <p class="text-xs text-slate-400 uppercase tracking-wider font-bold">Base de Datos</p>
          <p class="text-white font-medium">Supabase PostgreSQL</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Users, ShoppingCart, Package, ChevronRight, Activity, Cloud } from 'lucide-vue-next'
</script>

<style scoped>
/* Transiciones suaves para las tarjetas */
.backdrop-blur-xl {
  backdrop-filter: blur(24px);
}
</style>
