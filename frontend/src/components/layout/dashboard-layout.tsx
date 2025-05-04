import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { cn } from '@/lib/utils'

interface DashboardLayoutProps {
  children: React.ReactNode
  className?: string
}

export function DashboardLayout({ children, className }: DashboardLayoutProps) {
  const location = useLocation()

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <Link to="/" className="flex items-center">
                <span className="text-xl font-bold text-primary">AutoAtende</span>
              </Link>
            </div>
          </div>
        </div>
      </header>

      <div className="flex">
        <aside className="w-64 bg-white shadow-sm min-h-screen">
          <nav className="mt-5 px-2">
            <Link
              to="/"
              className={cn(
                'group flex items-center px-2 py-2 text-base font-medium rounded-md',
                location.pathname === '/'
                  ? 'bg-primary text-white'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              )}
            >
              Dashboard
            </Link>
            <Link
              to="/vehicles"
              className={cn(
                'group flex items-center px-2 py-2 text-base font-medium rounded-md mt-1',
                location.pathname === '/vehicles'
                  ? 'bg-primary text-white'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              )}
            >
              Veículos
            </Link>
          </nav>
        </aside>

        <main className="flex-1">
          <div className={cn('py-6', className)}>{children}</div>
        </main>
      </div>
    </div>
  )
} 