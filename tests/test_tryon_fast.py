import unittest
import numpy as np
import torch
import os
from unittest.mock import MagicMock, patch
from app.services.tryon_fast.utils import ImageUtils
from app.services.tryon_fast.core import TryOnEngine

class TestImageUtils(unittest.TestCase):
    def test_keypoints_to_heatmap(self):
        # 1 Keypoint at (10, 10)
        kps = np.array([[10, 10, 1]])
        H, W = 64, 64
        
        device = "cpu" # Test on CPU for CI compatibility
        heatmap = ImageUtils.keypoints_to_heatmap(kps, H, W, num_keypoints=1, device=device)
        
        self.assertEqual(heatmap.shape, (1, 1, 64, 64))
        self.assertTrue(heatmap[0, 0, 10, 10] > 0.9) # Peak at center
        self.assertTrue(heatmap[0, 0, 0, 0] < 0.1)   # Low far away

    def test_preprocess_image(self):
        # Create a random image
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        
        device = "cpu"
        tensor = ImageUtils.preprocess_image(img, target_size=(256, 192), device=device)
        
        self.assertEqual(tensor.shape, (1, 3, 256, 192))
        self.assertIsInstance(tensor, torch.Tensor)

class TestTryOnEngine(unittest.TestCase):
    
    @patch('app.services.tryon_fast.core.ort.InferenceSession')
    def test_engine_initialization(self, mock_session):
        # Mock ONNX session
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        
        # Mock inputs/outputs metadata
        input_meta = MagicMock()
        input_meta.name = "test_input"
        mock_session_instance.get_inputs.return_value = [input_meta]
        
        output_meta = MagicMock()
        output_meta.name = "test_output"
        mock_session_instance.get_outputs.return_value = [output_meta]
        
        # Create a dummy file to bypass existence check
        with open("dummy_model.onnx", "w") as f:
            f.write("dummy")
            
        try:
            engine = TryOnEngine("dummy_model.onnx", device_id=0)
            self.assertIsNotNone(engine)
        finally:
            if os.path.exists("dummy_model.onnx"):
                os.remove("dummy_model.onnx")

if __name__ == '__main__':
    unittest.main()

