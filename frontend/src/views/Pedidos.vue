<template>
  <div class="min-h-screen bg-[#0f172a] text-white p-6 md:p-12 relative">
    <!-- Header -->
    <header class="mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div class="flex items-center gap-4">
        <router-link to="/" class="p-2 bg-slate-800 rounded-xl hover:bg-slate-700 transition-colors text-slate-400 hover:text-white">
          <ArrowLeft class="w-6 h-6" />
        </router-link>
        <div>
          <h1 class="text-3xl md:text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-indigo-400">
            Pedidos
          </h1>
          <p class="text-slate-400 text-sm mt-1">Gestión de órdenes y facturación</p>
        </div>
      </div>
      
      <div class="flex flex-col md:flex-row items-center gap-4 w-full md:w-auto">
        <!-- Input de búsqueda (Visual para consistencia) -->
        <div class="relative w-full md:w-80">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search class="h-5 w-5 text-slate-500" />
          </div>
          <input 
            v-model="searchQuery" 
            type="text" 
            class="block w-full pl-10 pr-3 py-3 border border-slate-700 rounded-2xl leading-5 bg-slate-800/50 text-slate-300 placeholder-slate-500 focus:outline-none focus:bg-slate-800 focus:border-violet-500 focus:ring-1 focus:ring-violet-500 transition-all sm:text-sm backdrop-blur-sm" 
            placeholder="Buscar por cliente o negocio..." 
          />
        </div>

        <button @click="exportarPedidos" :disabled="isExporting" class="w-full md:w-auto px-5 py-3 rounded-2xl font-semibold bg-emerald-600 text-white hover:bg-emerald-500 transition-colors flex items-center justify-center shadow-lg shadow-emerald-600/20 active:scale-95 disabled:opacity-50">
          <Loader2 v-if="isExporting" class="w-5 h-5 mr-2 animate-spin" />
          <Download v-else class="w-5 h-5 mr-2" /> Exportar Pedidos
        </button>
        <button @click="openModal()" class="w-full md:w-auto px-5 py-3 rounded-2xl font-semibold bg-violet-600 text-white hover:bg-violet-500 transition-colors flex items-center justify-center shadow-lg shadow-violet-600/20 active:scale-95">
          <Plus class="w-5 h-5 mr-2" /> Nuevo Pedido
        </button>
      </div>
    </header>

    <!-- Lista de Pedidos -->
    <div v-if="pedidos.length === 0 && !loading" class="text-center py-20 bg-slate-800/30 rounded-3xl border border-slate-700/50 backdrop-blur-sm">
      <ShoppingCart class="mx-auto h-12 w-12 text-slate-500 mb-4" />
      <h3 class="text-lg font-medium text-slate-300">No hay pedidos registrados</h3>
      <p class="text-slate-500 mt-1">Crea un nuevo pedido para empezar.</p>
    </div>

    <!-- No se encontraron resultados en la búsqueda -->
    <div v-else-if="filteredPedidos.length === 0 && searchQuery" class="text-center py-20 bg-slate-800/30 rounded-3xl border border-slate-700/50 backdrop-blur-sm">
      <Search class="mx-auto h-12 w-12 text-slate-500 mb-4" />
      <h3 class="text-lg font-medium text-slate-300">No se encontraron pedidos</h3>
      <p class="text-slate-500 mt-1">No hay resultados para "{{ searchQuery }}". Intenta con otro nombre o negocio.</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div 
        v-for="pedido in filteredPedidos" 
        :key="pedido.id" 
        @click="openDetailModal(pedido)"
        class="bg-slate-800/40 border border-slate-700/50 rounded-2xl p-6 hover:border-violet-500/50 hover:bg-slate-800 transition-all cursor-pointer backdrop-blur-sm relative overflow-hidden group shadow-lg flex flex-col justify-between"
      >
        <div class="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-violet-500 to-indigo-500 opacity-0 group-hover:opacity-100 transition-opacity"></div>
        
        <div>
          <div class="flex items-start justify-between mb-4 gap-3">
            <div class="min-w-0 flex-1">
              <h3 class="text-xl font-bold text-slate-100 leading-snug break-words">
                {{ pedido.nombre_negocio || pedido.cliente_nombre }}
              </h3>
              <p v-if="pedido.nombre_negocio" class="text-sm text-indigo-400 font-medium mt-1">
                {{ pedido.cliente_nombre }}
              </p>
            </div>
            <span :class="['inline-flex items-center px-2.5 py-1 rounded-md text-xs font-semibold flex-shrink-0', getEstadoColor(pedido)]">
              {{ getEstadoDisplay(pedido) }}
            </span>
          </div>

          <div class="space-y-2 mt-4 text-sm text-slate-300">
            <div class="flex items-center gap-2">
              <Calendar class="w-4 h-4 text-slate-500" />
              <span>Creado: {{ new Date(pedido.fecha).toLocaleDateString() }}</span>
            </div>
            <div class="flex items-center gap-2">
              <Truck class="w-4 h-4 text-slate-500" />
              <span>Entrega: {{ pedido.fecha_entrega ? new Date(pedido.fecha_entrega).toLocaleDateString() : 'No definida' }}</span>
            </div>
          </div>
        </div>

        <div class="mt-6 pt-4 border-t border-slate-700/50 flex items-center justify-between">
          <span class="text-slate-400 font-medium text-sm">Total</span>
          <span class="text-2xl font-bold text-violet-400">
            {{ formatCurrency(pedido.total) }}
          </span>
        </div>
      </div>
    </div>

    <!-- Modal Nuevo Pedido -->
    <div v-if="showModal" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:p-0">
        
        <div class="fixed inset-0 transition-opacity bg-slate-900/80 backdrop-blur-sm" @click="closeModal"></div>

        <div class="relative inline-block w-full max-w-5xl text-left align-middle transition-all transform bg-slate-900 border border-slate-700 rounded-3xl shadow-2xl overflow-hidden mt-10 mb-10">
          
          <div class="p-6 md:p-8">
            <div class="flex justify-between items-center mb-6 border-b border-slate-800 pb-4">
              <h2 class="text-2xl font-bold text-white flex items-center gap-3">
                <ShoppingCart class="text-violet-400 w-7 h-7" />
                {{ editMode ? 'Editar Pedido' : 'Crear Nuevo Pedido' }}
              </h2>
              <button @click="closeModal" class="text-slate-400 hover:text-white p-2 rounded-full hover:bg-slate-800 transition">
                <X class="w-6 h-6" />
              </button>
            </div>

            <div class="space-y-6">
              <!-- Información General -->
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="relative">
                  <label class="block text-sm font-medium text-slate-400 mb-1">Buscar Cliente <span class="text-red-400">*</span></label>
                  <div class="relative">
                    <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                    <input 
                      v-model="clientSearchQuery"
                      @focus="showClientDropdown = true"
                      @blur="() => setTimeout(() => showClientDropdown = false, 200)"
                      type="text"
                      placeholder="Escribe el nombre del negocio o cliente..."
                      class="w-full bg-slate-800 border border-slate-700 rounded-lg pl-10 pr-4 py-2 text-white focus:border-violet-500 outline-none transition-all"
                    />
                  </div>

                  <!-- Dropdown de búsqueda -->
                  <div v-if="showClientDropdown && filteredClientesForSelect.length > 0" class="absolute z-[60] w-full mt-1 bg-slate-900 border border-slate-700 rounded-xl shadow-2xl max-h-60 overflow-y-auto custom-scrollbar">
                    <div 
                      v-for="cliente in filteredClientesForSelect" 
                      :key="cliente.id"
                      @click="selectCliente(cliente)"
                      class="p-3 hover:bg-violet-600/20 cursor-pointer border-b border-slate-800 last:border-none transition-colors group"
                    >
                      <p class="font-bold text-slate-200 group-hover:text-white">{{ cliente.nombre_negocio || cliente.nombre_cliente }}</p>
                      <p v-if="cliente.nombre_negocio" class="text-xs text-slate-500 group-hover:text-violet-300">{{ cliente.nombre_cliente }}</p>
                    </div>
                  </div>

                  <!-- No hay resultados -->
                  <div v-if="showClientDropdown && clientSearchQuery && filteredClientesForSelect.length === 0" class="absolute z-[60] w-full mt-1 bg-slate-900 border border-slate-700 rounded-xl p-4 text-center text-slate-500 text-sm">
                    No se encontraron clientes con ese nombre
                  </div>

                  <div v-if="selectedClienteInfo" class="mt-3 p-3 bg-slate-800/50 border border-slate-700/80 rounded-lg text-sm text-slate-300 space-y-1">
                    <p><strong class="text-slate-400 font-medium">Negocio:</strong> {{ selectedClienteInfo.nombre_negocio || 'No registrado' }}</p>
                    <p><strong class="text-slate-400 font-medium">NIT/CC:</strong> {{ selectedClienteInfo.cc_o_nit || 'No registrado' }}</p>
                    <p><strong class="text-slate-400 font-medium">Teléfono:</strong> {{ selectedClienteInfo.telefono || 'No registrado' }}</p>
                    <p><strong class="text-slate-400 font-medium">Dirección:</strong> {{ selectedClienteInfo.direccion || 'No registrada' }}</p>
                    <p><strong class="text-slate-400 font-medium">Barrio:</strong> {{ selectedClienteInfo.barrio_poblacion || 'No registrado' }}</p>
                  </div>
                </div>
                <div>
                  <label class="block text-sm font-medium text-slate-400 mb-1">Fecha a Entregar <span class="text-red-400">*</span></label>
                  <input v-model="formData.fecha_entrega" type="date" class="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:border-violet-500 outline-none" style="color-scheme: dark;" required />
                </div>
              </div>

              <!-- Lista de Productos (Items) -->
              <div class="mt-8 border border-slate-700 rounded-xl overflow-hidden bg-slate-800/20">
                <div class="bg-slate-800/80 px-4 py-3 border-b border-slate-700">
                  <h3 class="text-lg font-semibold text-slate-200">Productos del Pedido</h3>
                </div>

                <div class="p-4 space-y-4">
                  <!-- Cabeceras (solo en desktop) -->
                  <div class="hidden md:grid grid-cols-12 gap-3 text-xs font-semibold text-slate-400 uppercase tracking-wider px-2">
                    <div class="col-span-3">Producto</div>
                    <div class="col-span-1 text-center">Cant.</div>
                    <div class="col-span-2 text-center">Precio</div>
                    <div class="col-span-3 text-center">Observaciones</div>
                    <div class="col-span-2 text-right">Subtotal</div>
                    <div class="col-span-1"></div>
                  </div>

                  <!-- Filas -->
                  <div v-for="(item, index) in formData.items" :key="index" class="grid grid-cols-1 md:grid-cols-12 gap-3 items-start bg-slate-800/50 p-3 md:p-2 rounded-lg md:bg-transparent border border-slate-700 md:border-none relative group transition-all">
                    
                    <div class="col-span-1 md:col-span-3">
                      <label class="md:hidden block text-xs text-slate-400 mb-1">Producto</label>
                      <select v-model="item.producto_id" @change="() => fetchSuggestedPrice(index)" class="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:border-violet-500 outline-none">
                        <option value="" disabled>Selecciona producto</option>
                        <option v-for="prod in productos" :key="prod.id" :value="prod.id">
                          {{ prod.nombre }}
                        </option>
                      </select>
                    </div>
                    
                    <div class="col-span-1 md:col-span-1">
                      <label class="md:hidden block text-xs text-slate-400 mb-1">Cant.</label>
                      <input v-model="item.cantidad" type="number" min="1" class="w-full bg-slate-800 border border-slate-700 rounded-lg px-1.5 py-2 text-sm text-center text-white focus:border-violet-500 outline-none" />
                    </div>
                    
                    <div class="col-span-1 md:col-span-2">
                      <label class="md:hidden block text-xs text-slate-400 mb-1">Precio Unitario</label>
                      <div class="relative">
                        <input v-model="item.precio_unitario" type="number" step="0.01" class="w-full bg-slate-800 border border-slate-700 rounded-lg px-2 py-2 text-sm text-center text-white focus:border-violet-500 outline-none" />
                        <div v-if="item.loadingPrice" class="absolute right-2 top-2">
                          <Loader2 class="w-3 h-3 text-violet-500 animate-spin" />
                        </div>
                      </div>
                      <div class="min-h-[16px] mt-1">
                        <p v-if="item.origen === 'historial'" class="text-[10px] text-purple-400 font-medium italic flex items-center leading-none">
                          <History class="w-2.5 h-2.5 mr-1"/> Historial
                        </p>
                        <p v-if="item.origen === 'base'" class="text-[10px] text-emerald-400 font-medium italic flex items-center leading-none">
                          <Tag class="w-2.5 h-2.5 mr-1"/> Precio Base
                        </p>
                      </div>
                    </div>

                    <div class="col-span-1 md:col-span-3">
                      <label class="md:hidden block text-xs text-slate-400 mb-1">Observaciones</label>
                      <input 
                        v-model="item.observaciones" 
                        type="text" 
                        placeholder="Nota..." 
                        class="w-full bg-slate-800/80 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-300 focus:border-violet-500 outline-none placeholder:text-slate-600" 
                      />
                    </div>

                    <div class="col-span-1 md:col-span-2 flex items-center md:h-[38px]">
                      <label class="md:hidden block text-xs text-slate-400 mr-2">Subtotal:</label>
                      <span class="text-sm font-semibold text-slate-200">
                        {{ formatCurrency(item.cantidad * item.precio_unitario) }}
                      </span>
                    </div>

                    <div class="col-span-1 md:col-span-1 flex items-center justify-end md:justify-center md:h-[38px] absolute top-2 right-2 md:relative md:top-auto md:right-auto">
                      <button @click="removeItem(index)" class="text-slate-500 hover:text-red-400 transition p-1 bg-slate-800 rounded-md">
                        <Trash2 class="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  <div v-if="formData.items.length === 0" class="text-center py-6 text-slate-500 text-sm">
                    No hay productos en el pedido. Haz clic en "Añadir producto".
                  </div>
                </div>

                <!-- Total Row -->
                <!-- Botón Añadir -->
                <div class="p-4 border-t border-slate-700/50">
                  <button @click="addItem" class="text-sm font-medium text-violet-400 hover:text-violet-300 flex items-center transition bg-violet-500/10 hover:bg-violet-500/20 px-4 py-2.5 rounded-xl w-full justify-center border border-violet-500/20">
                    <Plus class="w-4 h-4 mr-1" /> Añadir producto
                  </button>
                </div>

                <!-- Total Row -->
                <div class="bg-slate-800/80 p-4 border-t border-slate-700 flex justify-between items-center">
                  <span class="text-slate-400 font-medium uppercase text-xs tracking-wider">Total del Pedido</span>
                  <span class="text-2xl font-black text-violet-400 bg-violet-500/10 px-4 py-1.5 rounded-xl border border-violet-500/20 shadow-inner">
                    {{ formatCurrency(computedTotal) }}
                  </span>
                </div>
              </div>

              <!-- Botones de Acción Formulario -->
              <div class="mt-8 pt-6 border-t border-slate-700 flex flex-wrap gap-3 justify-end">
                <button @click="closeModal" class="px-5 py-2.5 rounded-xl font-medium bg-slate-800 text-slate-300 hover:bg-slate-700 transition">
                  Cancelar
                </button>
                <button @click="savePedido" :disabled="saving || formData.items.length === 0 || !formData.cliente_id || !formData.fecha_entrega" class="px-5 py-2.5 rounded-xl font-medium bg-violet-600 text-white hover:bg-violet-500 transition flex items-center disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-violet-600/20">
                  <Loader2 v-if="saving" class="w-4 h-4 mr-2 animate-spin" />
                  <Save v-else class="w-4 h-4 mr-2" />
                  {{ editMode ? 'Guardar Cambios' : 'Guardar Pedido' }}
                </button>
              </div>

            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal Detalles del Pedido -->
    <div v-if="showDetailModal" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:p-0">
        <div class="fixed inset-0 transition-opacity bg-slate-900/80 backdrop-blur-sm" @click="closeDetailModal"></div>
        <div class="relative inline-block w-full max-w-4xl text-left align-middle transition-all transform bg-slate-900 border border-slate-700 rounded-3xl shadow-2xl overflow-hidden mt-10 mb-10">
          <div class="p-6 md:p-8">
            <div v-if="loadingDetail" class="flex flex-col items-center py-12">
              <Loader2 class="w-10 h-10 text-violet-500 animate-spin mb-4" />
              <p class="text-slate-400">Cargando detalles...</p>
            </div>
            <div v-else-if="selectedPedidoDetail">
              <div class="flex justify-between items-start mb-6 gap-4">
                <div class="min-w-0">
                  <h2 class="text-xl md:text-2xl font-bold text-white mb-1 truncate">
                    {{ selectedPedidoDetail.nombre_negocio || selectedPedidoDetail.cliente_nombre }}
                  </h2>
                  <p class="text-sm text-slate-400 flex items-center gap-2">
                    <History class="w-4 h-4 flex-shrink-0" /> Pedido #{{ selectedPedidoDetail.id }}
                  </p>
                </div>
                <button @click="closeDetailModal" class="text-slate-400 hover:text-white p-2 rounded-full hover:bg-slate-800 transition flex-shrink-0">
                  <X class="w-6 h-6" />
                </button>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
                <div class="p-4 bg-slate-800/50 rounded-2xl border border-slate-700/50">
                  <p class="text-xs text-slate-500 uppercase font-bold mb-1">Cliente</p>
                  <p class="text-slate-200 font-medium truncate">{{ selectedPedidoDetail.cliente_nombre }}</p>
                </div>
                <div class="p-4 bg-slate-800/50 rounded-2xl border border-slate-700/50">
                  <p class="text-xs text-slate-500 uppercase font-bold mb-1">Entrega</p>
                  <p class="text-slate-200 font-medium">{{ selectedPedidoDetail.fecha_entrega ? new Date(selectedPedidoDetail.fecha_entrega).toLocaleDateString() : 'No definida' }}</p>
                </div>
              </div>

              <div class="overflow-x-auto border border-slate-700/50 rounded-2xl mb-6 custom-scrollbar">
                <table class="w-full text-left text-sm min-w-[500px]">
                  <thead class="bg-slate-800/80 text-slate-400 uppercase text-xs">
                    <tr>
                      <th class="px-4 py-3 font-semibold">Producto</th>
                      <th class="px-4 py-3 font-semibold text-center">Cantidad</th>
                      <th class="px-4 py-3 font-semibold text-right">Precio</th>
                      <th class="px-4 py-3 font-semibold text-right">Total</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-slate-700/50 text-slate-300">
                    <tr v-for="item in selectedPedidoDetail.items" :key="item.id">
                      <td class="px-4 py-3">
                        <div class="font-medium">{{ item.producto_nombre }}</div>
                        <div v-if="item.observaciones" class="text-xs text-violet-400/80 mt-0.5 flex items-start gap-1">
                          <Tag class="w-3 h-3 mt-0.5 flex-shrink-0" />
                          {{ item.observaciones }}
                        </div>
                      </td>
                      <td class="px-4 py-3 text-center">{{ item.cantidad }}</td>
                      <td class="px-4 py-3 text-right">{{ formatCurrency(item.precio_unitario) }}</td>
                      <td class="px-4 py-3 text-right font-medium text-white">{{ formatCurrency(item.cantidad * item.precio_unitario) }}</td>
                    </tr>
                  </tbody>
                  <tfoot>
                    <tr class="bg-slate-800/30">
                      <td colspan="3" class="px-4 py-4 text-right font-bold text-slate-400">Total Pedido</td>
                      <td class="px-4 py-4 text-right font-bold text-violet-400 text-lg">{{ formatCurrency(selectedPedidoDetail.total) }}</td>
                    </tr>
                  </tfoot>
                </table>
              </div>

              <div class="flex flex-col md:flex-row justify-end gap-3 pt-6 border-t border-slate-700/50">
                <button @click="confirmDelete" class="px-5 py-2.5 rounded-xl font-medium bg-red-500/10 text-red-400 hover:bg-red-500 hover:text-white transition flex items-center justify-center order-3 md:order-1">
                  <Trash2 class="w-4 h-4 mr-2" />
                  Eliminar
                </button>
                <button @click="enterEditMode" class="px-5 py-2.5 rounded-xl font-medium bg-slate-800 text-slate-300 hover:bg-slate-700 transition flex items-center justify-center order-2">
                  <Edit class="w-4 h-4 mr-2" />
                  Editar
                </button>
                <button @click="closeDetailModal" class="px-6 py-2.5 rounded-xl font-medium bg-violet-600 text-white hover:bg-violet-500 transition justify-center order-1 md:order-3">
                  Cerrar
                </button>
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
          <h3 class="text-xl font-bold text-white mb-2">¿Confirmar eliminación?</h3>
          <p class="text-slate-400 mb-8">Esta acción eliminará permanentemente el pedido y todos sus items. No se puede deshacer.</p>
          
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
import { ref, computed, onMounted } from 'vue'
import { ArrowLeft, ShoppingCart, Plus, X, Trash2, Edit, Save, Loader2, Calendar, Truck, History, Tag, Search, Download, AlertTriangle } from 'lucide-vue-next'
import api from '../services/api'

// States
const pedidos = ref([])
const clientes = ref([])
const productos = ref([])
const loading = ref(false)
const isExporting = ref(false)
const showModal = ref(false)
const showDeleteConfirm = ref(false)
const saving = ref(false)
const isDeleting = ref(false)
const searchQuery = ref('')
const showDetailModal = ref(false)
const selectedPedidoDetail = ref(null)
const loadingDetail = ref(false)
const editMode = ref(false)
const editingPedidoId = ref(null)

// Búsqueda de clientes en modal
const clientSearchQuery = ref('')
const showClientDropdown = ref(false)

const formData = ref({
  cliente_id: '',
  fecha_entrega: '',
  items: []
})

// Format helpers
const formatCurrency = (value) => {
  return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP' }).format(value || 0)
}

const getEstadoDisplay = (pedido) => {
  if (!pedido.fecha_entrega) return 'Pendiente'
  
  const hoy = new Date()
  hoy.setHours(0, 0, 0, 0)
  
  const fechaEntrega = new Date(pedido.fecha_entrega)
  fechaEntrega.setHours(0, 0, 0, 0)
  
  if (fechaEntrega < hoy) {
    return 'Remitido'
  }
  return 'Pendiente'
}

const getEstadoColor = (pedido) => {
  const estado = getEstadoDisplay(pedido)
  if (estado === 'Remitido') {
    return 'bg-emerald-500/20 text-emerald-400' // Verde dinero
  }
  return 'bg-amber-500/20 text-amber-400' // Amarillo
}

// Computeds
const computedTotal = computed(() => {
  return formData.value.items.reduce((sum, item) => sum + (item.cantidad * item.precio_unitario), 0)
})

const filteredPedidos = computed(() => {
  if (!searchQuery.value) return pedidos.value
  const q = searchQuery.value.toLowerCase()
  return pedidos.value.filter(p => 
    (p.cliente_nombre && p.cliente_nombre.toLowerCase().includes(q)) || 
    (p.nombre_negocio && p.nombre_negocio.toLowerCase().includes(q))
  )
})

const filteredClientesForSelect = computed(() => {
  if (!clientSearchQuery.value) return clientes.value
  const q = clientSearchQuery.value.toLowerCase()
  return clientes.value.filter(c => 
    (c.nombre_cliente && c.nombre_cliente.toLowerCase().includes(q)) || 
    (c.nombre_negocio && c.nombre_negocio.toLowerCase().includes(q))
  )
})

const selectedClienteInfo = computed(() => {
  if (!formData.value.cliente_id) return null
  return clientes.value.find(c => c.id === formData.value.cliente_id)
})

// Lifecycle
onMounted(() => {
  fetchPedidos()
  fetchClientes()
  fetchProductos()
})

// Fetches
const fetchPedidos = async () => {
  loading.value = true
  try {
    const response = await api.get('/pedidos')
    pedidos.value = response.data
  } catch (error) {
    console.error("Error al obtener pedidos:", error)
  } finally {
    loading.value = false
  }
}

const exportarPedidos = async () => {
  isExporting.value = true
  try {
    const response = await api.get('/pedidos/exportar', {
      responseType: 'blob'
    })
    
    const contentDisposition = response.headers['content-disposition']
    let filename = 'pedidos Jose Caro.xlsx'
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/)
      if (filenameMatch && filenameMatch.length >= 2)
        filename = filenameMatch[1]
    }
    
    const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error("Error al exportar pedidos:", error)
    alert("Hubo un error al exportar los pedidos.")
  } finally {
    isExporting.value = false
  }
}

const openDetailModal = async (pedido) => {
  showDetailModal.value = true
  loadingDetail.value = true
  try {
    const response = await api.get(`/pedidos/${pedido.id}`)
    selectedPedidoDetail.value = response.data
  } catch (error) {
    console.error("Error al obtener detalle:", error)
    showDetailModal.value = false
  } finally {
    loadingDetail.value = false
  }
}

const closeDetailModal = () => {
  showDetailModal.value = false
  selectedPedidoDetail.value = null
}

const fetchClientes = async () => {
  try {
    const response = await api.get('/clientes')
    clientes.value = response.data
  } catch (error) {
    console.error("Error al obtener clientes:", error)
  }
}

const fetchProductos = async () => {
  try {
    const response = await api.get('/productos')
    productos.value = response.data
  } catch (error) {
    console.error("Error al obtener productos:", error)
  }
}

// Modal actions
const openModal = (pedido = null) => {
  if (pedido) {
    editMode.value = true
    editingPedidoId.value = pedido.id
    clientSearchQuery.value = pedido.nombre_negocio || pedido.cliente_nombre
    formData.value = {
      cliente_id: pedido.cliente_id,
      fecha_entrega: pedido.fecha_entrega ? pedido.fecha_entrega.split('T')[0] : '',
      items: pedido.items.map(item => ({
        producto_id: item.producto_id,
        cantidad: item.cantidad,
        precio_unitario: item.precio_unitario,
        observaciones: item.observaciones,
        origen: null,
        loadingPrice: false
      }))
    }
  } else {
    editMode.value = false
    editingPedidoId.value = null
    clientSearchQuery.value = ''
    formData.value = {
      cliente_id: '',
      fecha_entrega: '',
      items: [{ producto_id: '', cantidad: 1, precio_unitario: 0, observaciones: '', origen: null, loadingPrice: false }]
    }
  }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editMode.value = false
  editingPedidoId.value = null
  clientSearchQuery.value = ''
  showClientDropdown.value = false
}

const selectCliente = (cliente) => {
  formData.value.cliente_id = cliente.id
  clientSearchQuery.value = cliente.nombre_negocio || cliente.nombre_cliente
  showClientDropdown.value = false
  onClienteChange()
}

const enterEditMode = () => {
  if (!selectedPedidoDetail.value) return
  const pedido = selectedPedidoDetail.value
  closeDetailModal()
  openModal(pedido)
}

const confirmDelete = () => {
  if (!selectedPedidoDetail.value) return
  showDeleteConfirm.value = true
}

const handleDelete = async () => {
  if (!selectedPedidoDetail.value) return
  
  isDeleting.value = true
  try {
    await api.delete(`/pedidos/${selectedPedidoDetail.value.id}`)
    showDeleteConfirm.value = false
    closeDetailModal()
    fetchPedidos()
  } catch (error) {
    console.error("Error al eliminar pedido:", error)
    alert("Error al eliminar el pedido")
  } finally {
    isDeleting.value = false
  }
}

// Item actions
const addItem = () => {
  formData.value.items.push({ producto_id: '', cantidad: 1, precio_unitario: 0, observaciones: '', origen: null, loadingPrice: false })
}

const removeItem = (index) => {
  formData.value.items.splice(index, 1)
}

// Price Logic
const onClienteChange = () => {
  // If client changes, refetch prices for all selected products
  formData.value.items.forEach((item, index) => {
    if (item.producto_id) {
      fetchSuggestedPrice(index)
    }
  })
}

const fetchSuggestedPrice = async (index) => {
  const item = formData.value.items[index]
  if (!item.producto_id) return
  
  if (!formData.value.cliente_id) {
    // If no client selected, just fallback to base price
    const prod = productos.value.find(p => p.id === item.producto_id)
    if (prod) {
      item.precio_unitario = prod.precio
      item.origen = 'base'
    }
    return
  }

  item.loadingPrice = true
  item.origen = null
  try {
    const response = await api.get('/pedidos/sugerencia-precio', {
      params: {
        cliente_id: formData.value.cliente_id,
        producto_id: item.producto_id
      }
    })
    item.precio_unitario = response.data.precio
    item.origen = response.data.origen
  } catch (error) {
    console.error("Error al obtener precio sugerido:", error)
    // Fallback if error
    const prod = productos.value.find(p => p.id === item.producto_id)
    if (prod) {
      item.precio_unitario = prod.precio
      item.origen = 'base'
    }
  } finally {
    item.loadingPrice = false
  }
}

// Save logic
const savePedido = async () => {
  if (!formData.value.cliente_id) {
    alert("Debe seleccionar un cliente.")
    return
  }
  if (!formData.value.fecha_entrega) {
    alert("Debe seleccionar una fecha de entrega.")
    return
  }
  // Limpiar filas vacías automáticamente
  const itemsValidos = formData.value.items.filter(i => i.producto_id)

  if (itemsValidos.length === 0) {
    alert("El pedido debe tener al menos un producto seleccionado.")
    return
  }

  if (itemsValidos.some(i => i.cantidad <= 0 || i.precio_unitario < 0)) {
    alert("Por favor revise los productos. La cantidad y el precio deben ser mayores o iguales a cero.")
    return
  }

  saving.value = true
  try {
    const payload = {
      cliente_id: formData.value.cliente_id,
      fecha_entrega: formData.value.fecha_entrega ? new Date(formData.value.fecha_entrega).toISOString() : null,
      items: itemsValidos.map(i => ({
        producto_id: i.producto_id,
        cantidad: i.cantidad,
        precio_unitario: i.precio_unitario,
        observaciones: i.observaciones
      }))
    }
    
    if (editMode.value) {
      await api.put(`/pedidos/${editingPedidoId.value}`, payload)
    } else {
      await api.post('/pedidos', payload)
    }
    
    // Recargar lista
    await fetchPedidos()
    closeModal()
  } catch (error) {
    console.error("Error al guardar el pedido:", error)
    alert(error.response?.data?.detail || "Hubo un error al guardar el pedido.")
  } finally {
    saving.value = false
  }
}

</script>
