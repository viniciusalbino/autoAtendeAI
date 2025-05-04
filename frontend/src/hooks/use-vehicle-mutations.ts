import { useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/axios'
import { CreateVehicleData, UpdateVehicleData } from '@/types'

export function useVehicleMutations() {
  const queryClient = useQueryClient()

  const createVehicle = useMutation({
    mutationFn: (data: CreateVehicleData) => api.post('/vehicles', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vehicles'] })
    },
  })

  const updateVehicle = useMutation({
    mutationFn: ({ id, data }: { id: number; data: UpdateVehicleData }) =>
      api.put(`/vehicles/${id}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vehicles'] })
    },
  })

  const markVehicleAsSold = useMutation({
    mutationFn: (id: number) =>
      api.put(`/vehicles/${id}`, { is_available: false }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vehicles'] })
    },
  })

  return {
    createVehicle,
    updateVehicle,
    markVehicleAsSold,
  }
} 