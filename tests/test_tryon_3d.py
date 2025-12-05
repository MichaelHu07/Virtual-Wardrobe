import unittest
from unittest.mock import MagicMock, patch
import os
import shutil
import tempfile
import numpy as np
import torch
from app.services.tryon_3d.core import ReconstructionPipeline

class TestReconstructionPipeline(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @patch('app.services.tryon_3d.core.PixieWrapper')
    @patch('app.services.tryon_3d.core.PifuhdWrapper')
    def test_pipeline_flow(self, MockPifuhd, MockPixie):
        # Setup Mocks
        mock_pixie = MockPixie.return_value
        mock_pixie.predict.return_value = {"betas": torch.tensor([1.0])}
        
        mock_pifuhd = MockPifuhd.return_value
        mock_pifuhd.predict.return_value = (
            np.zeros((10, 3)), # Vertices
            np.zeros((10, 3), dtype=np.int32) # Faces
        )
        
        pipeline = ReconstructionPipeline()
        
        # Execute
        results = pipeline.process_images(
            image_paths=["dummy.jpg"],
            output_dir=self.test_dir
        )
        
        # Verify
        self.assertIn("mesh_path", results)
        self.assertTrue(os.path.exists(results["mesh_path"]))
        self.assertTrue(results["mesh_path"].endswith(".glb"))
        
        # Verify calls
        mock_pixie.load.assert_called()
        mock_pifuhd.load.assert_called()

if __name__ == '__main__':
    unittest.main()

