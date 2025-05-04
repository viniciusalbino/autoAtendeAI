export interface Dealership {
  id: string
  name: string
  address: string
  city: string
  state: string
  phone: string
  email: string
  createdAt: string
  updatedAt: string
}

export type CreateDealershipData = Omit<Dealership, "id" | "createdAt" | "updatedAt">

export type UpdateDealershipData = Partial<CreateDealershipData> & { id: string } 