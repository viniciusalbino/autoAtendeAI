export interface Dealership {
  id: number
  name: string
  address: string
  phone: string
  email: string
  created_at: string
  updated_at: string
}

export interface Vehicle {
  id: number
  dealership_id: number
  brand: string
  model: string
  year: number
  model_year: number
  transmission: string
  fuel: string
  color: string
  mileage: number
  price: number
  promotional_price?: number
  condition: string
  notes?: string
  optional_items?: string[]
  photo_urls?: string[]
  is_available: boolean
  created_at: string
  updated_at: string
}

export interface DashboardStats {
  totalVehicles: number
  soldVehicles: number
  activeDealerships: number
  totalValue: number
}

export interface CreateVehicleData {
  dealership_id: number
  brand: string
  model: string
  year: number
  model_year: number
  transmission: string
  fuel: string
  color: string
  mileage: number
  price: number
  promotional_price?: number
  condition: string
  notes?: string
  optional_items?: string[]
  photo_urls?: string[]
  is_available: boolean
}

export interface UpdateVehicleData {
  dealership_id?: number
  brand?: string
  model?: string
  year?: number
  model_year?: number
  transmission?: string
  fuel?: string
  color?: string
  mileage?: number
  price?: number
  promotional_price?: number
  condition?: string
  notes?: string
  optional_items?: string[]
  photo_urls?: string[]
  is_available?: boolean
} 