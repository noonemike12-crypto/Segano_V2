import os
from utils.logger import logger

class PathManager:
    BASE_OUTPUT_DIR = "output"
    
    SUBDIRS = {
        "image": "images",
        "audio": "audio",
        "video": "video",
        "other": "others"
    }

    @staticmethod
    def get_output_path(category, filename):
        """
        Get the full path for an output file based on its category.
        Categories: 'image', 'audio', 'video', 'other'
        """
        if category not in PathManager.SUBDIRS:
            category = "other"
            
        # Ensure base output directory exists
        if not os.path.exists(PathManager.BASE_OUTPUT_DIR):
            os.makedirs(PathManager.BASE_OUTPUT_DIR)
            logger.log("info", f"Created base output directory: {PathManager.BASE_OUTPUT_DIR}")
            
        # Ensure category subdirectory exists
        category_dir = os.path.join(PathManager.BASE_OUTPUT_DIR, PathManager.SUBDIRS[category])
        if not os.path.exists(category_dir):
            os.makedirs(category_dir)
            logger.log("info", f"Created category directory: {category_dir}")
            
        return os.path.join(category_dir, filename)

    @staticmethod
    def get_category_dir(category):
        """Get the absolute path of a category directory."""
        if category not in PathManager.SUBDIRS:
            category = "other"
        return os.path.abspath(os.path.join(PathManager.BASE_OUTPUT_DIR, PathManager.SUBDIRS[category]))
