import { useState, useCallback } from 'react';
import { compressImage } from '../utils/compression';
import { Upload, Loader2 } from 'lucide-react';

interface FileUploadProps {
  onUpload: (file: File) => Promise<void>;
  label?: string;
}

export default function FileUpload({ onUpload, label = "Upload Image" }: FileUploadProps) {
  const [isUploading, setIsUploading] = useState(false);

  const handleFileChange = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setIsUploading(true);
      try {
        const file = e.target.files[0];
        const compressed = await compressImage(file);
        await onUpload(compressed);
      } catch (error) {
        console.error("Upload error", error);
      } finally {
        setIsUploading(false);
      }
    }
  }, [onUpload]);

  return (
    <div className="flex flex-col items-center gap-4 p-6 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary transition-colors">
      <label className="cursor-pointer flex flex-col items-center">
        {isUploading ? (
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
        ) : (
          <Upload className="w-8 h-8 text-gray-500" />
        )}
        <span className="mt-2 text-sm text-gray-600">{label}</span>
        <input 
          type="file" 
          className="hidden" 
          accept="image/*" 
          onChange={handleFileChange} 
          disabled={isUploading} 
        />
      </label>
    </div>
  );
}

