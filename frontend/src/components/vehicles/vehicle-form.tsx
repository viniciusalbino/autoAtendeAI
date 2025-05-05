'use client'
import * as React from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select } from "@/components/ui/select"
import { useDealerships } from "@/hooks/use-dealerships"
import type { Vehicle, CreateVehicleData, UpdateVehicleData } from "@/types/vehicle"

const vehicleSchema = z.object({
  brand: z.string().min(1, "Brand is required"),
  model: z.string().min(1, "Model is required"),
  year: z.number().min(1900).max(new Date().getFullYear() + 1),
  price: z.number().min(0),
  dealershipId: z.string().min(1, "Dealership is required"),
  description: z.string().optional(),
  imageUrl: z.string().url().optional(),
})

type VehicleFormData = z.infer<typeof vehicleSchema>

interface VehicleFormProps {
  initialData?: Vehicle
  onSubmit: (data: CreateVehicleData | UpdateVehicleData) => void
  isLoading: boolean
  onCancel: () => void
}

export function VehicleForm({
  initialData,
  onSubmit,
  isLoading,
  onCancel,
}: VehicleFormProps) {
  const { data: dealerships } = useDealerships()
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<VehicleFormData>({
    resolver: zodResolver(vehicleSchema),
    defaultValues: initialData,
  })

  const onSubmitHandler = (data: VehicleFormData) => {
    onSubmit(data)
  }

  return (
    <form onSubmit={handleSubmit(onSubmitHandler)} className="space-y-6">
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="brand">Brand</Label>
          <Input
            id="brand"
            {...register("brand")}
            error={errors.brand?.message}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="model">Model</Label>
          <Input
            id="model"
            {...register("model")}
            error={errors.model?.message}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="year">Year</Label>
          <Input
            id="year"
            type="number"
            {...register("year", { valueAsNumber: true })}
            error={errors.year?.message}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="price">Price</Label>
          <Input
            id="price"
            type="number"
            step="0.01"
            {...register("price", { valueAsNumber: true })}
            error={errors.price?.message}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="dealershipId">Dealership</Label>
          <Select
            id="dealershipId"
            {...register("dealershipId")}
            error={errors.dealershipId?.message}
          >
            <option value="">Select a dealership</option>
            {dealerships?.map((dealership) => (
              <option key={dealership.id} value={dealership.id}>
                {dealership.name}
              </option>
            ))}
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="imageUrl">Image URL</Label>
          <Input
            id="imageUrl"
            type="url"
            {...register("imageUrl")}
            error={errors.imageUrl?.message}
          />
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="description">Description</Label>
        <Textarea
          id="description"
          {...register("description")}
          error={errors.description?.message}
        />
      </div>

      <div className="flex justify-end space-x-4">
        <Button
          type="button"
          variant="outline"
          onClick={onCancel}
          disabled={isLoading}
        >
          Cancel
        </Button>
        <Button type="submit" disabled={isLoading}>
          {isLoading ? "Saving..." : initialData ? "Update" : "Create"}
        </Button>
      </div>
    </form>
  )
} 