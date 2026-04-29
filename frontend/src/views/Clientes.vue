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
            Clientes
          </h1>
          <p class="text-slate-400 text-sm mt-1">Directorio de cuentas y contactos</p>
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
            placeholder="Buscar por nombre o negocio..." 
          />
          <div v-if="loading" class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
            <Loader2 class="h-5 w-5 text-violet-500 animate-spin" />
          </div>
        </div>

        <!-- Botón Nuevo Cliente -->
        <button @click="openCreateModal" class="w-full md:w-auto px-5 py-3 rounded-2xl font-semibold bg-violet-600 text-white hover:bg-violet-500 transition-colors flex items-center justify-center shadow-lg shadow-violet-600/20">
          <Plus class="w-5 h-5 mr-2" /> Nuevo Cliente
        </button>
      </div>
    </header>

    <!-- Lista de Clientes -->
    <div v-if="clientes.length === 0 && !loading" class="text-center py-20 bg-slate-800/30 rounded-3xl border border-slate-700/50 backdrop-blur-sm">
      <Users class="mx-auto h-12 w-12 text-slate-500 mb-4" />
      <h3 class="text-lg font-medium text-slate-300">No se encontraron clientes</h3>
      <p class="text-slate-500 mt-1">Intenta con otro término de búsqueda.</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div 
        v-for="cliente in clientes" 
        :key="cliente.id" 
        @click="openClientDetails(cliente)"
        class="bg-slate-800/40 border border-slate-700/50 rounded-2xl p-6 hover:border-violet-500/50 hover:bg-slate-800 transition-all cursor-pointer backdrop-blur-sm relative overflow-hidden group shadow-lg"
      >
        <!-- Decoración lateral -->
        <div class="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-violet-500 to-indigo-500 opacity-0 group-hover:opacity-100 transition-opacity"></div>
        
        <div class="flex items-start justify-between mb-4">
          <div class="w-full">
            <h3 class="text-xl font-bold text-slate-100 pr-2 leading-snug break-words">
              {{ cliente.nombre_negocio || cliente.nombre_cliente }}
            </h3>
            <div class="flex items-center gap-2 mt-1">
              <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-slate-700 text-slate-300">
                NIT: {{ cliente.cc_o_nit }}
              </span>
              <span v-if="cliente.tipo_negocio" class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-indigo-500/20 text-indigo-300">
                {{ cliente.tipo_negocio }}
              </span>
            </div>
          </div>
        </div>

        <div class="space-y-3 mt-6">
          <div class="flex items-start gap-3">
            <MapPin class="w-5 h-5 text-slate-500 shrink-0 mt-0.5" />
            <div>
              <p class="text-sm text-slate-300">{{ cliente.direccion || 'Sin dirección' }}</p>
            </div>
          </div>
          <div class="flex items-center gap-3">
            <Phone class="w-5 h-5 text-slate-500 shrink-0" />
            <p class="text-sm text-slate-300">{{ cliente.telefono || 'Sin teléfono' }}</p>
          </div>
          <div class="flex items-center gap-3">
            <User class="w-5 h-5 text-slate-500 shrink-0" />
            <p class="text-sm text-slate-300 font-medium">{{ cliente.nombre_cliente }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal Detalle/Editar -->
    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="closeModal"></div>
      
      <div class="relative bg-slate-900 border border-slate-700 rounded-3xl w-full max-w-4xl max-h-[90vh] overflow-y-auto shadow-2xl">
        <div class="p-6 md:p-8">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-2xl font-bold text-white flex items-center gap-3">
              <User v-if="!createMode" class="text-violet-400 w-7 h-7" />
              <UserPlus v-else class="text-violet-400 w-7 h-7" />
              {{ createMode ? 'Nuevo Cliente' : (selectedCliente?.nombre_negocio || selectedCliente?.nombre_cliente) }}
            </h2>
            <button @click="closeModal" class="text-slate-400 hover:text-white p-2 rounded-full hover:bg-slate-800 transition">
              <X class="w-6 h-6" />
            </button>
          </div>

          <!-- Tabs (sólo si no estamos creando uno nuevo) -->
          <div v-if="!createMode" class="flex border-b border-slate-700 mb-6">
            <button 
              @click="activeTab = 'detalles'" 
              :class="{'text-violet-400 border-b-2 border-violet-400': activeTab === 'detalles', 'text-slate-400 hover:text-slate-200': activeTab !== 'detalles'}" 
              class="px-4 py-2 font-medium transition"
            >
              Detalles y Edición
            </button>
            <button 
              @click="activeTab = 'pedidos'" 
              :class="{'text-violet-400 border-b-2 border-violet-400': activeTab === 'pedidos', 'text-slate-400 hover:text-slate-200': activeTab !== 'pedidos'}" 
              class="px-4 py-2 font-medium transition"
            >
              Historial de Pedidos
            </button>
          </div>

          <!-- Formulario / Detalles -->
          <div v-if="(selectedCliente || createMode) && activeTab === 'detalles'" class="space-y-6">
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <!-- Nombre -->
              <div class="col-span-1 md:col-span-2">
                <label class="block text-sm font-medium text-slate-400 mb-1">Nombre del Negocio <span v-if="editMode" class="text-red-400">*</span></label>
                <input v-if="editMode" v-model="formData.nombre_negocio" type="text" class="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:border-violet-500 focus:ring-1 focus:ring-violet-500 outline-none" />
                <p v-else class="text-lg font-medium text-slate-200">{{ selectedCliente?.nombre_negocio || selectedCliente?.nombre_cliente }}</p>
              </div>

              <!-- NIT -->
              <div>
                <label class="block text-sm font-medium text-slate-400 mb-1">CC o NIT <span v-if="editMode" class="text-red-400">*</span></label>
                <input v-if="editMode" v-model="formData.cc_o_nit" type="text" class="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:border-violet-500 outline-none" required />
                <p v-else class="text-slate-300">{{ selectedCliente?.cc_o_nit || 'N/A' }}</p>
              </div>

              <!-- Nombre Negocio -->
              <div>
                <label class="block text-sm font-medium text-slate-400 mb-1">Nombre del Cliente</label>
                <input v-if="editMode" v-model="formData.nombre_cliente" type="text" class="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:border-violet-500 outline-none" required />
                <p v-else class="text-slate-300">{{ selectedCliente?.nombre_cliente || 'N/A' }}</p>
              </div>

              <!-- Teléfono -->
              <div>
                <label class="block text-sm font-medium text-slate-400 mb-1">Teléfono</label>
                <input v-if="editMode" v-model="formData.telefono" type="text" class="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:border-violet-500 outline-none" />
                <p v-else class="text-slate-300">{{ selectedCliente?.telefono || 'N/A' }}</p>
              </div>

              <!-- Correo -->
              <div>
                <label class="block text-sm font-medium text-slate-400 mb-1">Correo Electrónico</label>
                <input v-if="editMode" v-model="formData.correo_electronico" type="email" class="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:border-violet-500 outline-none" />
                <p v-else class="text-slate-300">{{ selectedCliente?.correo_electronico || 'N/A' }}</p>
              </div>

              <!-- Dirección -->
              <div class="col-span-1 md:col-span-2">
                <label class="block text-sm font-medium text-slate-400 mb-1">Dirección</label>
                <input v-if="editMode" v-model="formData.direccion" type="text" class="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:border-violet-500 outline-none" />
                <p v-else class="text-slate-300">{{ selectedCliente?.direccion || 'N/A' }}</p>
              </div>

              <!-- Barrio / Población -->
              <div>
                <label class="block text-sm font-medium text-slate-400 mb-1">Barrio / Población</label>
                <input v-if="editMode" v-model="formData.barrio_poblacion" type="text" class="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:border-violet-500 outline-none" />
                <p v-else class="text-slate-300">{{ selectedCliente?.barrio_poblacion || 'N/A' }}</p>
              </div>

              <!-- Ubicación -->
              <div>
                <label class="block text-sm font-medium text-slate-400 mb-1">Ubicación</label>
                <select v-if="editMode" v-model="formData.ubicacion" class="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:border-violet-500 outline-none">
                  <option value="">Selecciona...</option>
                  <option v-for="opcion in opcionesUbicacion" :key="opcion" :value="opcion">{{ opcion }}</option>
                </select>
                <p v-else class="text-slate-300">{{ selectedCliente?.ubicacion || 'N/A' }}</p>
              </div>

               <!-- Contacto Comercial -->
               <div>
                <label class="block text-sm font-medium text-slate-400 mb-1">Contacto Comercial</label>
                <input v-if="editMode" v-model="formData.contacto_comercial" type="text" class="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:border-violet-500 outline-none" />
                <p v-else class="text-slate-300">{{ selectedCliente?.contacto_comercial || 'N/A' }}</p>
              </div>

              <!-- Días de Visita -->
              <div>
                <label class="block text-sm font-medium text-slate-400 mb-1">Días de Visita</label>
                <input v-if="editMode" v-model="formData.dias_visita" type="text" class="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:border-violet-500 outline-none" />
                <p v-else class="text-slate-300">{{ selectedCliente?.dias_visita || 'N/A' }}</p>
              </div>

              <!-- Tipo de negocio -->
              <div>
                <label class="block text-sm font-medium text-slate-400 mb-1">Tipo de Negocio</label>
                <select v-if="editMode" v-model="formData.tipo_negocio" class="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:border-violet-500 outline-none">
                  <option value="">Selecciona...</option>
                  <option v-for="opcion in opcionesTipoNegocio" :key="opcion" :value="opcion">{{ opcion }}</option>
                </select>
                <p v-else class="text-slate-300">{{ selectedCliente?.tipo_negocio || 'N/A' }}</p>
              </div>
            </div>

            <!-- Botones de Acción -->
            <div class="mt-8 pt-6 border-t border-slate-700 flex flex-wrap gap-3 justify-end">
              <template v-if="editMode">
                <button @click="editMode = false" class="px-5 py-2.5 rounded-xl font-medium bg-slate-800 text-slate-300 hover:bg-slate-700 transition">
                  Cancelar
                </button>
                <button @click="saveClient" :disabled="saving" class="px-5 py-2.5 rounded-xl font-medium bg-violet-600 text-white hover:bg-violet-500 transition flex items-center disabled:opacity-50">
                  <Loader2 v-if="saving" class="w-4 h-4 mr-2 animate-spin" />
                  <Save v-else class="w-4 h-4 mr-2" />
                  Guardar Cambios
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

          <!-- Pestaña Historial de Pedidos -->
          <div v-if="activeTab === 'pedidos'" class="space-y-4 min-h-[300px]">
            <div v-if="loadingPedidos" class="flex justify-center items-center h-40">
              <Loader2 class="w-8 h-8 text-violet-500 animate-spin" />
            </div>
            <div v-else-if="historialPedidos.length === 0" class="text-center py-12 bg-slate-800/30 rounded-2xl border border-slate-700/50">
              <Store class="mx-auto h-10 w-10 text-slate-500 mb-3" />
              <h3 class="text-lg font-medium text-slate-300">Sin pedidos</h3>
              <p class="text-slate-500 text-sm">Este cliente aún no tiene pedidos registrados.</p>
            </div>
            <div v-else class="space-y-3">
              <div v-for="pedido in historialPedidos" :key="pedido.id" class="flex items-center justify-between p-4 bg-slate-800/50 rounded-xl border border-slate-700/50 hover:bg-slate-800 transition">
                <div>
                  <div class="flex items-center gap-2 mb-1">
                    <span class="text-slate-200 font-bold">#{{ pedido.id }}</span>
                    <span 
                      :class="{
                        'bg-yellow-500/20 text-yellow-400 border-yellow-500/30': pedido.estado === 'Pendiente',
                        'bg-green-500/20 text-green-400 border-green-500/30': pedido.estado === 'Entregado',
                        'bg-slate-500/20 text-slate-400 border-slate-500/30': pedido.estado !== 'Pendiente' && pedido.estado !== 'Entregado'
                      }" 
                      class="text-xs px-2 py-0.5 rounded border"
                    >
                      {{ pedido.estado }}
                    </span>
                  </div>
                  <p class="text-sm text-slate-400">{{ new Date(pedido.fecha).toLocaleString() }}</p>
                </div>
                <div class="text-right">
                  <p class="text-lg font-bold text-emerald-400">
                    {{ new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP' }).format(pedido.total) }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal de Confirmación de Eliminación -->
    <div v-if="showDeleteConfirm" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-slate-950/40 backdrop-blur-md" @click="showDeleteConfirm = false"></div>
      <div class="relative bg-slate-900 border border-slate-700/50 rounded-3xl p-8 max-w-md w-full shadow-2xl transform transition-all scale-100">
        <div class="flex flex-col items-center text-center">
          <div class="w-16 h-16 bg-red-500/10 rounded-full flex items-center justify-center mb-6">
            <AlertTriangle class="w-8 h-8 text-red-500" />
          </div>
          <h3 class="text-xl font-bold text-white mb-2">¿Eliminar cliente?</h3>
          <p class="text-slate-400 mb-8">¿Estás seguro de que deseas eliminar a <strong>{{ selectedCliente?.nombre_cliente }}</strong>? Esta acción no se puede deshacer.</p>
          
          <div class="flex flex-col sm:flex-row gap-3 w-full">
            <button 
              @click="showDeleteConfirm = false" 
              class="flex-1 px-6 py-3 rounded-2xl font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition-colors"
            >
              Cancelar
            </button>
            <button 
              @click="handleDelete" 
              :disabled="isDeleting"
              class="flex-1 px-6 py-3 rounded-2xl font-semibold bg-red-600 text-white hover:bg-red-500 transition-colors flex items-center justify-center disabled:opacity-50"
            >
              <Loader2 v-if="isDeleting" class="w-5 h-5 animate-spin mr-2" />
              {{ isDeleting ? 'Eliminando...' : 'Sí, eliminar' }}
            </button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ArrowLeft, Search, Loader2, Users, MapPin, Phone, Store, User, UserPlus, Plus, X, Edit, Trash2, Save, AlertTriangle } from 'lucide-vue-next'
import api from '../services/api'

const clientes = ref([])
const searchQuery = ref('')
const loading = ref(false)
let searchTimeout = null

// Opciones dinámicas de la base de datos
const opcionesUbicacion = ref([])
const opcionesTipoNegocio = ref([])

// Modal state
const showModal = ref(false)
const editMode = ref(false)
const createMode = ref(false)
const showDeleteConfirm = ref(false)
const isDeleting = ref(false)
const activeTab = ref('detalles') // 'detalles' o 'pedidos'
const selectedCliente = ref(null)
const formData = ref({
  nombre_cliente: '',
  cc_o_nit: '',
  direccion: '',
  barrio_poblacion: '',
  ubicacion: '',
  contacto_comercial: '',
  telefono: '',
  correo_electronico: '',
  nombre_negocio: '',
  dias_visita: '',
  tipo_negocio: ''
})
const saving = ref(false)

// Historial state
const historialPedidos = ref([])
const loadingPedidos = ref(false)

const fetchClientes = async () => {
  loading.value = true
  try {
    const params = {}
    if (searchQuery.value.trim() !== '') {
      params.search = searchQuery.value.trim()
    }
    const response = await api.get('/clientes', { params })
    clientes.value = response.data
  } catch (error) {
    console.error("Error al obtener clientes:", error)
  } finally {
    loading.value = false
  }
}

const fetchOpciones = async () => {
  try {
    const response = await api.get('/clientes/opciones')
    opcionesUbicacion.value = response.data.ubicaciones
    opcionesTipoNegocio.value = response.data.tipos_negocio
  } catch (error) {
    console.error("Error al obtener opciones:", error)
  }
}

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    fetchClientes()
  }, 400)
}

const openCreateModal = () => {
  selectedCliente.value = null
  createMode.value = true
  editMode.value = true
  activeTab.value = 'detalles'
  formData.value = {
    nombre_cliente: '',
    cc_o_nit: '',
    direccion: '',
    barrio_poblacion: '',
    ubicacion: '',
    contacto_comercial: '',
    telefono: '',
    correo_electronico: '',
    nombre_negocio: '',
    dias_visita: '',
    tipo_negocio: ''
  }
  showModal.value = true
}

const fetchPedidos = async (clienteId) => {
  loadingPedidos.value = true
  try {
    const response = await api.get(`/clientes/${clienteId}/pedidos`)
    historialPedidos.value = response.data
  } catch (error) {
    console.error("Error al obtener pedidos:", error)
  } finally {
    loadingPedidos.value = false
  }
}

const openClientDetails = (cliente) => {
  selectedCliente.value = cliente
  formData.value = { ...cliente } // Clonar para editar
  createMode.value = false
  editMode.value = false
  activeTab.value = 'detalles'
  showModal.value = true
}

import { watch } from 'vue'

watch(activeTab, (newTab) => {
  if (newTab === 'pedidos' && selectedCliente.value) {
    fetchPedidos(selectedCliente.value.id)
  }
})

const closeModal = () => {
  showModal.value = false
  selectedCliente.value = null
  editMode.value = false
  createMode.value = false
  activeTab.value = 'detalles'
  historialPedidos.value = []
}

const saveClient = async () => {
  // Validaciones mínimas
  if (!formData.value.nombre_cliente || !formData.value.cc_o_nit) {
    alert("El Nombre Completo y el CC/NIT son obligatorios.")
    return
  }
  
  saving.value = true
  try {
    if (createMode.value) {
      // Crear nuevo cliente
      const response = await api.post('/clientes', formData.value)
      clientes.value.unshift(response.data) // Agregar al inicio de la lista
      
      // Pasar a modo vista del cliente creado
      selectedCliente.value = response.data
      createMode.value = false
      editMode.value = false
    } else {
      // Actualizar cliente existente
      const response = await api.put(`/clientes/${selectedCliente.value.id}`, formData.value)
      
      const index = clientes.value.findIndex(c => c.id === selectedCliente.value.id)
      if (index !== -1) {
        clientes.value[index] = response.data
      }
      
      selectedCliente.value = response.data
      editMode.value = false
    }
  } catch (error) {
    console.error("Error al guardar:", error)
    alert("Hubo un error al guardar los cambios.")
  } finally {
    saving.value = false
  }
}

const confirmDelete = () => {
  showDeleteConfirm.value = true
}

const handleDelete = async () => {
  isDeleting.value = true
  try {
    await api.delete(`/clientes/${selectedCliente.value.id}`)
    clientes.value = clientes.value.filter(c => c.id !== selectedCliente.value.id)
    showDeleteConfirm.value = false
    closeModal()
  } catch (error) {
    console.error("Error al eliminar:", error)
    alert("Hubo un error al eliminar el cliente.")
  } finally {
    isDeleting.value = false
  }
}

onMounted(() => {
  fetchOpciones()
  fetchClientes()
})
</script>
