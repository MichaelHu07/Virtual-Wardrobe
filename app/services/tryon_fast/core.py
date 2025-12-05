import os
import onnxruntime as ort
import torch
import numpy as np
from typing import Dict, Union, Tuple, Optional
from app.services.tryon_fast.utils import ImageUtils

class TryOnEngine:
    """
    High-performance Inference Engine for Virtual Try-On using ONNX Runtime.
    Designed for <250ms latency on T4/A10 GPUs.
    """
    
    def __init__(self, model_path: str, device_id: int = 0):
        self.device = f"cuda:{device_id}" if torch.cuda.is_available() else "cpu"
        self.providers = [
            ('CUDAExecutionProvider', {
                'device_id': device_id,
                'arena_extend_strategy': 'kNextPowerOfTwo',
                'gpu_mem_limit': 4 * 1024 * 1024 * 1024, # 4GB Limit
                'cudnn_conv_algo_search': 'EXHAUSTIVE',
                'do_copy_in_default_stream': True,
            }),
            'CPUExecutionProvider',
        ]
        
        # Load Model
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}")

        session_options = ort.SessionOptions()
        session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        
        self.session = ort.InferenceSession(model_path, session_options, providers=self.providers)
        self.io_binding = self.session.io_binding()
        
        # Cache input/output shapes
        self.inputs_meta = self.session.get_inputs()
        self.outputs_meta = self.session.get_outputs()
        
    def _bind_input_tensor(self, name: str, tensor: torch.Tensor):
        """
        Binds a PyTorch tensor directly to ONNX Runtime input.
        Zero-copy transfer.
        """
        # Ensure tensor is contiguous and on correct device
        if not tensor.is_contiguous():
            tensor = tensor.contiguous()
            
        self.io_binding.bind_input(
            name=name,
            device_type='cuda' if 'cuda' in self.device else 'cpu',
            device_id=0,
            element_type=np.float32,
            shape=tuple(tensor.shape),
            buffer_ptr=tensor.data_ptr(),
        )

    def _bind_output_tensor(self, name: str, shape: Tuple[int, ...]):
        """
        Pre-allocates output tensor on GPU and binds it.
        """
        # Allocate output tensor on GPU
        output_tensor = torch.empty(shape, dtype=torch.float32, device=self.device)
        
        self.io_binding.bind_output(
            name=name,
            device_type='cuda' if 'cuda' in self.device else 'cpu',
            device_id=0,
            element_type=np.float32,
            shape=tuple(shape),
            buffer_ptr=output_tensor.data_ptr(),
        )
        return output_tensor

    def process(
        self,
        person_mask: Union[bytes, np.ndarray],
        garment_mask: Union[bytes, np.ndarray],
        garment_texture: Union[bytes, np.ndarray],
        pose_keypoints: np.ndarray,
    ) -> bytes:
        """
        Main inference pipeline.
        
        Args:
            person_mask: Binary mask of the person (blocking original clothes).
            garment_mask: Binary mask of the target garment.
            garment_texture: RGB image of the garment.
            pose_keypoints: (18, 2) or (18, 3) keypoints.
            
        Returns:
            PNG bytes of the warped garment/try-on result.
        """
        # 1. Preprocess Inputs (CPU/GPU hybrid -> GPU tensors)
        # Assuming model input size 256x192 (CP-VTON standard)
        H, W = 256, 192
        
        # Prepare Tensors on GPU
        t_person_mask = ImageUtils.preprocess_mask(person_mask, (H, W), self.device)
        t_garment_mask = ImageUtils.preprocess_mask(garment_mask, (H, W), self.device)
        t_garment_texture = ImageUtils.preprocess_image(garment_texture, (H, W), device=self.device)
        t_pose_heatmap = ImageUtils.keypoints_to_heatmap(pose_keypoints, H, W, device=self.device)
        
        # 2. Concatenate/Prepare Inputs matching Model Signature
        # Note: Actual CP-VTON inputs vary. 
        # Common signature: agnostic (mask+pose), cloth, cloth_mask
        # Here we assume a specific signature or concatenated input based on common optimizations.
        # We will bind 4 inputs assuming the ONNX model expects:
        # 'person_mask', 'garment_mask', 'garment_texture', 'pose_heatmap'
        
        # Use try-except to handle model input name mismatches gracefully in this scaffolding
        try:
            self._bind_input_tensor("person_mask", t_person_mask)
            self._bind_input_tensor("garment_mask", t_garment_mask)
            self._bind_input_tensor("garment_texture", t_garment_texture)
            self._bind_input_tensor("pose_heatmap", t_pose_heatmap)
        except RuntimeError as e:
            # Fallback or detailed error for debugging model mismatch
            raise ValueError(f"Model input binding failed. Check ONNX input names: {[i.name for i in self.inputs_meta]}") from e

        # 3. Bind Output
        # Assuming output is Bx3xHxW image
        output_name = self.outputs_meta[0].name
        output_shape = (1, 3, H, W)
        output_tensor = self._bind_output_tensor(output_name, output_shape)
        
        # 4. Run Inference (Synchronize for accurate timing if needed, but here we just run)
        self.session.run_with_iobinding(self.io_binding)
        
        # 5. Post-process (GPU -> PNG Bytes)
        result_bytes = ImageUtils.tensor_to_bytes(output_tensor)
        
        return result_bytes

