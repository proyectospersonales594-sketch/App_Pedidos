<template>
  <div class="min-h-screen bg-[#0f172a] text-white p-6 md:p-12 relative">

    <!-- Header -->
    <header class="mb-8 relative flex flex-col md:flex-row md:items-center justify-between gap-4">
      <router-link to="/" class="absolute left-0 top-1 p-2 bg-slate-800 rounded-xl hover:bg-slate-700 transition-colors text-slate-400 hover:text-white">
        <ArrowLeft class="w-6 h-6" />
      </router-link>
      <div class="text-center w-full pt-12 md:pt-0 md:text-left md:ml-16">
        <h1 class="text-3xl md:text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-amber-400 to-orange-400">
          Informe de Ventas
        </h1>
        <p class="text-slate-400 text-sm mt-1">Historial y análisis de facturación por período</p>
      </div>
    </header>

    <!-- Formulario de consulta -->
    <div class="bg-slate-800/40 border border-slate-700/50 rounded-2xl p-6 mb-8 backdrop-blur-sm">
      <h2 class="text-lg font-semibold text-slate-200 mb-4 flex items-center justify-center sm:justify-start gap-2">
        <Search class="w-5 h-5 text-amber-400" />
        Consultar por período
      </h2>
      <div class="flex flex-col sm:flex-row gap-4 items-end">
        <!-- Selector de Mes -->
        <div class="flex flex-col gap-1 flex-1">
          <label class="text-xs text-slate-400 font-semibold uppercase tracking-wider">Mes</label>
          <select
            v-model="mesSeleccionado"
            id="select-mes"
            class="bg-slate-900/60 border border-slate-600 text-slate-200 rounded-xl px-4 py-3 focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500 transition-all"
          >
            <option v-for="m in meses" :key="m.valor" :value="m.valor">{{ m.nombre }}</option>
          </select>
        </div>

        <!-- Selector de Año -->
        <div class="flex flex-col gap-1 flex-1">
          <label class="text-xs text-slate-400 font-semibold uppercase tracking-wider">Año</label>
          <select
            v-model="anioSeleccionado"
            id="select-anio"
            class="bg-slate-900/60 border border-slate-600 text-slate-200 rounded-xl px-4 py-3 focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500 transition-all"
          >
            <option v-for="a in anios" :key="a" :value="a">{{ a }}</option>
          </select>
        </div>

        <!-- Botón Consultar -->
        <button
          @click="consultarMes"
          :disabled="loadingDetalle"
          id="btn-consultar"
          class="px-6 py-3 rounded-xl font-semibold bg-amber-500 text-slate-900 hover:bg-amber-400 transition-colors flex items-center gap-2 shadow-lg shadow-amber-500/20 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Loader2 v-if="loadingDetalle" class="w-5 h-5 animate-spin" />
          <BarChart2 v-else class="w-5 h-5" />
          Consultar
        </button>

        <!-- Botón Exportar (solo aparece tras consultar) -->
        <Transition name="fade">
          <button
            v-if="resultadoDetalle.length > 0"
            @click="exportarMes"
            :disabled="isExporting"
            id="btn-exportar-informe"
            class="px-6 py-3 rounded-xl font-semibold bg-emerald-600 text-white hover:bg-emerald-500 transition-colors flex items-center gap-2 shadow-lg shadow-emerald-600/20 active:scale-95 disabled:opacity-50"
          >
            <Loader2 v-if="isExporting" class="w-5 h-5 animate-spin" />
            <Download v-else class="w-5 h-5" />
            Exportar Excel
          </button>
        </Transition>
      </div>
    </div>

    <!-- Resultado de la consulta por mes -->
    <Transition name="slide-down">
      <div v-if="resultadoDetalle.length > 0 || consultaRealizada" class="mb-10">
        <div class="flex flex-col md:flex-row items-center md:justify-between mb-4 gap-4">
          <h2 class="text-xl font-bold text-slate-100 flex items-center justify-center md:justify-start gap-2 text-center md:text-left">
            <TrendingUp class="w-5 h-5 text-emerald-400" />
            Ventas de {{ nombreMesSeleccionado }} {{ anioSeleccionado }}
          </h2>
          <!-- Resumen rápido -->
          <div class="flex justify-center md:justify-end gap-4 w-full md:w-auto" v-if="resultadoDetalle.length > 0">
            <div class="text-right">
              <p class="text-xs text-slate-400">Total Ventas</p>
              <p class="text-lg font-bold text-emerald-400">{{ formatCurrency(totalVentasMes) }}</p>
            </div>
            <div class="text-right">
              <p class="text-xs text-slate-400">Pedidos</p>
              <p class="text-lg font-bold text-amber-400">{{ totalPedidosMes }}</p>
            </div>
          </div>
        </div>

        <div v-if="resultadoDetalle.length === 0 && consultaRealizada" class="text-center py-12 bg-slate-800/30 rounded-2xl border border-slate-700/50">
          <BarChart2 class="mx-auto h-10 w-10 text-slate-500 mb-3" />
          <p class="text-slate-400">No hay pedidos registrados en este período.</p>
        </div>

        <div v-else class="bg-slate-800/40 border border-slate-700/50 rounded-2xl overflow-x-auto backdrop-blur-sm w-full">
          <table class="w-full text-sm">
            <thead>
              <tr class="bg-slate-700/60 text-slate-300">
                <th class="text-left px-5 py-3 font-semibold">#</th>
                <th class="text-left px-5 py-3 font-semibold">Negocio / Cliente</th>
                <th class="text-right px-5 py-3 font-semibold">Total Ventas</th>
                <th class="text-center px-5 py-3 font-semibold">Pedidos</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(row, idx) in resultadoDetalle"
                :key="idx"
                class="border-t border-slate-700/40 hover:bg-slate-700/30 transition-colors"
              >
                <td class="px-5 py-3 text-slate-500 font-mono text-xs">{{ idx + 1 }}</td>
                <td class="px-5 py-3">
                  <p class="font-semibold text-slate-100">{{ row.nombre_negocio || row.cliente_nombre }}</p>
                  <p v-if="row.nombre_negocio" class="text-xs text-slate-400 mt-0.5">{{ row.cliente_nombre }}</p>
                </td>
                <td class="px-5 py-3 text-right">
                  <span class="text-emerald-400 font-bold">{{ formatCurrency(row.total_ventas) }}</span>
                </td>
                <td class="px-5 py-3 text-center">
                  <span class="inline-flex items-center justify-center w-8 h-8 rounded-full bg-amber-500/10 text-amber-400 font-bold text-xs">
                    {{ row.cantidad_pedidos }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </Transition>

    <!-- Historial Mensual -->
    <div>
      <h2 class="text-xl font-bold text-slate-100 mb-5 flex items-center justify-center md:justify-start gap-2 text-center md:text-left">
        <Calendar class="w-5 h-5 text-amber-400" />
        Historial de Ventas por Mes
      </h2>

      <!-- Skeleton loader -->
      <div v-if="loadingHistorico" class="space-y-2">
        <div v-for="i in 6" :key="i" class="h-14 bg-slate-800/40 rounded-xl animate-pulse"></div>
      </div>

      <div v-else-if="resumenHistorico.length === 0" class="text-center py-16 bg-slate-800/30 rounded-2xl border border-slate-700/50">
        <Calendar class="mx-auto h-10 w-10 text-slate-500 mb-3" />
        <p class="text-slate-400">No hay datos de ventas históricos aún.</p>
      </div>

      <div v-else class="bg-slate-800/40 border border-slate-700/50 rounded-2xl overflow-x-auto backdrop-blur-sm w-full">
        <table class="w-full text-sm">
          <thead>
            <tr class="bg-slate-700/60 text-slate-300">
              <th class="text-left px-5 py-3 font-semibold">Período</th>
              <th class="text-right px-5 py-3 font-semibold">Total Ventas</th>
              <th class="text-center px-5 py-3 font-semibold">Pedidos</th>
              <th class="text-center px-5 py-3 font-semibold">Acción</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(row, idx) in resumenHistorico"
              :key="idx"
              class="border-t border-slate-700/40 hover:bg-slate-700/30 transition-colors"
              :class="{ 'bg-amber-500/5': esMesActual(row) }"
            >
              <td class="px-5 py-4">
                <div class="flex items-center gap-3">
                  <div class="w-2 h-2 rounded-full" :class="esMesActual(row) ? 'bg-amber-400' : 'bg-slate-600'"></div>
                  <div>
                    <p class="font-semibold text-slate-100">{{ row.nombre_mes }} {{ row.anio }}</p>
                    <p v-if="esMesActual(row)" class="text-xs text-amber-400">Mes actual</p>
                  </div>
                </div>
              </td>
              <td class="px-5 py-4 text-right">
                <span class="text-emerald-400 font-bold text-base">{{ formatCurrency(row.total_ventas) }}</span>
              </td>
              <td class="px-5 py-4 text-center">
                <span class="inline-flex items-center justify-center w-8 h-8 rounded-full bg-amber-500/10 text-amber-400 font-bold text-xs">
                  {{ row.cantidad_pedidos }}
                </span>
              </td>
              <td class="px-5 py-4 text-center">
                <button
                  @click="seleccionarMesHistorico(row)"
                  class="text-xs px-3 py-1.5 rounded-lg bg-slate-700 hover:bg-amber-500/20 text-slate-300 hover:text-amber-400 border border-slate-600 hover:border-amber-500/50 transition-all"
                >
                  Ver detalle
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ArrowLeft, Search, BarChart2, Download, Loader2, TrendingUp, Calendar } from 'lucide-vue-next'
import api from '../services/api'

// --- Estado ---
const resumenHistorico = ref([])
const resultadoDetalle = ref([])
const loadingHistorico = ref(true)
const loadingDetalle = ref(false)
const isExporting = ref(false)
const consultaRealizada = ref(false)

const anioActual = new Date().getFullYear()
const mesActual = new Date().getMonth() + 1

const mesSeleccionado = ref(mesActual)
const anioSeleccionado = ref(anioActual)

const meses = [
  { valor: 1, nombre: 'Enero' }, { valor: 2, nombre: 'Febrero' }, { valor: 3, nombre: 'Marzo' },
  { valor: 4, nombre: 'Abril' }, { valor: 5, nombre: 'Mayo' }, { valor: 6, nombre: 'Junio' },
  { valor: 7, nombre: 'Julio' }, { valor: 8, nombre: 'Agosto' }, { valor: 9, nombre: 'Septiembre' },
  { valor: 10, nombre: 'Octubre' }, { valor: 11, nombre: 'Noviembre' }, { valor: 12, nombre: 'Diciembre' },
]

const anios = computed(() => {
  const lista = []
  for (let y = anioActual; y >= 2024; y--) lista.push(y)
  return lista
})

const nombreMesSeleccionado = computed(() => {
  return meses.find(m => m.valor === mesSeleccionado.value)?.nombre || ''
})

const totalVentasMes = computed(() => resultadoDetalle.value.reduce((sum, r) => sum + r.total_ventas, 0))
const totalPedidosMes = computed(() => resultadoDetalle.value.reduce((sum, r) => sum + r.cantidad_pedidos, 0))

// --- Métodos ---
const formatCurrency = (val) => {
  return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', minimumFractionDigits: 0 }).format(val)
}

const esMesActual = (row) => row.mes === mesActual && row.anio === anioActual

const cargarHistorico = async () => {
  loadingHistorico.value = true
  try {
    const res = await api.get('/informes/resumen-historico')
    resumenHistorico.value = res.data.reverse() // Más reciente primero
  } catch (e) {
    console.error('Error cargando histórico:', e)
  } finally {
    loadingHistorico.value = false
  }
}

const consultarMes = async () => {
  loadingDetalle.value = true
  consultaRealizada.value = false
  resultadoDetalle.value = []
  try {
    const res = await api.get('/informes/detalle-mes', {
      params: { anio: anioSeleccionado.value, mes: mesSeleccionado.value }
    })
    resultadoDetalle.value = res.data
    consultaRealizada.value = true
  } catch (e) {
    console.error('Error consultando mes:', e)
  } finally {
    loadingDetalle.value = false
  }
}

const seleccionarMesHistorico = (row) => {
  mesSeleccionado.value = row.mes
  anioSeleccionado.value = row.anio
  consultarMes()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const exportarMes = async () => {
  isExporting.value = true
  try {
    const res = await api.get('/informes/exportar-mes', {
      params: { anio: anioSeleccionado.value, mes: mesSeleccionado.value },
      responseType: 'blob'
    })
    const blob = new Blob([res.data], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    const contentDisposition = res.headers['content-disposition']
    let filename = `Informe_Ventas_${nombreMesSeleccionado.value}_${anioSeleccionado.value}.xlsx`
    if (contentDisposition) {
      const match = contentDisposition.match(/filename="?([^"]+)"?/)
      if (match) filename = match[1]
    }
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (e) {
    console.error('Error exportando:', e)
    alert('Hubo un error al exportar el informe.')
  } finally {
    isExporting.value = false
  }
}

onMounted(cargarHistorico)
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.slide-down-enter-active { transition: all 0.4s ease; }
.slide-down-enter-from { opacity: 0; transform: translateY(-12px); }
</style>
