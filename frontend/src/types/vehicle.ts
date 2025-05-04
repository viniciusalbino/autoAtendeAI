export interface Vehicle {
  id: string
  brand: string
  model: string
  year: number
  price: number
  dealershipId: string
  description?: string
  imageUrl?: string
  createdAt: string
  updatedAt: string
}

export type CreateVehicleData = Omit<Vehicle, "id" | "createdAt" | "updatedAt">

export type UpdateVehicleData = Partial<CreateVehicleData> & { id: string } 