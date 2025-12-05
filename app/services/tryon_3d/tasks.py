from app.services.tryon_3d.worker import celery_app
from app.services.tryon_3d.core import ReconstructionPipeline
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="reconstruct_3d")
def reconstruct_3d_task(self, image_paths: list[str], output_dir: str):
    """
    Celery task wrapper for 3D reconstruction.
    """
    try:
        logger.info(f"Starting reconstruction for {len(image_paths)} images")
        
        # Instantiate pipeline inside task to ensure fresh GPU state
        pipeline = ReconstructionPipeline()
        result = pipeline.process_images(image_paths, output_dir)
        
        return {
            "status": "success",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Reconstruction failed: {str(e)}")
        # Clean up if needed
        return {
            "status": "failed",
            "error": str(e)
        }

