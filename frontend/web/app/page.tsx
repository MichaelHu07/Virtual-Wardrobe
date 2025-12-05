"use client"

import { useWardrobeStore } from './store'
import FileUpload from './components/FileUpload'
import { useOnnxModel } from './lib/onnx'
import { useState, useEffect } from 'react'

export default function Home() {
  const { garments, addGarment, setGarments } = useWardrobeStore()
  // Example of using the hook, model path would be a public URL
  const { loading: modelLoading } = useOnnxModel('/models/classifier.onnx')
  const [isLoading, setIsLoading] = useState(false)

  // Fetch garments on load
  useEffect(() => {
    fetch('http://localhost:8000/api/v1/garments?category=upper_body') // Just an example filter
      .then(res => res.json())
      .then(data => setGarments(data))
      .catch(err => console.error("Failed to fetch garments", err))
  }, [setGarments])

  const handleGarmentUpload = async (file: File) => {
    setIsLoading(true)
    try {
      // 1. Create FormData
      const formData = new FormData()
      formData.append('file', file)
      formData.append('category', 'unknown') // TODO: infer category

      // 2. Upload to Backend
      const res = await fetch('http://localhost:8000/api/v1/garments', {
        method: 'POST',
        body: formData,
      })
      
      if (!res.ok) throw new Error("Upload failed")

      const savedItem = await res.json()

      // 3. Add to local state
      addGarment(savedItem)
    } catch (error) {
      console.error("Upload Error", error)
      alert("Failed to upload garment")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
      {/* Upload Section */}
      <div className="col-span-1 space-y-6">
        <div className="bg-white p-6 rounded-xl shadow-sm">
          <h2 className="text-lg font-semibold mb-4">Add Garment</h2>
          <FileUpload onUpload={handleGarmentUpload} label="Upload Clothing Item" />
          {modelLoading && <p className="text-sm text-gray-500 mt-2">Loading AI Model...</p>}
          {isLoading && <p className="text-sm text-blue-500 mt-2">Uploading to server...</p>}
        </div>
      </div>

      {/* Wardrobe Grid */}
      <div className="col-span-2">
        <h2 className="text-lg font-semibold mb-4">Your Wardrobe</h2>
        {garments.length === 0 ? (
          <div className="bg-white p-12 rounded-xl border border-gray-100 text-center text-gray-400">
            No items yet. Upload a garment to get started.
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {garments.map((item) => (
              <div key={item.id} className="group relative bg-white rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow">
                <img 
                  src={item.image_url} 
                  alt={item.category} 
                  className="w-full h-48 object-cover" 
                />
                <div className="p-3">
                  <p className="font-medium text-sm truncate">{item.category}</p>
                  <p className="text-xs text-gray-500">ID: {item.id.slice(0, 8)}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
