"use client"

import { useWardrobeStore } from './store'
import FileUpload from './components/FileUpload'
import { useOnnxModel } from './lib/onnx'

export default function Home() {
  const { garments, addGarment } = useWardrobeStore()
  // Example of using the hook, model path would be a public URL
  const { loading: modelLoading } = useOnnxModel('/models/classifier.onnx')

  const handleGarmentUpload = async (file: File) => {
    // In production, upload to backend (S3/MinIO) via API
    // Here we just simulate local state update
    const mockUrl = URL.createObjectURL(file)
    addGarment({
      id: Date.now(),
      image_url: mockUrl,
      name: file.name,
      category: 'Unclassified'
    })
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
      {/* Upload Section */}
      <div className="col-span-1 space-y-6">
        <div className="bg-white p-6 rounded-xl shadow-sm">
          <h2 className="text-lg font-semibold mb-4">Add Garment</h2>
          <FileUpload onUpload={handleGarmentUpload} label="Upload Clothing Item" />
          {modelLoading && <p className="text-sm text-gray-500 mt-2">Loading AI Model...</p>}
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
                  alt={item.name} 
                  className="w-full h-48 object-cover" 
                />
                <div className="p-3">
                  <p className="font-medium text-sm truncate">{item.name}</p>
                  <p className="text-xs text-gray-500">{item.category}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

