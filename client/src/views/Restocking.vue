<template>
  <div class="restocking-view">
    <div class="header">
      <h1>📦 Inventory Restocking</h1>
      <p class="subtitle">Optimize your inventory based on demand forecasts</p>
    </div>

    <!-- Budget Control Section -->
    <div class="budget-section card">
      <h2>💰 Available Budget</h2>
      <div class="budget-controls">
        <div class="slider-container">
          <input 
            type="range" 
            v-model.number="budget" 
            min="0" 
            max="100000" 
            step="1000"
            class="budget-slider"
            @input="debouncedGetRecommendations"
          />
          <div class="slider-labels">
            <span>$0</span>
            <span>$50K</span>
            <span>$100K</span>
          </div>
        </div>
        <div class="budget-display">
          <div class="budget-value">{{ formatCurrency(budget) }}</div>
          <div class="budget-label">Total Budget</div>
        </div>
      </div>
      
      <button 
        @click="getRecommendations" 
        class="btn btn-primary"
        :disabled="loading || budget === 0"
      >
        {{ loading ? 'Loading...' : 'Get Recommendations' }}
      </button>
    </div>

    <!-- Recommendations Section -->
    <div v-if="recommendations.length > 0" class="recommendations-section card">
      <div class="section-header">
        <h2>📋 Recommended Items</h2>
        <div class="summary">
          <span class="summary-item">
            <strong>{{ recommendations.length }}</strong> items
          </span>
          <span class="summary-item">
            <strong>{{ formatCurrency(totalCost) }}</strong> total cost
          </span>
          <span class="summary-item">
            <strong>{{ formatCurrency(budget - totalCost) }}</strong> remaining
          </span>
        </div>
      </div>

      <div class="table-container">
        <table class="recommendations-table">
          <thead>
            <tr>
              <th>
                <input 
                  type="checkbox" 
                  @change="toggleSelectAll" 
                  :checked="allSelected"
                />
              </th>
              <th>Priority</th>
              <th>Item</th>
              <th>SKU</th>
              <th>Current Stock</th>
              <th>Forecasted Demand</th>
              <th>Recommended Qty</th>
              <th>Unit Cost</th>
              <th>Total Cost</th>
              <th>Trend</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="item in recommendations" 
              :key="item.item_sku"
              :class="{ 'selected': selectedItems.has(item.item_sku) }"
            >
              <td>
                <input 
                  type="checkbox" 
                  :checked="selectedItems.has(item.item_sku)"
                  @change="toggleItem(item)"
                />
              </td>
              <td>
                <span 
                  class="priority-badge" 
                  :class="`priority-${item.priority.toLowerCase()}`"
                >
                  {{ item.priority }}
                </span>
              </td>
              <td class="item-name">{{ item.item_name }}</td>
              <td class="sku">{{ item.item_sku }}</td>
              <td>{{ item.current_stock }}</td>
              <td>{{ item.forecasted_demand }}</td>
              <td class="recommended-qty">{{ item.recommended_quantity }}</td>
              <td>{{ formatCurrency(item.unit_cost) }}</td>
              <td class="total-cost">{{ formatCurrency(item.total_cost) }}</td>
              <td>
                <span 
                  class="trend-badge" 
                  :class="`trend-${item.trend.toLowerCase()}`"
                >
                  {{ getTrendIcon(item.trend) }} {{ item.trend }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Order Actions -->
      <div class="order-actions">
        <div class="order-summary">
          <div class="summary-row">
            <span>Selected Items:</span>
            <strong>{{ selectedItems.size }}</strong>
          </div>
          <div class="summary-row">
            <span>Total Order Value:</span>
            <strong>{{ formatCurrency(selectedTotalCost) }}</strong>
          </div>
        </div>
        <button 
          @click="placeOrder" 
          class="btn btn-success btn-large"
          :disabled="selectedItems.size === 0 || placingOrder"
        >
          {{ placingOrder ? 'Placing Order...' : '✓ Place Restocking Order' }}
        </button>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!loading && budget > 0" class="empty-state card">
      <div class="empty-icon">📭</div>
      <h3>No Recommendations Available</h3>
      <p>Try increasing your budget or check back later for demand updates.</p>
    </div>

    <!-- Success Modal -->
    <div v-if="showSuccessModal" class="modal-overlay" @click="closeSuccessModal">
      <div class="modal-content success-modal" @click.stop>
        <div class="success-icon">✓</div>
        <h2>Order Placed Successfully!</h2>
        <div class="order-details">
          <p><strong>Order Number:</strong> {{ createdOrder.order_number }}</p>
          <p><strong>Total Value:</strong> {{ formatCurrency(createdOrder.total_value) }}</p>
          <p><strong>Items Ordered:</strong> {{ createdOrder.items.length }}</p>
          <p><strong>Expected Delivery:</strong> {{ formatDate(createdOrder.expected_delivery) }}</p>
          <p><strong>Lead Time:</strong> {{ createdOrder.delivery_lead_time_days }} days</p>
        </div>
        <div class="modal-actions">
          <button @click="closeSuccessModal" class="btn btn-primary">Close</button>
          <button @click="goToOrders" class="btn btn-secondary">View Orders</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'

export default {
  name: 'Restocking',
  setup() {
    const router = useRouter()
    
    // State
    const budget = ref(25000) // Default budget $25,000
    const recommendations = ref([])
    const selectedItems = ref(new Set())
    const loading = ref(false)
    const placingOrder = ref(false)
    const showSuccessModal = ref(false)
    const createdOrder = ref(null)

    // Debounce timer for slider
    let debounceTimer = null

    // Computed properties
    const totalCost = computed(() => {
      return recommendations.value.reduce((sum, item) => sum + item.total_cost, 0)
    })

    const selectedTotalCost = computed(() => {
      return recommendations.value
        .filter(item => selectedItems.value.has(item.item_sku))
        .reduce((sum, item) => sum + item.total_cost, 0)
    })

    const allSelected = computed(() => {
      return recommendations.value.length > 0 && 
             selectedItems.value.size === recommendations.value.length
    })

    // Methods
    const getRecommendations = async () => {
      if (budget.value === 0) return

      loading.value = true
      try {
        const data = await api.getRestockRecommendations(budget.value)
        recommendations.value = data
        
        // Auto-select high priority items
        selectedItems.value.clear()
        data.forEach(item => {
          if (item.priority === 'High') {
            selectedItems.value.add(item.item_sku)
          }
        })
      } catch (error) {
        console.error('Error fetching recommendations:', error)
        alert('Failed to load recommendations. Please try again.')
      } finally {
        loading.value = false
      }
    }

    const debouncedGetRecommendations = () => {
      clearTimeout(debounceTimer)
      debounceTimer = setTimeout(() => {
        getRecommendations()
      }, 500)
    }

    const toggleItem = (item) => {
      if (selectedItems.value.has(item.item_sku)) {
        selectedItems.value.delete(item.item_sku)
      } else {
        selectedItems.value.add(item.item_sku)
      }
      // Trigger reactivity by creating new Set
      selectedItems.value = new Set(selectedItems.value)
    }

    const toggleSelectAll = () => {
      if (allSelected.value) {
        selectedItems.value.clear()
      } else {
        recommendations.value.forEach(item => {
          selectedItems.value.add(item.item_sku)
        })
      }
      selectedItems.value = new Set(selectedItems.value)
    }

    const placeOrder = async () => {
      if (selectedItems.value.size === 0) return

      // Prepare order items from selected recommendations
      const orderItems = recommendations.value
        .filter(item => selectedItems.value.has(item.item_sku))
        .map(item => ({
          sku: item.item_sku,
          quantity: item.recommended_quantity
        }))

      placingOrder.value = true
      try {
        const orderData = {
          items: orderItems,
          total_budget: budget.value,
          notes: `Restocking order based on demand forecast - ${new Date().toLocaleDateString()}`
        }

        const result = await api.createRestockOrder(orderData)
        createdOrder.value = result
        showSuccessModal.value = true

        // Reset state after successful order
        recommendations.value = []
        selectedItems.value.clear()
      } catch (error) {
        console.error('Error placing order:', error)
        alert('Failed to place order. Please try again.')
      } finally {
        placingOrder.value = false
      }
    }

    const closeSuccessModal = () => {
      showSuccessModal.value = false
      createdOrder.value = null
    }

    const goToOrders = () => {
      closeSuccessModal()
      router.push('/orders')
    }

    const formatCurrency = (value) => {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      }).format(value)
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    }

    const getTrendIcon = (trend) => {
      const icons = {
        'Increasing': '📈',
        'Stable': '➡️',
        'Decreasing': '📉'
      }
      return icons[trend] || '➡️'
    }

    // Load recommendations on mount with default budget
    onMounted(() => {
      getRecommendations()
    })

    return {
      budget,
      recommendations,
      selectedItems,
      loading,
      placingOrder,
      showSuccessModal,
      createdOrder,
      totalCost,
      selectedTotalCost,
      allSelected,
      getRecommendations,
      debouncedGetRecommendations,
      toggleItem,
      toggleSelectAll,
      placeOrder,
      closeSuccessModal,
      goToOrders,
      formatCurrency,
      formatDate,
      getTrendIcon
    }
  }
}
</script>

<style scoped>
.restocking-view {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.header {
  margin-bottom: 2rem;
}

.header h1 {
  font-size: 2rem;
  color: #0f172a;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #64748b;
  font-size: 1.1rem;
}

.card {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

/* Budget Section */
.budget-section h2 {
  color: #0f172a;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
}

.budget-controls {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 2rem;
  margin-bottom: 1.5rem;
  align-items: center;
}

.slider-container {
  flex: 1;
}

.budget-slider {
  width: 100%;
  height: 8px;
  border-radius: 4px;
  background: #e2e8f0;
  outline: none;
  -webkit-appearance: none;
  cursor: pointer;
}

.budget-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.budget-slider::-moz-range-thumb {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  border: none;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 0.5rem;
  color: #64748b;
  font-size: 0.875rem;
}

.budget-display {
  text-align: center;
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border-radius: 12px;
  color: white;
  min-width: 200px;
}

.budget-value {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 0.25rem;
}

.budget-label {
  font-size: 0.875rem;
  opacity: 0.9;
}

/* Recommendations Section */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-header h2 {
  color: #0f172a;
  font-size: 1.5rem;
}

.summary {
  display: flex;
  gap: 2rem;
}

.summary-item {
  color: #64748b;
}

.summary-item strong {
  color: #0f172a;
  margin-left: 0.5rem;
}

/* Table */
.table-container {
  overflow-x: auto;
  margin-bottom: 1.5rem;
}

.recommendations-table {
  width: 100%;
  border-collapse: collapse;
}

.recommendations-table th {
  background: #f8fafc;
  padding: 0.75rem;
  text-align: left;
  font-weight: 600;
  color: #475569;
  font-size: 0.875rem;
  border-bottom: 2px solid #e2e8f0;
}

.recommendations-table td {
  padding: 1rem 0.75rem;
  border-bottom: 1px solid #e2e8f0;
}

.recommendations-table tr:hover {
  background: #f8fafc;
}

.recommendations-table tr.selected {
  background: #eff6ff;
}

.item-name {
  font-weight: 500;
  color: #0f172a;
}

.sku {
  font-family: 'Courier New', monospace;
  color: #64748b;
  font-size: 0.875rem;
}

.recommended-qty {
  font-weight: 600;
  color: #3b82f6;
}

.total-cost {
  font-weight: 600;
  color: #0f172a;
}

.priority-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.priority-high {
  background: #fee2e2;
  color: #dc2626;
}

.priority-medium {
  background: #fef3c7;
  color: #d97706;
}

.priority-low {
  background: #e0e7ff;
  color: #4f46e5;
}

.trend-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.875rem;
  color: #64748b;
}

.trend-increasing {
  color: #059669;
}

.trend-decreasing {
  color: #dc2626;
}

/* Order Actions */
.order-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1.5rem;
  border-top: 2px solid #e2e8f0;
}

.order-summary {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.summary-row {
  display: flex;
  gap: 1rem;
  font-size: 1rem;
}

.summary-row strong {
  color: #0f172a;
  font-size: 1.125rem;
}

/* Buttons */
.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 1rem;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3);
}

.btn-success {
  background: #10b981;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #059669;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(16, 185, 129, 0.3);
}

.btn-secondary {
  background: #64748b;
  color: white;
}

.btn-secondary:hover {
  background: #475569;
}

.btn-large {
  padding: 1rem 2rem;
  font-size: 1.125rem;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-state h3 {
  color: #0f172a;
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: #64748b;
}

/* Success Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  max-width: 500px;
  width: 90%;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.success-modal {
  text-align: center;
}

.success-icon {
  width: 80px;
  height: 80px;
  background: #10b981;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3rem;
  margin: 0 auto 1.5rem;
}

.success-modal h2 {
  color: #0f172a;
  margin-bottom: 1.5rem;
}

.order-details {
  background: #f8fafc;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  text-align: left;
}

.order-details p {
  margin: 0.5rem 0;
  color: #64748b;
}

.order-details strong {
  color: #0f172a;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

/* Responsive */
@media (max-width: 768px) {
  .restocking-view {
    padding: 1rem;
  }

  .budget-controls {
    grid-template-columns: 1fr;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .summary {
    flex-direction: column;
    gap: 0.5rem;
  }

  .order-actions {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }

  .table-container {
    font-size: 0.875rem;
  }
}
</style>
