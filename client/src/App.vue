<template>
  <div class="app-container" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
    <!-- Sidebar Navigation -->
    <Sidebar 
      :nav-items="navigationItems"
      @toggle-sidebar="handleSidebarToggle"
      @toggle-theme="handleThemeToggle"
    />

    <!-- Main Content Area -->
    <div class="main-wrapper">
      <!-- Top Bar -->
      <header class="top-bar">
        <div class="top-bar-left">
          <h1 class="page-title">{{ pageTitle }}</h1>
        </div>
        <div class="top-bar-right">
          <FilterBar v-if="showFilters" />
          <LanguageSwitcher />
          <ProfileMenu
            @show-profile-details="showProfileDetails = true"
            @show-tasks="showTasks = true"
          />
        </div>
      </header>

      <!-- Page Content -->
      <main class="main-content">
        <router-view />
      </main>
    </div>

    <!-- Modals -->
    <ProfileDetailsModal
      :is-open="showProfileDetails"
      @close="showProfileDetails = false"
    />

    <TasksModal
      :is-open="showTasks"
      :tasks="tasks"
      @close="showTasks = false"
      @add-task="addTask"
      @delete-task="deleteTask"
      @toggle-task="toggleTask"
    />
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { api } from './api'
import { useAuth } from './composables/useAuth'
import { useI18n } from './composables/useI18n'
import { icons } from './utils/icons'
import Sidebar from './components/Sidebar.vue'
import FilterBar from './components/FilterBar.vue'
import ProfileMenu from './components/ProfileMenu.vue'
import ProfileDetailsModal from './components/ProfileDetailsModal.vue'
import TasksModal from './components/TasksModal.vue'
import LanguageSwitcher from './components/LanguageSwitcher.vue'

export default {
  name: 'App',
  components: {
    Sidebar,
    FilterBar,
    ProfileMenu,
    ProfileDetailsModal,
    TasksModal,
    LanguageSwitcher
  },
  setup() {
    const route = useRoute()
    const { currentUser } = useAuth()
    const { t } = useI18n()
    
    const showProfileDetails = ref(false)
    const showTasks = ref(false)
    const apiTasks = ref([])
    const sidebarCollapsed = ref(false)

    // Navigation items with SVG icons
    // Icons are defined in utils/icons.js for maintainability
    const navigationItems = computed(() => [
      { 
        path: '/', 
        label: t('nav.overview'), 
        icon: icons.dashboard 
      },
      { 
        path: '/inventory', 
        label: t('nav.inventory'), 
        icon: icons.inventory 
      },
      { 
        path: '/orders', 
        label: t('nav.orders'), 
        icon: icons.orders 
      },
      { 
        path: '/restocking', 
        label: 'Restocking', 
        icon: icons.restocking 
      },
      { 
        path: '/demand', 
        label: t('nav.demandForecast'), 
        icon: icons.demand 
      },
      { 
        path: '/spending', 
        label: t('nav.finance'), 
        icon: icons.spending 
      },
      { 
        path: '/reports', 
        label: 'Reports', 
        icon: icons.reports 
      }
    ])

    // Compute page title based on current route
    const pageTitle = computed(() => {
      const item = navigationItems.value.find(i => {
        if (i.path === '/') {
          return route.path === '/'
        }
        return route.path.startsWith(i.path)
      })
      return item?.label || 'Dashboard'
    })

    // Determine if filters should be shown on this route
    // Filters are hidden on specific pages like reports
    const showFilters = computed(() => {
      return route.meta.showFilters !== false && route.path !== '/reports'
    })

    // Merge mock tasks from currentUser with API tasks
    const tasks = computed(() => {
      return [...currentUser.value.tasks, ...apiTasks.value]
    })

    const loadTasks = async () => {
      try {
        apiTasks.value = await api.getTasks()
      } catch (err) {
        console.error('Failed to load tasks:', err)
      }
    }

    const addTask = async (taskData) => {
      try {
        const newTask = await api.createTask(taskData)
        // Add new task to the beginning of the array
        apiTasks.value.unshift(newTask)
      } catch (err) {
        console.error('Failed to add task:', err)
      }
    }

    const deleteTask = async (taskId) => {
      try {
        // Check if it's a mock task (from currentUser)
        const isMockTask = currentUser.value.tasks.some(t => t.id === taskId)

        if (isMockTask) {
          // Remove from mock tasks
          const index = currentUser.value.tasks.findIndex(t => t.id === taskId)
          if (index !== -1) {
            currentUser.value.tasks.splice(index, 1)
          }
        } else {
          // Remove from API tasks
          await api.deleteTask(taskId)
          apiTasks.value = apiTasks.value.filter(t => t.id !== taskId)
        }
      } catch (err) {
        console.error('Failed to delete task:', err)
      }
    }

    const toggleTask = async (taskId) => {
      try {
        // Check if it's a mock task (from currentUser)
        const mockTask = currentUser.value.tasks.find(t => t.id === taskId)

        if (mockTask) {
          // Toggle mock task status
          mockTask.status = mockTask.status === 'pending' ? 'completed' : 'pending'
        } else {
          // Toggle API task
          const updatedTask = await api.toggleTask(taskId)
          const index = apiTasks.value.findIndex(t => t.id === taskId)
          if (index !== -1) {
            apiTasks.value[index] = updatedTask
          }
        }
      } catch (err) {
        console.error('Failed to toggle task:', err)
      }
    }

    const handleSidebarToggle = (collapsed) => {
      sidebarCollapsed.value = collapsed
    }

    const handleThemeToggle = (isDark) => {
      // Theme is handled by Sidebar component
      // This handler can be used for additional theme logic if needed
      console.log('Theme toggled:', isDark ? 'dark' : 'light')
    }

    onMounted(loadTasks)

    return {
      t,
      showProfileDetails,
      showTasks,
      tasks,
      navigationItems,
      pageTitle,
      showFilters,
      sidebarCollapsed,
      addTask,
      deleteTask,
      toggleTask,
      handleSidebarToggle,
      handleThemeToggle
    }
  }
}
</script>

<style>
/* CSS Variables for Light Mode */
:root {
  /* Primary Colors */
  --color-primary-50: #eff6ff;
  --color-primary-100: #dbeafe;
  --color-primary-500: #3b82f6;
  --color-primary-600: #2563eb;
  --color-primary-700: #1d4ed8;

  /* Neutral Colors */
  --color-gray-50: #f9fafb;
  --color-gray-100: #f3f4f6;
  --color-gray-200: #e5e7eb;
  --color-gray-300: #d1d5db;
  --color-gray-400: #9ca3af;
  --color-gray-500: #6b7280;
  --color-gray-600: #4b5563;
  --color-gray-700: #374151;
  --color-gray-800: #1f2937;
  --color-gray-900: #111827;

  /* Status Colors */
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
  --color-info: #3b82f6;

  /* Background Colors */
  --bg-primary: #ffffff;
  --bg-secondary: #f9fafb;
  --bg-tertiary: #f3f4f6;

  /* Text Colors */
  --text-primary: #111827;
  --text-secondary: #6b7280;
  --text-tertiary: #9ca3af;

  /* Border Colors */
  --border-light: #e5e7eb;
  --border-medium: #d1d5db;
  --border-dark: #9ca3af;

  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;
  --spacing-2xl: 3rem;
}

/* Dark Mode Variables */
.dark-mode {
  /* Primary Colors (slightly adjusted for dark mode) */
  --color-primary-50: #1e3a8a;
  --color-primary-100: #1e40af;
  --color-primary-500: #60a5fa;
  --color-primary-600: #93c5fd;
  --color-primary-700: #bfdbfe;

  /* Neutral Colors (inverted) */
  --color-gray-50: #1f2937;
  --color-gray-100: #374151;
  --color-gray-200: #4b5563;
  --color-gray-300: #6b7280;
  --color-gray-400: #9ca3af;
  --color-gray-500: #d1d5db;
  --color-gray-600: #e5e7eb;
  --color-gray-700: #f3f4f6;
  --color-gray-800: #f9fafb;
  --color-gray-900: #ffffff;

  /* Background Colors (dark) */
  --bg-primary: #111827;
  --bg-secondary: #1f2937;
  --bg-tertiary: #374151;

  /* Text Colors (inverted) */
  --text-primary: #f9fafb;
  --text-secondary: #d1d5db;
  --text-tertiary: #9ca3af;

  /* Border Colors (darker) */
  --border-light: #374151;
  --border-medium: #4b5563;
  --border-dark: #6b7280;
}

/* Global Reset */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: var(--bg-secondary);
  color: var(--text-primary);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  transition: background-color 0.2s, color 0.2s;
}

/* App Container Layout */
.app-container {
  display: flex;
  min-height: 100vh;
}

/* Main Wrapper (right of sidebar) */
.main-wrapper {
  flex: 1;
  margin-left: 260px;
  display: flex;
  flex-direction: column;
  transition: margin-left 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.app-container.sidebar-collapsed .main-wrapper {
  margin-left: 72px;
}

/* Top Bar */
.top-bar {
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-light);
  padding: 1rem 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 64px;
  position: sticky;
  top: 0;
  z-index: 100;
  transition: background-color 0.2s, border-color 0.2s;
}

.top-bar-left {
  flex: 1;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.025em;
}

.top-bar-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

/* Main Content */
.main-content {
  flex: 1;
  padding: 2rem;
  max-width: 1600px;
  width: 100%;
  margin: 0 auto;
}

/* Page Headers */
.page-header {
  margin-bottom: 1.5rem;
}

.page-header h2 {
  font-size: 1.875rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.375rem;
  letter-spacing: -0.025em;
}

.page-header p {
  color: var(--text-secondary);
  font-size: 0.938rem;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.25rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  background: var(--bg-primary);
  padding: 1.5rem;
  border-radius: 12px;
  border: 1px solid var(--border-light);
  transition: all 0.2s ease;
}

.stat-card:hover {
  border-color: var(--border-medium);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.stat-label {
  color: var(--text-secondary);
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 0.75rem;
}

.stat-value {
  font-size: 2.25rem;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.025em;
}

.stat-card.warning .stat-value {
  color: var(--color-warning);
}

.stat-card.success .stat-value {
  color: var(--color-success);
}

.stat-card.danger .stat-value {
  color: var(--color-error);
}

.stat-card.info .stat-value {
  color: var(--color-info);
}

/* Card Styles */
.card {
  background: var(--bg-primary);
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid var(--border-light);
  margin-bottom: 1.5rem;
  transition: background-color 0.2s, border-color 0.2s;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.875rem;
  border-bottom: 1px solid var(--border-light);
}

.card-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.025em;
}

/* Table Styles */
.table-container {
  overflow-x: auto;
  border-radius: 8px;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: var(--bg-tertiary);
  border-top: 1px solid var(--border-light);
  border-bottom: 1px solid var(--border-light);
}

th {
  text-align: left;
  padding: 0.75rem 1rem;
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

td {
  padding: 0.75rem 1rem;
  border-top: 1px solid var(--border-light);
  color: var(--text-primary);
  font-size: 0.875rem;
}

tbody tr {
  transition: background-color 0.15s ease;
}

tbody tr:hover {
  background: var(--bg-secondary);
}

/* Badge Styles */
.badge {
  display: inline-block;
  padding: 0.375rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.badge.success {
  background: #d1fae5;
  color: #065f46;
}

.badge.warning {
  background: #fed7aa;
  color: #92400e;
}

.badge.danger {
  background: #fecaca;
  color: #991b1b;
}

.badge.info {
  background: #dbeafe;
  color: #1e40af;
}

.badge.increasing {
  background: #d1fae5;
  color: #065f46;
}

.badge.decreasing {
  background: #fecaca;
  color: #991b1b;
}

.badge.stable {
  background: #e0e7ff;
  color: #3730a3;
}

.badge.high {
  background: #fecaca;
  color: #991b1b;
}

.badge.medium {
  background: #fed7aa;
  color: #92400e;
}

.badge.low {
  background: #dbeafe;
  color: #1e40af;
}

/* Loading & Error States */
.loading {
  text-align: center;
  padding: 3rem;
  color: var(--text-secondary);
  font-size: 0.938rem;
}

.error {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #991b1b;
  padding: 1rem;
  border-radius: 8px;
  margin: 1rem 0;
  font-size: 0.938rem;
}

.dark-mode .error {
  background: #7f1d1d;
  border-color: #991b1b;
  color: #fecaca;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .main-wrapper {
    margin-left: 0;
  }

  .top-bar {
    padding: 1rem;
  }

  .main-content {
    padding: 1rem;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .top-bar-right {
    gap: 0.5rem;
  }

  .page-title {
    font-size: 1.25rem;
  }
}
</style>
