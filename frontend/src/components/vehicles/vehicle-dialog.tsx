import * as React from "react"
import * as Dialog from "@radix-ui/react-dialog"
import { VehicleForm } from "./vehicle-form"
import type { Vehicle, CreateVehicleData, UpdateVehicleData } from "@/types/vehicle"

interface VehicleDialogProps {
  isOpen: boolean
  onClose: () => void
  onSubmit: (data: CreateVehicleData | UpdateVehicleData) => void
  isLoading: boolean
  initialData?: Vehicle
  title: string
}

export function VehicleDialog({
  isOpen,
  onClose,
  onSubmit,
  isLoading,
  initialData,
  title,
}: VehicleDialogProps) {
  return (
    <Dialog.Root open={isOpen} onOpenChange={onClose}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50" />
        <Dialog.Content className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-2xl bg-white rounded-lg shadow-lg p-6">
          <Dialog.Title className="text-xl font-semibold mb-4">{title}</Dialog.Title>
          <VehicleForm
            initialData={initialData}
            onSubmit={onSubmit}
            isLoading={isLoading}
            onCancel={onClose}
          />
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
} 