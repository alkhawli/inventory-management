<template>
  <aside class="sidebar" :class="{ collapsed: isCollapsed, dark: isDark }">
    <!-- Sidebar Header -->
    <div class="sidebar-header">
      <div class="logo">
        <span v-if="!isCollapsed" class="logo-text">Factory Inventory</span>
        <span v-else class="logo-icon">FI</span>
      </div>
      <button @click="toggleSidebar" class="collapse-btn" :title="isCollapsed ? 'Expand' : 'Collapse'">
        <svg v-if="!isCollapsed" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M15 18l-6-6 6-6"/>
        </svg>
        <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M9 18l6-6-6-6"/>
        </svg>
      </button>
    </div>

    <!-- Navigation Items -->
    <nav class="sidebar-nav">
      <router-link
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        class="nav-item"
        :class="{ active: isActive(item.path) }"
        :title="isCollapsed ? item.label : ''"
      >
        <span class="nav-icon" v-html="item.icon"></span>
        <span v-if="!isCollapsed" class="nav-label">{{ item.label }}</span>
        <span v-if="item.badge && !isCollapsed" class="nav-badge">{{ item.badge }}</span>
      </router-link>
    </nav>

    <!-- Sidebar Footer -->
    <div class="sidebar-footer">
      <!-- Theme Toggle -->
      <button @click="toggleTheme" class="theme-toggle" :title="isDark ? 'Light Mode' : 'Dark Mode'">
        <svg v-if="!isDark" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
        </svg>
        <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="5"/>
          <path d="M12 1v2m0 18v2M4.22 4.22l1.42 1.42m12.72 12.72 1.42 1.42M1 12h2m18 0h2M4.22 19.78l1.42-1.42m12.72-12.72 1.42-1.42"/>
        </svg>
        <span v-if="!isCollapsed" class="theme-label">{{ isDark ? 'Light' : 'Dark' }} Mode</span>
      </button>
    </div>
  </aside>
</template>

<script>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'

export default {
  name: 'Sidebar',
  props: {
    navItems: {
      type: Array,
      required: true
    }
  },
  emits: ['toggle-sidebar', 'toggle-theme'],
  setup(props, { emit }) {
    const route = useRoute()
    
    // Sidebar collapsed state - persisted in localStorage
    const isCollapsed = ref(localStorage.getItem('sidebarCollapsed') === 'true')
    
    // Dark mode state - persisted in localStorage
    const isDark = ref(localStorage.getItem('darkMode') === 'true')

    const toggleSidebar = () => {
      isCollapsed.value = !isCollapsed.value
      localStorage.setItem('sidebarCollapsed', isCollapsed.value.toString())
      emit('toggle-sidebar', isCollapsed.value)
    }

    const toggleTheme = () => {
      isDark.value = !isDark.value
      localStorage.setItem('darkMode', isDark.value.toString())
      
      // Apply dark mode class to document root for global theming
      if (isDark.value) {
        document.documentElement.classList.add('dark-mode')
      } else {
        document.documentElement.classList.remove('dark-mode')
      }
      
      emit('toggle-theme', isDark.value)
    }

    // Check if route is active
    // Handles exact match and nested routes
    const isActive = (path) => {
      if (path === '/') {
        return route.path === '/'
      }
      return route.path.startsWith(path)
    }

    // Initialize dark mode on mount
    if (isDark.value) {
      document.documentElement.classList.add('dark-mode')
    }

    return {
      isCollapsed,
      isDark,
      toggleSidebar,
      toggleTheme,
      isActive
    }
  }
}
</script>

<style scoped>
/* Sidebar Container */
.sidebar {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  width: 260px;
  background: #ffffff;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 1000;
}

.sidebar.collapsed {
  width: 72px;
}

/* Dark Mode */
.sidebar.dark {
  background: #1f2937;
  border-right-color: #374151;
}

/* Header Section */
.sidebar-header {
  padding: 1.25rem 1rem;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 64px;
}

.sidebar.dark .sidebar-header {
  border-bottom-color: #374151;
}

.logo {
  flex: 1;
  display: flex;
  align-items: center;
}

.logo-text {
  font-size: 1.125rem;
  font-weight: 700;
  color: #111827;
  white-space: nowrap;
}

.sidebar.dark .logo-text {
  color: #f9fafb;
}

.logo-icon {
  font-size: 1.25rem;
  font-weight: 700;
  color: #3b82f6;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #eff6ff;
  border-radius: 8px;
}

.sidebar.dark .logo-icon {
  background: #1e3a8a;
  color: #93c5fd;
}

.collapse-btn {
  padding: 0.5rem;
  border: none;
  background: transparent;
  color: #6b7280;
  cursor: pointer;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.collapse-btn:hover {
  background: #f3f4f6;
  color: #111827;
}

.sidebar.dark .collapse-btn {
  color: #9ca3af;
}

.sidebar.dark .collapse-btn:hover {
  background: #374151;
  color: #f9fafb;
}

/* Navigation */
.sidebar-nav {
  flex: 1;
  padding: 1rem 0.5rem;
  overflow-y: auto;
  overflow-x: hidden;
}

/* Custom Scrollbar */
.sidebar-nav::-webkit-scrollbar {
  width: 6px;
}

.sidebar-nav::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar-nav::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 3px;
}

.sidebar.dark .sidebar-nav::-webkit-scrollbar-thumb {
  background: #4b5563;
}

.sidebar-nav::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}

/* Navigation Items */
.nav-item {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  margin-bottom: 0.25rem;
  border-radius: 8px;
  color: #6b7280;
  text-decoration: none;
  transition: all 0.2s;
  position: relative;
  cursor: pointer;
}

.nav-item:hover {
  background: #f3f4f6;
  color: #111827;
}

.sidebar.dark .nav-item {
  color: #9ca3af;
}

.sidebar.dark .nav-item:hover {
  background: #374151;
  color: #f9fafb;
}

/* Active Navigation Item */
.nav-item.active {
  background: #eff6ff;
  color: #2563eb;
  font-weight: 600;
}

.sidebar.dark .nav-item.active {
  background: #1e3a8a;
  color: #93c5fd;
}

/* Active indicator line on the left */
.nav-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 60%;
  background: #2563eb;
  border-radius: 0 2px 2px 0;
}

.sidebar.dark .nav-item.active::before {
  background: #93c5fd;
}

.nav-icon {
  width: 20px;
  height: 20px;
  margin-right: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.nav-icon svg {
  width: 100%;
  height: 100%;
}

.collapsed .nav-icon {
  margin-right: 0;
}

.nav-label {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 0.9375rem;
}

.nav-badge {
  background: #ef4444;
  color: white;
  padding: 0.125rem 0.5rem;
  border-radius: 10px;
  font-size: 0.75rem;
  font-weight: 600;
  margin-left: auto;
}

/* Footer Section */
.sidebar-footer {
  padding: 1rem;
  border-top: 1px solid #e5e7eb;
}

.sidebar.dark .sidebar-footer {
  border-top-color: #374151;
}

.theme-toggle {
  width: 100%;
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  border: none;
  background: transparent;
  color: #6b7280;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.2s;
}

.theme-toggle:hover {
  background: #f3f4f6;
  color: #111827;
}

.sidebar.dark .theme-toggle {
  color: #9ca3af;
}

.sidebar.dark .theme-toggle:hover {
  background: #374151;
  color: #f9fafb;
}

.theme-toggle svg {
  flex-shrink: 0;
}

.theme-label {
  margin-left: 0.75rem;
  font-size: 0.9375rem;
  white-space: nowrap;
}

.collapsed .theme-toggle {
  justify-content: center;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .sidebar {
    transform: translateX(-100%);
  }

  .sidebar.open {
    transform: translateX(0);
    box-shadow: 4px 0 12px rgba(0, 0, 0, 0.15);
  }
}
</style>
