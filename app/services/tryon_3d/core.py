import os
import torch
import numpy as np
from app.services.tryon_3d.wrappers.models import PixieWrapper, PifuhdWrapper
from app.services.tryon_3d.utils import GPUMemoryManager
from app.services.tryon_3d.exporters import Exporter

class ReconstructionPipeline:
    def __init__(self):
        self.gpu_manager = GPUMemoryManager()
        self.pixie = PixieWrapper(checkpoint_path=os.getenv("PIXIE_PATH", "./weights/pixie.ckpt"))
        self.pifuhd = PifuhdWrapper(checkpoint_path=os.getenv("PIFUHD_PATH", "./weights/pifuhd.pth"))

    def process_images(self, image_paths: list[str], output_dir: str) -> dict:
        """
        Main pipeline execution.
        """
        results = {}
        
        # Ensure output dir exists
        os.makedirs(output_dir, exist_ok=True)

        with self.gpu_manager.execution_context("3D Reconstruction"):
            device = "cuda" if torch.cuda.is_available() else "cpu"
            
            # 1. Load Models
            self.pixie.load(device)
            self.pifuhd.load(device)
            
            # 2. Process each image (Simplification: assuming 1st image is main for now)
            # In real pipeline: fuse features from multiple views
            main_image_path = image_paths[0]
            # Load dummy tensor
            img_tensor = torch.randn(1, 3, 512, 512).to(device) 
            
            # 3. Coarse Reconstruction (SMPL-X)
            pixie_out = self.pixie.predict(img_tensor)
            
            # 4. Fine Reconstruction (PIFuHD)
            # Pass SMPL-X projection as guidance to PIFuHD (conceptual)
            vertices, faces = self.pifuhd.predict(img_tensor)
            
            # 5. Export
            glb_path = os.path.join(output_dir, "reconstruction.glb")
            preview_path = os.path.join(output_dir, "preview.png")
            
            Exporter.save_glb(vertices, faces, glb_path)
            Exporter.render_preview(vertices, faces, preview_path)
            
            results = {
                "mesh_path": glb_path,
                "preview_path": preview_path,
                "smplx_params": {k: v.cpu().numpy().tolist() for k, v in pixie_out.items()}
            }
            
        return results

