import torch
import gc
import logging
from typing import Optional, Any
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class GPUMemoryManager:
    """
    Context manager for handling GPU memory during heavy 3D reconstruction tasks.
    Ensures cleanup happens even if errors occur.
    """
    
    @staticmethod
    def cleanup():
        """Force clean GPU cache and garbage collector"""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
        gc.collect()
        
    @staticmethod
    def log_memory_stats():
        if torch.cuda.is_available():
            logger.info(f"GPU Memory Allocated: {torch.cuda.memory_allocated() / 1024**2:.2f} MB")
            logger.info(f"GPU Memory Reserved: {torch.cuda.memory_reserved() / 1024**2:.2f} MB")

    @contextmanager
    def execution_context(self, task_name: str):
        self.log_memory_stats()
        logger.info(f"Starting GPU task: {task_name}")
        try:
            yield
        except Exception as e:
            logger.error(f"Error in {task_name}: {str(e)}")
            raise
        finally:
            logger.info(f"Finishing GPU task: {task_name}")
            self.cleanup()
            self.log_memory_stats()

