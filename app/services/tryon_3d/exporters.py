import trimesh
import numpy as np
import os
import cv2
from typing import Tuple

class Exporter:
    @staticmethod
    def save_glb(vertices: np.ndarray, faces: np.ndarray, output_path: str):
        """
        Exports mesh to GLB format using trimesh.
        """
        mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
        mesh.export(output_path, file_type='glb')
        return output_path

    @staticmethod
    def render_preview(vertices: np.ndarray, faces: np.ndarray, output_path: str) -> str:
        """
        Renders a simple preview of the mesh.
        Using trimesh's scene or simple projection for speed.
        """
        # Create a scene
        mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
        
        # Simple orthographic projection for preview (mock render)
        # In production, use pyrender for high quality offscreen rendering
        
        # Project to 2D
        points = vertices[:, :2]
        points = (points - points.min(0)) / (points.max(0) - points.min(0) + 1e-6)
        points = (points * 255).astype(np.int32)
        
        img = np.zeros((256, 256, 3), dtype=np.uint8)
        for p in points:
            cv2.circle(img, (p[0], p[1]), 1, (255, 255, 255), -1)
            
        cv2.imwrite(output_path, img)
        return output_path

