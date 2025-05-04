import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import type { Dealership, CreateDealershipData, UpdateDealershipData } from "@/types/dealership"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000"

async function fetchDealerships(): Promise<Dealership[]> {
  const response = await fetch(`${API_URL}/dealerships`)
  if (!response.ok) {
    throw new Error("Failed to fetch dealerships")
  }
  return response.json()
}

async function createDealership(data: CreateDealershipData): Promise<Dealership> {
  const response = await fetch(`${API_URL}/dealerships`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    throw new Error("Failed to create dealership")
  }
  return response.json()
}

async function updateDealership(data: UpdateDealershipData): Promise<Dealership> {
  const response = await fetch(`${API_URL}/dealerships/${data.id}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    throw new Error("Failed to update dealership")
  }
  return response.json()
}

async function deleteDealership(id: string): Promise<void> {
  const response = await fetch(`${API_URL}/dealerships/${id}`, {
    method: "DELETE",
  })
  if (!response.ok) {
    throw new Error("Failed to delete dealership")
  }
}

export function useDealerships() {
  return useQuery({
    queryKey: ["dealerships"],
    queryFn: fetchDealerships,
  })
}

export function useCreateDealership() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: createDealership,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dealerships"] })
    },
  })
}

export function useUpdateDealership() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: updateDealership,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dealerships"] })
    },
  })
}

export function useDeleteDealership() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: deleteDealership,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dealerships"] })
    },
  })
} 