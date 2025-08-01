import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiService, type User, type Product, type Order } from '../services/api'

// Query Keys
export const queryKeys = {
  dashboard: {
    stats: ['dashboard', 'stats'] as const,
    revenue: (period: string) => ['dashboard', 'revenue', period] as const,
    categorySales: ['dashboard', 'category-sales'] as const,
    activity: (limit: number) => ['dashboard', 'activity', limit] as const,
  },
  users: {
    all: ['users'] as const,
    list: (page: number, limit: number) => ['users', 'list', page, limit] as const,
    detail: (id: number) => ['users', 'detail', id] as const,
    growth: (period: string) => ['users', 'growth', period] as const,
    demographics: ['users', 'demographics'] as const,
  },
  products: {
    all: ['products'] as const,
    list: (page: number, limit: number) => ['products', 'list', page, limit] as const,
    detail: (id: number) => ['products', 'detail', id] as const,
    sales: ['products', 'sales'] as const,
    inventory: ['products', 'inventory'] as const,
  },
  orders: {
    all: ['orders'] as const,
    list: (page: number, limit: number) => ['orders', 'list', page, limit] as const,
    detail: (id: number) => ['orders', 'detail', id] as const,
    timeline: (period: string) => ['orders', 'timeline', period] as const,
    statusDistribution: ['orders', 'status-distribution'] as const,
    daily: ['orders', 'daily'] as const,
  },
  analytics: {
    all: ['analytics'] as const,
    data: (period: string) => ['analytics', 'data', period] as const,
    traffic: ['analytics', 'traffic'] as const,
    conversion: ['analytics', 'conversion'] as const,
    devices: ['analytics', 'devices'] as const,
  },
  settings: {
    all: ['settings'] as const,
  },
  auth: {
    currentUser: ['auth', 'current-user'] as const,
  },
}

// Dashboard Hooks
export const useDashboardStats = () => {
  return useQuery({
    queryKey: queryKeys.dashboard.stats,
    queryFn: apiService.getDashboardStats,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

export const useRevenueData = (period: string = '6m') => {
  return useQuery({
    queryKey: queryKeys.dashboard.revenue(period),
    queryFn: () => apiService.getRevenueData(period),
    staleTime: 10 * 60 * 1000, // 10 minutes
  })
}

export const useCategorySales = () => {
  return useQuery({
    queryKey: queryKeys.dashboard.categorySales,
    queryFn: apiService.getCategorySales,
    staleTime: 15 * 60 * 1000, // 15 minutes
  })
}

export const useRecentActivity = (limit: number = 10) => {
  return useQuery({
    queryKey: queryKeys.dashboard.activity(limit),
    queryFn: () => apiService.getRecentActivity(limit),
    refetchInterval: 30 * 1000, // Refetch every 30 seconds
  })
}

// User Hooks
export const useUsers = (page: number = 1, limit: number = 10) => {
  return useQuery({
    queryKey: queryKeys.users.list(page, limit),
    queryFn: () => apiService.getUsers(page, limit),
    placeholderData: (previousData) => previousData,
  })
}

export const useUser = (id: number) => {
  return useQuery({
    queryKey: queryKeys.users.detail(id),
    queryFn: () => apiService.getUserById(id),
    enabled: !!id,
  })
}

export const useUserGrowth = (period: string = '6m') => {
  return useQuery({
    queryKey: queryKeys.users.growth(period),
    queryFn: () => apiService.getUserGrowthData(period),
    staleTime: 10 * 60 * 1000,
  })
}

export const useUserDemographics = () => {
  return useQuery({
    queryKey: queryKeys.users.demographics,
    queryFn: apiService.getUserDemographics,
    staleTime: 30 * 60 * 1000, // 30 minutes
  })
}

export const useCreateUser = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: apiService.createUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.users.all })
      queryClient.invalidateQueries({ queryKey: queryKeys.dashboard.stats })
    },
  })
}

export const useUpdateUser = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ id, userData }: { id: number; userData: Partial<User> }) =>
      apiService.updateUser(id, userData),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.users.all })
      queryClient.setQueryData(queryKeys.users.detail(variables.id), data)
    },
  })
}

export const useDeleteUser = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: apiService.deleteUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.users.all })
      queryClient.invalidateQueries({ queryKey: queryKeys.dashboard.stats })
    },
  })
}

// Product Hooks
export const useProducts = (page: number = 1, limit: number = 10) => {
  return useQuery({
    queryKey: queryKeys.products.list(page, limit),
    queryFn: () => apiService.getProducts(page, limit),
    placeholderData: (previousData) => previousData,
  })
}

export const useProduct = (id: number) => {
  return useQuery({
    queryKey: queryKeys.products.detail(id),
    queryFn: () => apiService.getProductById(id),
    enabled: !!id,
  })
}

export const useProductSales = () => {
  return useQuery({
    queryKey: queryKeys.products.sales,
    queryFn: apiService.getProductSales,
    staleTime: 15 * 60 * 1000,
  })
}

export const useInventoryLevels = () => {
  return useQuery({
    queryKey: queryKeys.products.inventory,
    queryFn: apiService.getInventoryLevels,
    staleTime: 5 * 60 * 1000,
  })
}

export const useCreateProduct = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: apiService.createProduct,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.products.all })
      queryClient.invalidateQueries({ queryKey: queryKeys.dashboard.stats })
    },
  })
}

export const useUpdateProduct = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ id, productData }: { id: number; productData: Partial<Product> }) =>
      apiService.updateProduct(id, productData),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.products.all })
      queryClient.setQueryData(queryKeys.products.detail(variables.id), data)
    },
  })
}

export const useDeleteProduct = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: apiService.deleteProduct,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.products.all })
      queryClient.invalidateQueries({ queryKey: queryKeys.dashboard.stats })
    },
  })
}

// Order Hooks
export const useOrders = (page: number = 1, limit: number = 10) => {
  return useQuery({
    queryKey: queryKeys.orders.list(page, limit),
    queryFn: () => apiService.getOrders(page, limit),
    keepPreviousData: true,
  })
}

export const useOrder = (id: number) => {
  return useQuery({
    queryKey: queryKeys.orders.detail(id),
    queryFn: () => apiService.getOrderById(id),
    enabled: !!id,
  })
}

export const useOrdersTimeline = (period: string = '6m') => {
  return useQuery({
    queryKey: queryKeys.orders.timeline(period),
    queryFn: () => apiService.getOrdersOverTime(period),
    staleTime: 10 * 60 * 1000,
  })
}

export const useOrderStatusDistribution = () => {
  return useQuery({
    queryKey: queryKeys.orders.statusDistribution,
    queryFn: apiService.getOrderStatusDistribution,
    staleTime: 5 * 60 * 1000,
  })
}

export const useDailyOrders = () => {
  return useQuery({
    queryKey: queryKeys.orders.daily,
    queryFn: apiService.getDailyOrders,
    staleTime: 5 * 60 * 1000,
  })
}

export const useUpdateOrderStatus = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ id, status }: { id: number; status: Order['status'] }) =>
      apiService.updateOrderStatus(id, status),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.orders.all })
      queryClient.setQueryData(queryKeys.orders.detail(variables.id), data)
      queryClient.invalidateQueries({ queryKey: queryKeys.orders.statusDistribution })
    },
  })
}

// Analytics Hooks
export const useAnalyticsData = (period: string = '7d') => {
  return useQuery({
    queryKey: queryKeys.analytics.data(period),
    queryFn: () => apiService.getAnalyticsData(period),
    staleTime: 10 * 60 * 1000,
  })
}

export const useTrafficData = () => {
  return useQuery({
    queryKey: queryKeys.analytics.traffic,
    queryFn: apiService.getTrafficData,
    staleTime: 15 * 60 * 1000,
  })
}

export const useConversionData = () => {
  return useQuery({
    queryKey: queryKeys.analytics.conversion,
    queryFn: apiService.getConversionData,
    staleTime: 15 * 60 * 1000,
  })
}

export const useDeviceUsage = () => {
  return useQuery({
    queryKey: queryKeys.analytics.devices,
    queryFn: apiService.getDeviceUsage,
    staleTime: 30 * 60 * 1000,
  })
}

// Settings Hooks
export const useSettings = () => {
  return useQuery({
    queryKey: queryKeys.settings.all,
    queryFn: apiService.getSettings,
    staleTime: 60 * 60 * 1000, // 1 hour
  })
}

export const useUpdateSettings = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: apiService.updateSettings,
    onSuccess: (data) => {
      queryClient.setQueryData(queryKeys.settings.all, data)
    },
  })
}

// Auth Hooks
export const useCurrentUser = () => {
  return useQuery({
    queryKey: queryKeys.auth.currentUser,
    queryFn: apiService.getCurrentUser,
    staleTime: 30 * 60 * 1000, // 30 minutes
    retry: false,
  })
}

export const useLogin = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ email, password }: { email: string; password: string }) =>
      apiService.login(email, password),
    onSuccess: (data) => {
      localStorage.setItem('authToken', data.token)
      queryClient.setQueryData(queryKeys.auth.currentUser, data.user)
      queryClient.invalidateQueries()
    },
  })
}

export const useLogout = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: apiService.logout,
    onSuccess: () => {
      queryClient.clear()
    },
  })
}