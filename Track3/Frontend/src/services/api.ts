import axios from 'axios'


// Create axios instance with base configuration
const api = axios.create({
  baseURL: 'https://blood-management-system-xplx.onrender.com',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for adding auth tokens
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for handling errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('authToken')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Types for API responses
export interface DashboardStats {
  totalRevenue: number
  orders: number
  customers: number
  products: number
  revenueChange: string
  ordersChange: string
  customersChange: string
  productsChange: string
}

export interface RevenueData {
  labels: string[]
  data: number[]
}

export interface CategorySales {
  category: string
  value: number
  percentage: number
}

export interface Activity {
  id: number
  action: string
  time: string
  icon: string
  user?: string
}

export interface User {
  id: number
  name: string
  email: string
  role: string
  status: 'active' | 'inactive'
  createdAt: string
  lastLogin: string
}

// Blood Bank Management System specific types
export interface RegisterPayload {
  username: string
  email: string
  full_name: string
  role: 'staff'
  phone: string
  password: string
  confirm_password: string
}

export interface RegisterResponse {
  username: string
  email: string
  full_name: string
  role: string
  phone: string
  user_id: string
  is_active: boolean
  is_verified: boolean
  last_login: string
  created_at: string
  updated_at: string
  can_manage_inventory: boolean
  can_view_forecasts: boolean
  can_manage_donors: boolean
  can_access_reports: boolean
  can_manage_users: boolean
  can_view_analytics: boolean
}

export interface LoginPayload {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user_id: string
  username: string
  role: string
  permissions: Record<string, any>
}

export interface Product {
  id: number
  name: string
  category: string
  price: number
  stock: number
  sales: number
  status: 'active' | 'inactive'
}

export interface Order {
  id: number
  customerName: string
  total: number
  status: 'completed' | 'processing' | 'shipped' | 'cancelled'
  createdAt: string
  items: number
}

export interface AnalyticsData {
  pageViews: number[]
  uniqueVisitors: number[]
  bounceRate: number
  conversionRate: number[]
  deviceUsage: { device: string; percentage: number }[]
}

// Blood Bank Analytics Types
export interface BloodBankAnalytics {
  total_collections: number
  total_usage: number
  current_inventory: number
  low_stock_alerts: number
  blood_type_distribution: {
    blood_type: string
    units: number
    percentage: number
  }[]
  collection_trends: {
    date: string
    collections: number
  }[]
  usage_trends: {
    date: string
    usage: number
  }[]
  inventory_levels: {
    blood_type: string
    current_stock: number
    minimum_required: number
    status: 'normal' | 'low' | 'critical'
  }[]
  donor_statistics: {
    total_donors: number
    active_donors: number
    new_donors_this_month: number
  }
  expiry_alerts: {
    blood_type: string
    units_expiring: number
    expiry_date: string
  }[]
}

// Blood Collection Types
export interface BloodCollection {
  donor_age: number
  donor_gender: 'M' | 'F'
  donor_occupation: string
  blood_type: string
  collection_site: string
  donation_date: string
  expiry_date: string
  collection_volume_ml: number
  hemoglobin_g_dl: number
  donation_record_id: string
  created_at: string
  updated_at: string
}

export interface BloodCollectionParams {
  blood_type?: string
  collection_date_from?: string
  collection_date_to?: string
  limit?: number
  offset?: number
}

// Blood Usage Types
export interface BloodUsage {
  purpose: string
  department: string
  blood_group: string
  volume_given_out: number
  usage_date: string
  individual_name: string
  patient_location: string
  usage_id: string
  created_at: string
  updated_at: string
}

export interface BloodUsageParams {
  blood_group?: string
  usage_date_from?: string
  usage_date_to?: string
  patient_location?: string
  limit?: number
  offset?: number
}

// Blood Inventory Types
export interface BloodInventoryItem {
  blood_group: string
  total_available: number
  total_near_expiry: number
  total_expired: number
  available_units: number
  last_updated: string
}

// API Service Functions
export const apiService = {
  // Dashboard APIs
  getDashboardStats: async (): Promise<DashboardStats> => {
    const response = await api.get('/dashboard/stats')
    return response.data
  },

  getRevenueData: async (period: string = '6m'): Promise<RevenueData> => {
    const response = await api.get(`/dashboard/revenue?period=${period}`)
    return response.data
  },

  getCategorySales: async (): Promise<CategorySales[]> => {
    const response = await api.get('/dashboard/category-sales')
    return response.data
  },

  getRecentActivity: async (limit: number = 10): Promise<Activity[]> => {
    const response = await api.get(`/dashboard/activity?limit=${limit}`)
    return response.data
  },

  // User APIs
  getUsers: async (page: number = 1, limit: number = 10): Promise<{ users: User[]; total: number }> => {
    const response = await api.get(`/users?page=${page}&limit=${limit}`)
    return response.data
  },

  getUserById: async (id: number): Promise<User> => {
    const response = await api.get(`/users/${id}`)
    return response.data
  },

  createUser: async (userData: Omit<User, 'id' | 'createdAt' | 'lastLogin'>): Promise<User> => {
    const response = await api.post('/users', userData)
    return response.data
  },

  updateUser: async (id: number, userData: Partial<User>): Promise<User> => {
    const response = await api.put(`/users/${id}`, userData)
    return response.data
  },

  deleteUser: async (id: number): Promise<void> => {
    await api.delete(`/users/${id}`)
  },

  getUserGrowthData: async (period: string = '6m'): Promise<{ newUsers: number[]; activeUsers: number[] }> => {
    const response = await api.get(`/users/growth?period=${period}`)
    return response.data
  },

  getUserDemographics: async (): Promise<{ ageGroup: string; count: number }[]> => {
    const response = await api.get('/users/demographics')
    return response.data
  },

  // Product APIs
  getProducts: async (page: number = 1, limit: number = 10): Promise<{ products: Product[]; total: number }> => {
    const response = await api.get(`/products?page=${page}&limit=${limit}`)
    return response.data
  },

  getProductById: async (id: number): Promise<Product> => {
    const response = await api.get(`/products/${id}`)
    return response.data
  },

  createProduct: async (productData: Omit<Product, 'id'>): Promise<Product> => {
    const response = await api.post('/products', productData)
    return response.data
  },

  updateProduct: async (id: number, productData: Partial<Product>): Promise<Product> => {
    const response = await api.put(`/products/${id}`, productData)
    return response.data
  },

  deleteProduct: async (id: number): Promise<void> => {
    await api.delete(`/products/${id}`)
  },

  getProductSales: async (): Promise<{ category: string; sales: number }[]> => {
    const response = await api.get('/products/sales-by-category')
    return response.data
  },

  getInventoryLevels: async (): Promise<{ inStock: number[]; lowStock: number[] }> => {
    const response = await api.get('/products/inventory-levels')
    return response.data
  },

  // Order APIs
  getOrders: async (page: number = 1, limit: number = 10): Promise<{ orders: Order[]; total: number }> => {
    const response = await api.get(`/orders?page=${page}&limit=${limit}`)
    return response.data
  },

  getOrderById: async (id: number): Promise<Order> => {
    const response = await api.get(`/orders/${id}`)
    return response.data
  },

  updateOrderStatus: async (id: number, status: Order['status']): Promise<Order> => {
    const response = await api.put(`/orders/${id}/status`, { status })
    return response.data
  },

  getOrdersOverTime: async (period: string = '6m'): Promise<number[]> => {
    const response = await api.get(`/orders/timeline?period=${period}`)
    return response.data
  },

  getOrderStatusDistribution: async (): Promise<{ status: string; count: number }[]> => {
    const response = await api.get('/orders/status-distribution')
    return response.data
  },

  getDailyOrders: async (): Promise<number[]> => {
    const response = await api.get('/orders/daily')
    return response.data
  },

  // Analytics APIs
  getAnalyticsData: async (period: string = '7d'): Promise<AnalyticsData> => {
    const response = await api.get(`/analytics?period=${period}`)
    return response.data
  },

  getTrafficData: async (): Promise<{ pageViews: number[]; uniqueVisitors: number[] }> => {
    const response = await api.get('/analytics/traffic')
    return response.data
  },

  getConversionData: async (): Promise<number[]> => {
    const response = await api.get('/analytics/conversion')
    return response.data
  },

  getDeviceUsage: async (): Promise<{ device: string; percentage: number }[]> => {
    const response = await api.get('/analytics/devices')
    return response.data
  },

  // Settings APIs
  getSettings: async (): Promise<Record<string, any>> => {
    const response = await api.get('/settings')
    return response.data
  },

  updateSettings: async (settings: Record<string, any>): Promise<Record<string, any>> => {
    const response = await api.put('/settings', settings)
    return response.data
  },

  // Blood Bank Management System Authentication APIs
  register: async (payload: RegisterPayload): Promise<RegisterResponse> => {
    const response = await api.post('/api/v1/auth/register', payload)
    return response.data
  },

  login: async (payload: LoginPayload): Promise<LoginResponse> => {
    const response = await api.post('/api/v1/auth/login', payload)
    return response.data
  },

  logout: async (): Promise<void> => {
    localStorage.removeItem('authToken')
    localStorage.removeItem('user')
  },

  getCurrentUser: async (): Promise<RegisterResponse> => {
    const response = await api.get('/api/v1/auth/me')
    return response.data
  },

  // Blood Bank Analytics APIs
  getBloodBankAnalytics: async (daysBack: number = 30): Promise<BloodBankAnalytics> => {
    const response = await api.get(`/api/v1/blood-bank/analytics/dashboard?days_back=${daysBack}`)
    return response.data
  },

  // Blood Collections APIs
  getBloodCollections: async (params: BloodCollectionParams = {}): Promise<BloodCollection[]> => {
    const queryParams = new URLSearchParams()
    
    if (params.blood_type) queryParams.append('blood_type', params.blood_type)
    if (params.collection_date_from) queryParams.append('collection_date_from', params.collection_date_from)
    if (params.collection_date_to) queryParams.append('collection_date_to', params.collection_date_to)
    if (params.limit) queryParams.append('limit', params.limit.toString())
    if (params.offset) queryParams.append('offset', params.offset.toString())

    const response = await api.get(`/api/v1/blood-bank/collections?${queryParams.toString()}`)
    return response.data
  },

  // Blood Usage APIs
  getBloodUsage: async (params: BloodUsageParams = {}): Promise<BloodUsage[]> => {
    const queryParams = new URLSearchParams()
    
    if (params.blood_group) queryParams.append('blood_group', params.blood_group)
    if (params.usage_date_from) queryParams.append('usage_date_from', params.usage_date_from)
    if (params.usage_date_to) queryParams.append('usage_date_to', params.usage_date_to)
    if (params.patient_location) queryParams.append('patient_location', params.patient_location)
    if (params.limit) queryParams.append('limit', params.limit.toString())
    if (params.offset) queryParams.append('offset', params.offset.toString())

    const response = await api.get(`/api/v1/blood-bank/usage?${queryParams.toString()}`)
    return response.data
  },

  // Blood Inventory APIs
  getBloodInventory: async (): Promise<BloodInventoryItem[]> => {
    const response = await api.get('/api/v1/blood-bank/inventory')
    return response.data
  },

  getBloodInventoryByGroup: async (bloodGroup: string): Promise<BloodInventoryItem> => {
    const response = await api.get(`/api/v1/blood-bank/inventory/${bloodGroup}`)
    return response.data
  },
}

export default api