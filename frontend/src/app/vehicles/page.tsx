'use client'
import * as React from "react"
import { useVehicles, useCreateVehicle, useUpdateVehicle, useDeleteVehicle } from "@/hooks/use-vehicles"
import { VehicleList } from "@/components/vehicles/vehicle-list"
import { VehicleDialog } from "@/components/vehicles/vehicle-dialog"
import { Button } from "@/components/ui/button"
import { toast } from "@/hooks/use-toast"
import type { Vehicle, CreateVehicleData, UpdateVehicleData } from "@/types/vehicle"

export function VehiclesPage() {
  const [isDialogOpen, setIsDialogOpen] = React.useState(false)
  const [selectedVehicle, setSelectedVehicle] = React.useState<Vehicle | undefined>()
  const { data: vehicles, isLoading } = useVehicles()
  const createVehicle = useCreateVehicle()
  const updateVehicle = useUpdateVehicle()
  const deleteVehicle = useDeleteVehicle()

  const handleAddVehicle = () => {
    setSelectedVehicle(undefined)
    setIsDialogOpen(true)
  }

  const handleEditVehicle = (vehicle: Vehicle) => {
    setSelectedVehicle(vehicle)
    setIsDialogOpen(true)
  }

  const handleSubmit = async (data: CreateVehicleData | UpdateVehicleData) => {
    try {
      if (selectedVehicle) {
        await updateVehicle.mutateAsync({ id: selectedVehicle.id, ...data })
        toast({
          title: "Success",
          description: "Vehicle updated successfully",
        })
      } else {
        await createVehicle.mutateAsync(data as CreateVehicleData)
        toast({
          title: "Success",
          description: "Vehicle created successfully",
        })
      }
      setIsDialogOpen(false)
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to save vehicle",
        variant: "destructive",
      })
    }
  }

  return (
    <div className="container mx-auto py-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Vehicles</h1>
        <Button onClick={handleAddVehicle}>Add Vehicle</Button>
      </div>

      <VehicleList onEdit={handleEditVehicle} />

      <VehicleDialog
        isOpen={isDialogOpen}
        onClose={() => setIsDialogOpen(false)}
        onSubmit={handleSubmit}
        isLoading={createVehicle.isPending || updateVehicle.isPending}
        initialData={selectedVehicle}
        title={selectedVehicle ? "Edit Vehicle" : "Add Vehicle"}
      />
    </div>
  )
}

export default VehiclesPage; 