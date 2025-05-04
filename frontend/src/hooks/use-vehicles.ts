import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import type { Vehicle, CreateVehicleData, UpdateVehicleData } from "@/types/vehicle"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000"

async function fetchVehicles(): Promise<Vehicle[]> {
  const response = await fetch(`${API_URL}/vehicles`)
  if (!response.ok) {
    throw new Error("Failed to fetch vehicles")
  }
  return response.json()
}

async function createVehicle(data: CreateVehicleData): Promise<Vehicle> {
  const response = await fetch(`${API_URL}/vehicles`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    throw new Error("Failed to create vehicle")
  }
  return response.json()
}

async function updateVehicle(data: UpdateVehicleData): Promise<Vehicle> {
  const response = await fetch(`${API_URL}/vehicles/${data.id}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    throw new Error("Failed to update vehicle")
  }
  return response.json()
}

async function deleteVehicle(id: string): Promise<void> {
  const response = await fetch(`${API_URL}/vehicles/${id}`, {
    method: "DELETE",
  })
  if (!response.ok) {
    throw new Error("Failed to delete vehicle")
  }
}

export function useVehicles() {
  return useQuery({
    queryKey: ["vehicles"],
    queryFn: fetchVehicles,
  })
}

export function useCreateVehicle() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: createVehicle,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["vehicles"] })
    },
  })
}

export function useUpdateVehicle() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: updateVehicle,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["vehicles"] })
    },
  })
}

export function useDeleteVehicle() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: deleteVehicle,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["vehicles"] })
    },
  })
} 