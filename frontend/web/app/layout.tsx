import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Virtual Wardrobe',
  description: 'AI-Powered Virtual Try-On',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <main className="min-h-screen bg-gray-50 text-gray-900">
          <nav className="p-4 bg-white shadow-sm flex justify-between items-center">
            <h1 className="text-xl font-bold text-primary">Virtual Wardrobe</h1>
            <div className="space-x-4">
              <button className="text-sm font-medium hover:text-primary">Dashboard</button>
              <button className="text-sm font-medium hover:text-primary">Profile</button>
            </div>
          </nav>
          <div className="container mx-auto p-8">
            {children}
          </div>
        </main>
      </body>
    </html>
  )
}

