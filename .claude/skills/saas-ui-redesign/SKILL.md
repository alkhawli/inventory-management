---
name: saas-ui-redesign
description: Transform Vue 3 applications into modern SaaS-style interfaces with vertical sidebar navigation, consistent spacing, and professional polish. Use this skill when redesigning application UI/UX.
---

# SaaS UI Redesign Skill

This skill provides comprehensive guidelines for transforming Vue 3 applications from traditional top navigation layouts into modern SaaS-style interfaces with vertical sidebar navigation, consistent spacing, and professional aesthetics.

## Design Principles

### 1. Modern SaaS Aesthetics
- **Clean & Minimal**: Remove visual clutter, focus on content
- **Whitespace**: Generous padding and margins for breathing room
- **Depth**: Subtle shadows and layering for hierarchy
- **Consistency**: Uniform spacing, colors, and typography
- **Accessibility**: High contrast ratios, clear focus states

### 2. Layout Philosophy
```
┌─────────────────────────────────────────┐
│  Sidebar  │  Header Bar                 │
│  (Fixed)  │  ─────────────────────────  │
│           │                             │
│  Nav      │  Main Content Area          │
│  Items    │  (Scrollable)               │
│           │                             │
│           │  Cards, Tables, Charts      │
│           │                             │
└─────────────────────────────────────────┘
```

**Key Characteristics:**
- Vertical sidebar (240-280px width) on the left
- Fixed positioning for sidebar
- Minimal top header/toolbar (optional)
- Main content area with max-width container
- Responsive: sidebar collapses on mobile

## Layout Transformation

### Step 1: Create Sidebar Component

Create `components/Sidebar.vue`:

```vue
<template>
  <aside class="sidebar" :class="{ collapsed: isCollapsed }">
    <!-- Logo Section -->
    <div class="sidebar-header">
      <div class="logo">
        <img v-if="!isCollapsed" src="/logo.svg" alt="Logo" />
        <img v-else src="/logo-icon.svg" alt="Logo" />
      </div>
      <button @click="toggleSidebar" class="collapse-btn">
        <span v-if="!isCollapsed">←</span>
        <span v-else>→</span>
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
      >
        <span class="nav-icon" v-html="item.icon"></span>
        <span v-if="!isCollapsed" class="nav-label">{{ item.label }}</span>
        <span v-if="item.badge && !isCollapsed" class="nav-badge">
          {{ item.badge }}
        </span>
      </router-link>
    </nav>

    <!-- Footer Section (Optional) -->
    <div class="sidebar-footer">
      <div class="user-profile">
        <img :src="currentUser.avatar" alt="User" class="user-avatar" />
        <div v-if="!isCollapsed" class="user-info">
          <div class="user-name">{{ currentUser.name }}</div>
          <div class="user-role">{{ currentUser.role }}</div>
        </div>
      </div>
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
    },
    currentUser: {
      type: Object,
      default: () => ({
        name: 'User',
        role: 'Admin',
        avatar: '/default-avatar.png'
      })
    }
  },
  setup() {
    const route = useRoute()
    const isCollapsed = ref(false)

    const toggleSidebar = () => {
      isCollapsed.value = !isCollapsed.value
    }

    const isActive = (path) => {
      return route.path === path || route.path.startsWith(path + '/')
    }

    return {
      isCollapsed,
      toggleSidebar,
      isActive
    }
  }
}
</script>

<style scoped>
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
  transition: width 0.3s ease;
  z-index: 1000;
}

.sidebar.collapsed {
  width: 72px;
}

/* Header */
.sidebar-header {
  padding: 1.5rem 1rem;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 64px;
}

.logo {
  display: flex;
  align-items: center;
  font-size: 1.25rem;
  font-weight: 700;
  color: #111827;
}

.collapse-btn {
  padding: 0.5rem;
  border: none;
  background: transparent;
  cursor: pointer;
  color: #6b7280;
  border-radius: 6px;
  transition: all 0.2s;
}

.collapse-btn:hover {
  background: #f3f4f6;
  color: #111827;
}

/* Navigation */
.sidebar-nav {
  flex: 1;
  padding: 1rem 0.5rem;
  overflow-y: auto;
}

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
}

.nav-item:hover {
  background: #f3f4f6;
  color: #111827;
}

.nav-item.active {
  background: #eff6ff;
  color: #2563eb;
  font-weight: 600;
}

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

.nav-icon {
  width: 20px;
  height: 20px;
  margin-right: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.collapsed .nav-icon {
  margin-right: 0;
}

.nav-label {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
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

/* Footer */
.sidebar-footer {
  padding: 1rem;
  border-top: 1px solid #e5e7eb;
}

.user-profile {
  display: flex;
  align-items: center;
  padding: 0.5rem;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.user-profile:hover {
  background: #f3f4f6;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  margin-right: 0.75rem;
  flex-shrink: 0;
}

.collapsed .user-avatar {
  margin-right: 0;
}

.user-info {
  flex: 1;
  min-width: 0;
}

.user-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: #111827;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-role {
  font-size: 0.75rem;
  color: #6b7280;
}

/* Scrollbar */
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

.sidebar-nav::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .sidebar {
    transform: translateX(-100%);
  }

  .sidebar.open {
    transform: translateX(0);
  }

  .sidebar.collapsed {
    transform: translateX(-100%);
  }
}
</style>
```

### Step 2: Update App.vue Layout

Transform `App.vue` to use sidebar layout:

```vue
<template>
  <div class="app-container">
    <!-- Sidebar Navigation -->
    <Sidebar 
      :nav-items="navigationItems" 
      :current-user="currentUser"
    />

    <!-- Main Content Area -->
    <div class="main-container">
      <!-- Optional Top Bar -->
      <header class="top-bar" v-if="showTopBar">
        <div class="top-bar-left">
          <h1 class="page-title">{{ pageTitle }}</h1>
        </div>
        <div class="top-bar-right">
          <FilterBar v-if="showFilters" />
          <button class="notification-btn">🔔</button>
          <LanguageSwitcher />
        </div>
      </header>

      <!-- Page Content -->
      <main class="main-content">
        <router-view />
      </main>
    </div>

    <!-- Mobile Overlay -->
    <div class="mobile-overlay" @click="closeSidebar"></div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import Sidebar from './components/Sidebar.vue'
import FilterBar from './components/FilterBar.vue'
import LanguageSwitcher from './components/LanguageSwitcher.vue'

export default {
  name: 'App',
  components: {
    Sidebar,
    FilterBar,
    LanguageSwitcher
  },
  setup() {
    const route = useRoute()

    const navigationItems = [
      { path: '/', label: 'Dashboard', icon: '📊' },
      { path: '/inventory', label: 'Inventory', icon: '📦' },
      { path: '/orders', label: 'Orders', icon: '🛒', badge: '5' },
      { path: '/restocking', label: 'Restocking', icon: '🔄' },
      { path: '/demand', label: 'Forecasts', icon: '📈' },
      { path: '/spending', label: 'Finance', icon: '💰' },
      { path: '/reports', label: 'Reports', icon: '📋' }
    ]

    const currentUser = {
      name: 'John Doe',
      role: 'Admin',
      avatar: '/avatar.png'
    }

    const pageTitle = computed(() => {
      const item = navigationItems.find(i => i.path === route.path)
      return item?.label || 'Dashboard'
    })

    return {
      navigationItems,
      currentUser,
      pageTitle,
      showTopBar: true,
      showFilters: computed(() => route.meta.showFilters !== false)
    }
  }
}
</script>

<style>
/* Global Reset & Base Styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background: #f9fafb;
  color: #111827;
}

/* App Container */
.app-container {
  display: flex;
  min-height: 100vh;
}

/* Main Container (Right of Sidebar) */
.main-container {
  flex: 1;
  margin-left: 260px; /* Match sidebar width */
  display: flex;
  flex-direction: column;
  transition: margin-left 0.3s ease;
}

.sidebar.collapsed ~ .main-container {
  margin-left: 72px;
}

/* Top Bar */
.top-bar {
  background: white;
  border-bottom: 1px solid #e5e7eb;
  padding: 1rem 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 64px;
  position: sticky;
  top: 0;
  z-index: 100;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #111827;
}

.top-bar-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.notification-btn {
  padding: 0.5rem;
  background: transparent;
  border: none;
  font-size: 1.25rem;
  cursor: pointer;
  border-radius: 8px;
  transition: background 0.2s;
}

.notification-btn:hover {
  background: #f3f4f6;
}

/* Main Content */
.main-content {
  flex: 1;
  padding: 2rem;
  max-width: 1600px;
  width: 100%;
  margin: 0 auto;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .main-container {
    margin-left: 0;
  }

  .main-content {
    padding: 1rem;
  }

  .top-bar {
    padding: 1rem;
  }

  .mobile-overlay {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: 999;
  }

  .mobile-overlay.active {
    display: block;
  }
}
</style>
```

## Spacing System

### Consistent Spacing Scale
Use a standardized spacing scale throughout the application:

```css
/* CSS Variables for Spacing */
:root {
  --spacing-xs: 0.25rem;   /* 4px */
  --spacing-sm: 0.5rem;    /* 8px */
  --spacing-md: 1rem;      /* 16px */
  --spacing-lg: 1.5rem;    /* 24px */
  --spacing-xl: 2rem;      /* 32px */
  --spacing-2xl: 3rem;     /* 48px */
  --spacing-3xl: 4rem;     /* 64px */
}
```

### Component Spacing Guidelines

**Cards:**
```css
.card {
  padding: var(--spacing-xl);        /* 32px internal padding */
  margin-bottom: var(--spacing-lg);  /* 24px gap between cards */
  border-radius: 12px;
  background: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}
```

**Sections:**
```css
.section {
  margin-bottom: var(--spacing-2xl); /* 48px between sections */
}

.section-header {
  margin-bottom: var(--spacing-lg);  /* 24px below headers */
}
```

**Forms:**
```css
.form-group {
  margin-bottom: var(--spacing-lg);  /* 24px between form fields */
}

.form-label {
  margin-bottom: var(--spacing-sm); /* 8px label to input gap */
}
```

## Color Palette

### Modern SaaS Color System

```css
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
}
```

### Usage Examples

```css
/* Primary Button */
.btn-primary {
  background: var(--color-primary-600);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:hover {
  background: var(--color-primary-700);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

/* Card with Shadow */
.card {
  background: var(--bg-primary);
  border: 1px solid var(--border-light);
  border-radius: 12px;
  padding: var(--spacing-xl);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.card:hover {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
```

## Typography System

### Font Hierarchy

```css
:root {
  /* Font Families */
  --font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  --font-mono: 'Monaco', 'Courier New', monospace;

  /* Font Sizes */
  --text-xs: 0.75rem;    /* 12px */
  --text-sm: 0.875rem;   /* 14px */
  --text-base: 1rem;     /* 16px */
  --text-lg: 1.125rem;   /* 18px */
  --text-xl: 1.25rem;    /* 20px */
  --text-2xl: 1.5rem;    /* 24px */
  --text-3xl: 1.875rem;  /* 30px */
  --text-4xl: 2.25rem;   /* 36px */

  /* Font Weights */
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;

  /* Line Heights */
  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;
}
```

### Heading Styles

```css
h1 {
  font-size: var(--text-3xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  line-height: var(--leading-tight);
  margin-bottom: var(--spacing-lg);
}

h2 {
  font-size: var(--text-2xl);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  line-height: var(--leading-tight);
  margin-bottom: var(--spacing-md);
}

h3 {
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  line-height: var(--leading-normal);
  margin-bottom: var(--spacing-md);
}

p {
  font-size: var(--text-base);
  color: var(--text-secondary);
  line-height: var(--leading-normal);
  margin-bottom: var(--spacing-md);
}
```

## Component Patterns

### 1. Modern Card Component

```vue
<template>
  <div class="modern-card" :class="cardClass">
    <!-- Card Header -->
    <div class="card-header" v-if="$slots.header || title">
      <slot name="header">
        <h3 class="card-title">{{ title }}</h3>
        <p v-if="subtitle" class="card-subtitle">{{ subtitle }}</p>
      </slot>
      <div v-if="$slots.actions" class="card-actions">
        <slot name="actions"></slot>
      </div>
    </div>

    <!-- Card Body -->
    <div class="card-body">
      <slot></slot>
    </div>

    <!-- Card Footer -->
    <div class="card-footer" v-if="$slots.footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<style scoped>
.modern-card {
  background: white;
  border-radius: 12px;
  border: 1px solid var(--border-light);
  overflow: hidden;
  transition: all 0.2s;
}

.modern-card:hover {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
}

.card-header {
  padding: var(--spacing-xl);
  border-bottom: 1px solid var(--border-light);
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.card-title {
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0;
}

.card-subtitle {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin-top: var(--spacing-xs);
}

.card-body {
  padding: var(--spacing-xl);
}

.card-footer {
  padding: var(--spacing-xl);
  border-top: 1px solid var(--border-light);
  background: var(--bg-secondary);
}
</style>
```

### 2. Modern Table Component

```vue
<style scoped>
.modern-table-container {
  background: white;
  border-radius: 12px;
  border: 1px solid var(--border-light);
  overflow: hidden;
}

.modern-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
}

.modern-table thead {
  background: var(--bg-secondary);
  border-bottom: 2px solid var(--border-light);
}

.modern-table th {
  padding: 1rem 1.5rem;
  text-align: left;
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.modern-table td {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--border-light);
  font-size: var(--text-sm);
  color: var(--text-primary);
}

.modern-table tbody tr {
  transition: background 0.2s;
}

.modern-table tbody tr:hover {
  background: var(--bg-secondary);
}

.modern-table tbody tr:last-child td {
  border-bottom: none;
}
</style>
```

### 3. Status Badge Component

```vue
<template>
  <span class="status-badge" :class="`badge-${variant}`">
    <span v-if="dot" class="badge-dot"></span>
    <slot></slot>
  </span>
</template>

<script>
export default {
  props: {
    variant: {
      type: String,
      default: 'default',
      validator: (v) => ['default', 'success', 'warning', 'error', 'info'].includes(v)
    },
    dot: Boolean
  }
}
</script>

<style scoped>
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  line-height: 1;
}

.badge-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.badge-success {
  background: #d1fae5;
  color: #065f46;
}

.badge-success .badge-dot {
  background: #10b981;
}

.badge-warning {
  background: #fef3c7;
  color: #92400e;
}

.badge-warning .badge-dot {
  background: #f59e0b;
}

.badge-error {
  background: #fee2e2;
  color: #991b1b;
}

.badge-error .badge-dot {
  background: #ef4444;
}

.badge-info {
  background: #dbeafe;
  color: #1e40af;
}

.badge-info .badge-dot {
  background: #3b82f6;
}
</style>
```

## Implementation Checklist

### Phase 1: Structure
- [ ] Create `Sidebar.vue` component
- [ ] Update `App.vue` with new layout structure
- [ ] Remove top navigation bar
- [ ] Add sidebar navigation items
- [ ] Implement responsive mobile behavior

### Phase 2: Styling
- [ ] Add CSS custom properties for colors and spacing
- [ ] Update global styles in `App.vue`
- [ ] Apply consistent spacing throughout
- [ ] Add shadows and depth to cards
- [ ] Ensure proper hover states

### Phase 3: Components
- [ ] Create reusable card component
- [ ] Style tables with modern aesthetic
- [ ] Add status badge component
- [ ] Update form inputs styling
- [ ] Create button variants

### Phase 4: Polish
- [ ] Add smooth transitions
- [ ] Implement proper focus states
- [ ] Test keyboard navigation
- [ ] Verify color contrast ratios
- [ ] Test responsive breakpoints
- [ ] Add loading states
- [ ] Implement empty states

### Phase 5: Testing
- [ ] Test on different screen sizes
- [ ] Verify sidebar collapse functionality
- [ ] Check navigation highlighting
- [ ] Test all interactive elements
- [ ] Verify accessibility
- [ ] Cross-browser testing

## Best Practices

### 1. Always Comment Non-Obvious Logic
```vue
<script>
// Calculate sidebar margin for main content
// This ensures content doesn't overlap with fixed sidebar
// 260px = expanded sidebar width
// 72px = collapsed sidebar width
const mainMargin = computed(() => {
  return isCollapsed.value ? '72px' : '260px'
})
</script>
```

### 2. Use Semantic HTML
```vue
<!-- Good: Semantic structure -->
<nav class="sidebar-nav">
  <router-link>...</router-link>
</nav>

<!-- Avoid: Non-semantic divs -->
<div class="sidebar-nav">
  <div>...</div>
</div>
```

### 3. Progressive Enhancement
```css
/* Base styles first (mobile) */
.sidebar {
  width: 100%;
}

/* Enhanced for larger screens */
@media (min-width: 768px) {
  .sidebar {
    width: 260px;
  }
}
```

### 4. Consistent Naming Conventions
```css
/* Component-specific classes */
.sidebar-header { }
.sidebar-nav { }
.sidebar-footer { }

/* State modifiers */
.nav-item.active { }
.sidebar.collapsed { }

/* Utility classes */
.text-primary { }
.bg-secondary { }
```

### 5. Performance Considerations
```vue
<!-- Use v-show for frequently toggled elements -->
<div v-show="!isCollapsed" class="nav-label">

<!-- Use v-if for rarely shown elements -->
<div v-if="showMobileMenu" class="mobile-menu">
```

## Common Pitfalls to Avoid

1. **Inconsistent Spacing**: Always use spacing variables
2. **Missing Hover States**: Every interactive element needs hover feedback
3. **Poor Mobile Experience**: Test on mobile from the start
4. **Accessibility Issues**: Ensure keyboard navigation works
5. **Heavy Animations**: Keep transitions under 300ms
6. **Fixed Positioning Issues**: Account for z-index layers
7. **Color Contrast**: Maintain WCAG AA standards minimum

## Quick Reference

### Standard Spacing
- Card padding: 32px (2rem)
- Section gaps: 48px (3rem)
- Card gaps: 24px (1.5rem)
- Element gaps: 16px (1rem)

### Standard Borders
- Radius: 12px for cards, 8px for buttons
- Width: 1px
- Color: #e5e7eb

### Standard Shadows
- Card: `box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1)`
- Card hover: `box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1)`
- Button hover: `box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3)`

### Standard Transitions
- Duration: 200ms (0.2s)
- Easing: ease or ease-in-out
- Properties: background, transform, box-shadow

---

**Remember**: Modern SaaS design is about clarity, consistency, and user comfort. Every design decision should make the interface easier to use and more pleasant to look at.
