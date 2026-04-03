"""
User directory management for multi-user data isolation.

This module provides functionality for managing user-specific directories,
ensuring that each user's data is isolated from others.
"""

import os
import logging
import threading
from contextlib import contextmanager
from typing import Optional, Callable, Dict

from .interfaces import IPathManager


class BaseUserDirectoryManager(IPathManager):
    """
    Manages user-specific directories for data isolation.
    
    This class implements IPathManager interface and provides:
    - User-specific input/output/temp directories
    - Thread-safe directory switching
    - Context manager for user directory operations
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        """Singleton pattern for global directory manager."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, base_user_dir: Optional[str] = None,
                 default_input_dir: Optional[str] = None,
                 default_output_dir: Optional[str] = None,
                 default_temp_dir: Optional[str] = None,
                 path_provider: Optional[Callable] = None):
        """
        Initialize the user directory manager.
        
        Args:
            base_user_dir: Base directory for user data (e.g., /app/user)
            default_input_dir: Default input directory (fallback)
            default_output_dir: Default output directory (fallback)
            default_temp_dir: Default temp directory (fallback)
            path_provider: Optional callable that provides folder_paths module
        """
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        self._base_user_dir = base_user_dir
        self._default_input_dir = default_input_dir
        self._default_output_dir = default_output_dir
        self._default_temp_dir = default_temp_dir
        self._path_provider = path_provider
        self._thread_lock = threading.Lock()
        self._initialized = True
        
        self._init_directories()
    
    def _init_directories(self):
        """Initialize default directories from ComfyUI or provided values."""
        if self._base_user_dir is None:
            try:
                if self._path_provider:
                    folder_paths = self._path_provider()
                else:
                    import folder_paths
                self._base_user_dir = os.path.join(folder_paths.base_path, "user")
            except ImportError:
                self._base_user_dir = os.path.join(os.getcwd(), "user")
        
        if self._default_input_dir is None:
            try:
                if self._path_provider:
                    folder_paths = self._path_provider()
                else:
                    import folder_paths
                self._default_input_dir = folder_paths.get_input_directory()
            except (ImportError, AttributeError):
                self._default_input_dir = os.path.join(os.getcwd(), "input")
        
        if self._default_output_dir is None:
            try:
                if self._path_provider:
                    folder_paths = self._path_provider()
                else:
                    import folder_paths
                self._default_output_dir = folder_paths.get_output_directory()
            except (ImportError, AttributeError):
                self._default_output_dir = os.path.join(os.getcwd(), "output")
        
        if self._default_temp_dir is None:
            try:
                if self._path_provider:
                    folder_paths = self._path_provider()
                else:
                    import folder_paths
                self._default_temp_dir = folder_paths.get_temp_directory()
            except (ImportError, AttributeError):
                self._default_temp_dir = os.path.join(os.getcwd(), "temp")
    
    def get_user_directory(self, user_id: str = "default") -> str:
        """
        Get the base user directory path.
        
        Args:
            user_id: The user identifier
            
        Returns:
            Absolute path to the user's base directory
        """
        if user_id == "default":
            return self._base_user_dir
        return os.path.join(self._base_user_dir, user_id)
    
    def get_input_directory(self, user_id: str = "default") -> str:
        """
        Get the input directory path for a user.
        
        Args:
            user_id: The user identifier
            
        Returns:
            Absolute path to the user's input directory
        """
        if user_id == "default":
            return self._default_input_dir
        return os.path.join(self.get_user_directory(user_id), "input")
    
    def get_output_directory(self, user_id: str = "default") -> str:
        """
        Get the output directory path for a user.
        
        Args:
            user_id: The user identifier
            
        Returns:
            Absolute path to the user's output directory
        """
        if user_id == "default":
            return self._default_output_dir
        return os.path.join(self.get_user_directory(user_id), "output")
    
    def get_temp_directory(self, user_id: str = "default") -> str:
        """
        Get the temp directory path for a user.
        
        Args:
            user_id: The user identifier
            
        Returns:
            Absolute path to the user's temp directory
        """
        if user_id == "default":
            return self._default_temp_dir
        return os.path.join(self.get_user_directory(user_id), "temp")
    
    def get_webapp_directory(self, user_id: str = "default") -> str:
        """
        Get the webapp data directory for a user.
        
        Args:
            user_id: The user identifier
            
        Returns:
            Absolute path to the user's webapp directory
        """
        return os.path.join(self.get_user_directory(user_id), "webapp")
    
    def get_task_directory(self, user_id: str = "default") -> str:
        """
        Get the task data directory for a user.
        
        Args:
            user_id: The user identifier
            
        Returns:
            Absolute path to the user's task directory
        """
        return os.path.join(self.get_user_directory(user_id), "tasks")
    
    def ensure_user_directories(self, user_id: str = "default") -> None:
        """
        Ensure all user directories exist.
        
        Args:
            user_id: The user identifier
        """
        dirs = [
            self.get_user_directory(user_id),
            self.get_input_directory(user_id),
            self.get_output_directory(user_id),
            self.get_temp_directory(user_id),
            self.get_webapp_directory(user_id),
            self.get_task_directory(user_id),
        ]
        
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
    
    @contextmanager
    def user_context(self, user_id: str):
        """
        Context manager for user-specific directory operations.
        
        This temporarily switches the global folder_paths to user-specific
        directories, and restores them when exiting the context.
        
        Args:
            user_id: The user identifier
            
        Yields:
            self for chaining operations
            
        Example:
            with user_dir_manager.user_context("user123"):
                # Operations here use user123's directories
                input_dir = folder_paths.get_input_directory()
        """
        try:
            if self._path_provider:
                folder_paths = self._path_provider()
            else:
                import folder_paths
            
            original_input = folder_paths.get_input_directory()
            original_output = folder_paths.get_output_directory()
            original_temp = folder_paths.get_temp_directory()
            
            try:
                with self._thread_lock:
                    folder_paths.set_input_directory(self.get_input_directory(user_id))
                    folder_paths.set_output_directory(self.get_output_directory(user_id))
                    folder_paths.set_temp_directory(self.get_temp_directory(user_id))
                
                yield self
                
            finally:
                with self._thread_lock:
                    folder_paths.set_input_directory(original_input)
                    folder_paths.set_output_directory(original_output)
                    folder_paths.set_temp_directory(original_temp)
                    
        except ImportError:
            logging.warning("folder_paths not available, context switching skipped")
            yield self
    
    def cleanup_user_data(self, user_id: str) -> bool:
        """
        Clean up all data for a user.
        
        Args:
            user_id: The user identifier
            
        Returns:
            True if cleanup successful
        """
        if user_id == "default":
            logging.warning("Cannot cleanup default user data")
            return False
        
        user_dir = self.get_user_directory(user_id)
        if os.path.exists(user_dir):
            try:
                import shutil
                shutil.rmtree(user_dir)
                return True
            except Exception as e:
                logging.error(f"Error cleaning up user data: {e}")
                return False
        return True
    
    def get_user_storage_usage(self, user_id: str = "default") -> Dict[str, int]:
        """
        Get storage usage for a user.
        
        Args:
            user_id: The user identifier
            
        Returns:
            Dict with storage usage for each directory
        """
        usage = {}
        
        for name, dir_func in [
            ("input", self.get_input_directory),
            ("output", self.get_output_directory),
            ("temp", self.get_temp_directory),
            ("webapp", self.get_webapp_directory),
            ("tasks", self.get_task_directory),
        ]:
            dir_path = dir_func(user_id)
            usage[name] = self._calculate_dir_size(dir_path)
        
        usage["total"] = sum(usage.values())
        return usage
    
    def _calculate_dir_size(self, dir_path: str) -> int:
        """Calculate total size of a directory in bytes."""
        if not os.path.exists(dir_path):
            return 0
        
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(dir_path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except OSError:
                        pass
        except OSError:
            pass
        
        return total_size


user_dir_manager = BaseUserDirectoryManager()
