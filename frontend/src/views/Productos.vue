<template>
  <div class="min-h-screen bg-[#0f172a] text-white p-6 md:p-12 relative">
    <!-- Header y Buscador -->
    <header class="mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div class="flex items-center gap-4">
        <router-link to="/" class="p-2 bg-slate-800 rounded-xl hover:bg-slate-700 transition-colors text-slate-400 hover:text-white">
          <ArrowLeft class="w-6 h-6" />
        </router-link>
        <div>
          <h1 class="text-3xl md:text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-indigo-400">
            Productos
          </h1>
          <p class="text-slate-400 text-sm mt-1">Catálogo de inventario y precios base</p>
        </div>
      </div>
      
      <div class="flex flex-col md:flex-row items-center gap-4 w-full md:w-auto">
        <!-- Input de búsqueda -->
        <div class="relative w-full md:w-80">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search class="h-5 w-5 text-slate-500" />
          </div>
          <input 
            v-model="searchQuery" 
            @input="debouncedSearch"
            type="text" 
            class="block w-full pl-10 pr-3 py-3 border border-slate-700 rounded-2xl leading-5 bg-slate-800/50 text-slate-300 placeholder-slate-500 focus:outline-none focus:bg-slate-800 focus:border-violet-500 focus:ring-1 focus:ring-violet-500 transition-all sm:text-sm backdrop-blur-sm" 
            placeholder="Buscar producto por nombre..." 
          />
          <div v-if="loading" class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
            <Loader2 class="h-5 w-5 text-violet-500 animate-spin" />
          </div>
        </div>

        <!-- Botón Nuevo Producto -->
        <button @click="openCreateModal" class="w-full md:w-auto px-5 py-3 rounded-2xl font-semibold bg-violet-600 text-white hover:bg-violet-500 transition-colors flex items-center justify-center shadow-lg shadow-violet-600/20">
          <Plus class="w-5 h-5 mr-2" /> Nuevo Producto
        </button>
      </div>
    </header>

    <!-- Lista de Productos -->
    <div v-if="productos.length === 0 && !loading" class="text-center py-20 bg-slate-800/30 rounded-3xl border border-slate-700/50 backdrop-blur-sm">
      <Package class="mx-auto h-12 w-12 text-slate-500 mb-4" />
      <h3 class="text-lg font-medium text-slate-300">No se encontraron productos</h3>
      <p class="text-slate-500 mt-1">Intenta con otro término de búsqueda o agrega uno nuevo.</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div 
        v-for="producto in productos" 
        :key="producto.id" 
        @click="openProductDetails(producto)"
        class="bg-slate-800/40 border border-slate-700/50 rounded-2xl p-6 hover:border-violet-500/50 hover:bg-slate-800 transition-all cursor-pointer backdrop-blur-sm relative overflow-hidden group shadow-lg"
      >
        <!-- Decoración lateral -->
        <div class="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-violet-500 to-indigo-500 opacity-0 group-hover:opacity-100 transition-opacity"></div>
        
        <div class="flex items-start justify-between mb-4">
          <div class="w-full">
            <h3 class="text-xl font-bold text-slate-100 pr-2 leading-snug break-words">
              {{ producto.nombre }}
            </h3>
          </div>
        </div>

        <div class="space-y-3 mt-4">
          <div class="flex items-start gap-3">
            <FileText class="w-5 h-5 text-slate-500 shrink-0 mt-0.5" />
            <div>
              <p class="text-sm text-slate-300 line-clamp-2">{{ producto.descripcion || 'Sin descripción' }}</p>
            </div>
          </div>
          <div class="flex items-center gap-3">
            <Tag class="w-5 h-5 text-emerald-500 shrink-0" />
            <p class="text-lg text-emerald-400 font-bold">
              {{ new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP' }).format(producto.precio) }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal Detalles / Edición -->
    <div v-if="showModal" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:p-0">
        
        <div class="fixed inset-0 transition-opacity bg-slate-900/80 backdrop-blur-sm" @click="closeModal"></div>

        <div class="relative inline-block w-full max-w-2xl text-left align-middle transition-all transform bg-slate-900 border border-slate-700 rounded-3xl shadow-2xl overflow-hidden mt-10 mb-10">
          
          <div class="p-6 md:p-8">
            <div class="flex justify-between items-center mb-6">
              <h2 class="text-2xl font-bold text-white flex items-center gap-3">
                <Package class="text-violet-400 w-7 h-7" />
                {{ createMode ? 'Nuevo Producto' : selectedProducto?.nombre }}
              </h2>
              <button @click="closeModal" class="text-slate-400 hover:text-white p-2 rounded-full hover:bg-slate-800 transition">
                <X class="w-6 h-6" />
              </button>
            </div>

            <!-- Tabs -->
            <div v-if="!createMode" class="flex border-b border-slate-700 mb-6">
              <button 
                @click="activeTab = 'detalles'" 
                :class="{'text-violet-400 border-b-2 border-violet-400': activeTab === 'detalles', 'text-slate-400 hover:text-slate-200': activeTab !== 'detalles'}" 
                class="px-4 py-2 font-medium transition"
              >
                Detalles y Edición
              </button>
              <button 
                @click="activeTab = 'historial'" 
                :class="{'text-violet-400 border-b-2 border-violet-400': activeTab === 'historial', 'text-slate-400 hover:text-slate-200': activeTab !== 'historial'}" 
                class="px-4 py-2 font-medium transition"
              >
                Historial de Ventas
              </button>
            </div>

            <!-- Pestaña Detalles y Formulario -->
            <div v-if="(selectedProducto || createMode) && activeTab === 'detalles'" class="space-y-6">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                
                <!-- Nombre -->
                <div class="col-span-1 md:col-span-2">
                  <label class="block text-sm font-medium text-slate-400 mb-1">Nombre del Producto <span v-if="editMode" class="text-red-400">*</span></label>
                  <input v-if="editMode" v-model="formData.nombre" type="text" class="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:border-violet-500 outline-none" required />
                  <p v-else class="text-lg font-medium text-slate-200">{{ selectedProducto?.nombre }}</p>
                </div>

                <!-- Descripción -->
                <div class="col-span-1 md:col-span-2">
                  <label class="block text-sm font-medium text-slate-400 mb-1">Descripción</label>
                  <textarea v-if="editMode" v-model="formData.descripcion" rows="3" class="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:border-violet-500 outline-none"></textarea>
                  <p v-else class="text-slate-300 whitespace-pre-wrap">{{ selectedProducto?.descripcion || 'Sin descripción' }}</p>
                </div>

                <!-- Precio Base -->
                <div>
                  <label class="block text-sm font-medium text-slate-400 mb-1">Precio Base (Referencia) <span v-if="editMode" class="text-red-400">*</span></label>
                  <input v-if="editMode" v-model="formData.precio" type="number" step="0.01" class="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:border-violet-500 outline-none" required />
                  <p v-else class="text-xl font-bold text-emerald-400">
                    {{ new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP' }).format(selectedProducto?.precio || 0) }}
                  </p>
                </div>

              </div>

              <!-- Botones de Acción Formulario -->
              <div class="mt-8 pt-6 border-t border-slate-700 flex flex-wrap gap-3 justify-end">
                <template v-if="editMode">
                  <button @click="createMode ? closeModal() : editMode = false" class="px-5 py-2.5 rounded-xl font-medium bg-slate-800 text-slate-300 hover:bg-slate-700 transition">
                    Cancelar
                  </button>
                  <button @click="saveProducto" :disabled="saving" class="px-5 py-2.5 rounded-xl font-medium bg-violet-600 text-white hover:bg-violet-500 transition flex items-center disabled:opacity-50">
                    <Loader2 v-if="saving" class="w-4 h-4 mr-2 animate-spin" />
                    <Save v-else class="w-4 h-4 mr-2" />
                    Guardar Producto
                  </button>
                </template>
                
                <template v-else>
                  <button @click="confirmDelete" class="px-5 py-2.5 rounded-xl font-medium bg-red-500/10 text-red-400 hover:bg-red-500/20 transition flex items-center mr-auto">
                    <Trash2 class="w-4 h-4 mr-2" /> Eliminar
                  </button>
                  <button @click="editMode = true" class="px-5 py-2.5 rounded-xl font-medium bg-violet-600 text-white hover:bg-violet-500 transition flex items-center">
                    <Edit class="w-4 h-4 mr-2" /> Editar
                  </button>
                </template>
              </div>
            </div>

            <!-- Pestaña Historial de Ventas -->
            <div v-if="activeTab === 'historial'" class="space-y-4 min-h-[300px]">
              <div v-if="loadingHistorial" class="flex justify-center items-center h-40">
                <Loader2 class="w-8 h-8 text-violet-500 animate-spin" />
              </div>
              <div v-else-if="historialVentas.length === 0" class="text-center py-12 bg-slate-800/30 rounded-2xl border border-slate-700/50">
                <History class="mx-auto h-10 w-10 text-slate-500 mb-3" />
                <h3 class="text-lg font-medium text-slate-300">Sin historial</h3>
                <p class="text-slate-500 text-sm">Este producto aún no ha sido incluido en ningún pedido.</p>
              </div>
              <div v-else class="space-y-3">
                <div v-for="item in historialVentas" :key="item.pedido_id" class="flex flex-col md:flex-row md:items-center justify-between p-4 bg-slate-800/50 rounded-xl border border-slate-700/50 hover:bg-slate-800 transition gap-4">
                  <div class="flex-1">
                    <div class="flex items-center gap-2 mb-1">
                      <span class="text-slate-200 font-bold">Pedido #{{ item.pedido_id }}</span>
                      <span class="text-sm text-slate-400">{{ new Date(item.fecha).toLocaleString() }}</span>
                    </div>
                    <div class="flex items-center gap-2">
                      <User class="w-4 h-4 text-slate-500" />
                      <p class="text-sm text-slate-300 font-medium truncate">{{ item.cliente_nombre }}</p>
                    </div>
                  </div>
                  
                  <div class="flex items-center gap-6 text-right">
                    <div>
                      <p class="text-xs text-slate-400 uppercase tracking-wider mb-1">Cant.</p>
                      <p class="text-lg text-slate-200 font-medium">{{ item.cantidad }}</p>
                    </div>
                    <div>
                      <p class="text-xs text-slate-400 uppercase tracking-wider mb-1">Precio Unit.</p>
                      <p class="text-lg font-bold text-emerald-400">
                        {{ new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP' }).format(item.precio_unitario) }}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { ArrowLeft, Search, Loader2, Package, Plus, X, Edit, Trash2, Save, FileText, Tag, History, User } from 'lucide-vue-next'
import api from '../services/api'

const productos = ref([])
const searchQuery = ref('')
const loading = ref(false)
let searchTimeout = null

// Modal state
const showModal = ref(false)
const editMode = ref(false)
const createMode = ref(false)
const activeTab = ref('detalles') // 'detalles' o 'historial'
const selectedProducto = ref(null)
const formData = ref({
  nombre: '',
  descripcion: '',
  precio: 0
})
const saving = ref(false)

// Historial state
const historialVentas = ref([])
const loadingHistorial = ref(false)

const fetchProductos = async () => {
  loading.value = true
  try {
    const params = {}
    if (searchQuery.value.trim() !== '') {
      params.search = searchQuery.value.trim()
    }
    const response = await api.get('/productos', { params })
    productos.value = response.data
  } catch (error) {
    console.error("Error al obtener productos:", error)
  } finally {
    loading.value = false
  }
}

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    fetchProductos()
  }, 400)
}

const openCreateModal = () => {
  selectedProducto.value = null
  createMode.value = true
  editMode.value = true
  activeTab.value = 'detalles'
  formData.value = {
    nombre: '',
    descripcion: '',
    precio: 0
  }
  showModal.value = true
}

const fetchHistorial = async (productoId) => {
  loadingHistorial.value = true
  try {
    const response = await api.get(`/productos/${productoId}/historial`)
    historialVentas.value = response.data
  } catch (error) {
    console.error("Error al obtener historial:", error)
  } finally {
    loadingHistorial.value = false
  }
}

const openProductDetails = (producto) => {
  selectedProducto.value = producto
  formData.value = { ...producto }
  createMode.value = false
  editMode.value = false
  activeTab.value = 'detalles'
  showModal.value = true
}

watch(activeTab, (newTab) => {
  if (newTab === 'historial' && selectedProducto.value) {
    fetchHistorial(selectedProducto.value.id)
  }
})

const closeModal = () => {
  showModal.value = false
  selectedProducto.value = null
  editMode.value = false
  createMode.value = false
  activeTab.value = 'detalles'
  historialVentas.value = []
}

const saveProducto = async () => {
  if (!formData.value.nombre || formData.value.precio === null || formData.value.precio === undefined) {
    alert("El Nombre y el Precio Base son obligatorios.")
    return
  }
  
  saving.value = true
  try {
    if (createMode.value) {
      const response = await api.post('/productos', formData.value)
      productos.value.unshift(response.data)
      selectedProducto.value = response.data
      createMode.value = false
      editMode.value = false
    } else {
      const response = await api.put(`/productos/${selectedProducto.value.id}`, formData.value)
      const index = productos.value.findIndex(p => p.id === selectedProducto.value.id)
      if (index !== -1) {
        productos.value[index] = response.data
      }
      selectedProducto.value = response.data
      editMode.value = false
    }
  } catch (error) {
    console.error("Error al guardar:", error)
    alert("Hubo un error al guardar los cambios.")
  } finally {
    saving.value = false
  }
}

const confirmDelete = async () => {
  if (confirm(`¿Estás seguro de que deseas eliminar el producto ${selectedProducto.value.nombre}? Esta acción no se puede deshacer.`)) {
    try {
      await api.delete(`/productos/${selectedProducto.value.id}`)
      productos.value = productos.value.filter(p => p.id !== selectedProducto.value.id)
      closeModal()
    } catch (error) {
      console.error("Error al eliminar:", error)
      alert("No se pudo eliminar el producto. Verifica que no tenga pedidos asociados.")
    }
  }
}

onMounted(() => {
  fetchProductos()
})
</script>
