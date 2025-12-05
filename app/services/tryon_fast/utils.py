import torch
import numpy as np
import cv2
from typing import Tuple, Union, List

class ImageUtils:
    """
    GPU-accelerated image utility class using PyTorch.
    Minimizes CPU-GPU transfers.
    """

    @staticmethod
    def preprocess_image(
        image: Union[np.ndarray, bytes], 
        target_size: Tuple[int, int] = (256, 192),
        mean: List[float] = [0.5],
        std: List[float] = [0.5],
        device: str = "cuda"
    ) -> torch.Tensor:
        """
        Converts raw image bytes or numpy array to normalized NCHW float32 tensor on GPU.
        """
        if isinstance(image, bytes):
            # Decode using OpenCV (CPU) - Unavoidable for encoded formats like PNG/JPG
            # cv2.imdecode returns BGR
            nparr = np.frombuffer(image, np.uint8)
            img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        else:
            img_np = image

        if img_np is None:
            raise ValueError("Could not decode image")

        # Resize (CPU) - cv2.resize is very fast, often faster than transferring large image to GPU then resizing
        if (img_np.shape[0], img_np.shape[1]) != target_size:
            img_np = cv2.resize(img_np, (target_size[1], target_size[0]), interpolation=cv2.INTER_LINEAR)

        # Convert to Tensor (CPU -> GPU)
        # HWC -> CHW, BGR -> RGB
        tensor = torch.from_numpy(img_np).permute(2, 0, 1).float()
        
        if device == "cuda" and torch.cuda.is_available():
            tensor = tensor.to(device, non_blocking=True)
            
        # Normalize: (x / 255.0 - mean) / std
        tensor = tensor / 255.0
        
        # Apply mean/std
        # Assume mean/std are scalar or length 1 for grayscale, 3 for RGB
        mean_tensor = torch.tensor(mean, device=device).view(-1, 1, 1)
        std_tensor = torch.tensor(std, device=device).view(-1, 1, 1)
        
        tensor = (tensor - mean_tensor) / std_tensor
        
        # Add Batch Dimension: CHW -> BCHW
        return tensor.unsqueeze(0)

    @staticmethod
    def preprocess_mask(
        mask: Union[np.ndarray, bytes], 
        target_size: Tuple[int, int] = (256, 192),
        device: str = "cuda"
    ) -> torch.Tensor:
        """
        Handles single channel masks.
        """
        if isinstance(mask, bytes):
            nparr = np.frombuffer(mask, np.uint8)
            img_np = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        else:
            img_np = mask

        if (img_np.shape[0], img_np.shape[1]) != target_size:
            img_np = cv2.resize(img_np, (target_size[1], target_size[0]), interpolation=cv2.INTER_NEAREST)

        tensor = torch.from_numpy(img_np).float().unsqueeze(0) # HW -> CHW (C=1)
        
        if device == "cuda" and torch.cuda.is_available():
            tensor = tensor.to(device, non_blocking=True)
            
        tensor = tensor / 255.0
        # Binary thresholding often helps masks
        tensor = (tensor > 0.5).float()
        
        return tensor.unsqueeze(0) # BCHW

    @staticmethod
    def tensor_to_bytes(tensor: torch.Tensor) -> bytes:
        """
        Converts GPU tensor to PNG bytes.
        Expects NCHW tensor, normalized [-1, 1] or [0, 1].
        """
        # Remove batch dim
        if tensor.dim() == 4:
            tensor = tensor.squeeze(0)
            
        # Un-normalize if needed (assuming [-1, 1] input from GANs usually)
        # Mapping [-1, 1] to [0, 255]
        tensor = (tensor * 0.5 + 0.5).clamp(0, 1) * 255.0
        
        # CHW -> HWC
        tensor = tensor.permute(1, 2, 0).byte()
        
        # GPU -> CPU
        img_np = tensor.cpu().numpy()
        
        # RGB -> BGR for OpenCV
        if img_np.shape[2] == 3:
            img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
            
        success, encoded_img = cv2.imencode('.png', img_np)
        if not success:
            raise ValueError("Failed to encode image to PNG")
            
        return encoded_img.tobytes()

    @staticmethod
    def keypoints_to_heatmap(
        keypoints: np.ndarray, 
        height: int, 
        width: int, 
        num_keypoints: int = 18, 
        sigma: float = 6.0,
        device: str = "cuda"
    ) -> torch.Tensor:
        """
        Generates Gaussian heatmaps from keypoints on GPU.
        keypoints: (N, 3) array (x, y, visibility) or (N, 2)
        Returns: (1, 18, H, W) tensor
        """
        # Create grid
        xs = torch.arange(0, width, 1, dtype=torch.float32, device=device)
        ys = torch.arange(0, height, 1, dtype=torch.float32, device=device)
        yy, xx = torch.meshgrid(ys, xs, indexing='ij')
        
        heatmaps = torch.zeros((num_keypoints, height, width), dtype=torch.float32, device=device)
        
        # Transfer keypoints to GPU
        kps_tensor = torch.tensor(keypoints, device=device)
        
        for i in range(min(len(keypoints), num_keypoints)):
            kp = kps_tensor[i]
            # Check visibility if present (x, y, v)
            if kp.shape[0] > 2 and kp[2] < 0.1:
                continue
                
            x, y = kp[0], kp[1]
            if x < 0 or y < 0: 
                continue

            # Gaussian formula
            heatmap = torch.exp(-((xx - x) ** 2 + (yy - y) ** 2) / (2 * sigma ** 2))
            heatmaps[i] = heatmap

        return heatmaps.unsqueeze(0) # Add batch dim

