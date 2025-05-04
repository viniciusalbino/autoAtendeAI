import * as React from "react"
import { useVehicles, useDeleteVehicle } from "@/hooks/use-vehicles"
import { Button } from "@/components/ui/button"
import { toast } from "@/hooks/use-toast"
import type { Vehicle } from "@/types/vehicle"

interface VehicleListProps {
  onEdit: (vehicle: Vehicle) => void
}

export function VehicleList({ onEdit }: VehicleListProps) {
  const { data: vehicles, isLoading, error } = useVehicles()
  const deleteMutation = useDeleteVehicle()

  if (isLoading) {
    return <div>Loading vehicles...</div>
  }

  if (error) {
    return <div>Error loading vehicles</div>
  }

  const handleDelete = async (id: string) => {
    try {
      await deleteMutation.mutateAsync(id)
      toast({
        title: "Success",
        description: "Vehicle deleted successfully",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete vehicle",
        variant: "destructive",
      })
    }
  }

  return (
    <div className="space-y-4">
      {vehicles?.map((vehicle) => (
        <div
          key={vehicle.id}
          className="flex items-center justify-between p-4 border rounded-lg"
        >
          <div>
            <h3 className="text-lg font-medium">
              {vehicle.brand} {vehicle.model}
            </h3>
            <p className="text-sm text-gray-500">
              Year: {vehicle.year} | Price: ${vehicle.price.toLocaleString()}
            </p>
            {vehicle.description && (
              <p className="mt-2 text-sm">{vehicle.description}</p>
            )}
          </div>
          <div className="flex space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => onEdit(vehicle)}
            >
              Edit
            </Button>
            <Button
              variant="destructive"
              size="sm"
              onClick={() => handleDelete(vehicle.id)}
              disabled={deleteMutation.isPending}
            >
              {deleteMutation.isPending ? "Deleting..." : "Delete"}
            </Button>
          </div>
        </div>
      ))}
    </div>
  )
} 