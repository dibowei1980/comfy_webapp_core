"""
Abstract interfaces for ComfyUI WebApp Core.

These interfaces allow the webapp-core library to be used in different
environments (standalone, master-worker distributed) by providing
abstraction layers for ComfyUI-specific dependencies.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
from contextlib import contextmanager


class INodeRegistry(ABC):
    """
    Abstract interface for node registry.
    
    Provides access to ComfyUI node class mappings and metadata.
    Implementation should wrap ComfyUI's nodes.NODE_CLASS_MAPPINGS.
    """
    
    @abstractmethod
    def get_node_class_mappings(self) -> Dict[str, type]:
        """
        Get the mapping of node class names to node classes.
        
        Returns:
            Dict mapping class_type string to node class
        """
        pass
    
    @abstractmethod
    def get_node_display_names(self) -> Dict[str, str]:
        """
        Get the mapping of node class names to display names.
        
        Returns:
            Dict mapping class_type string to display name
        """
        pass
    
    def get_node_class(self, class_name: str) -> Optional[type]:
        """
        Get a specific node class by name.
        
        Args:
            class_name: The node class type name
            
        Returns:
            The node class or None if not found
        """
        mappings = self.get_node_class_mappings()
        return mappings.get(class_name)
    
    def get_node_info(self, class_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a node class.
        
        Args:
            class_name: The node class type name
            
        Returns:
            Dict with node information or None if not found
        """
        node_class = self.get_node_class(class_name)
        if not node_class:
            return None
        
        info = {
            "name": class_name,
            "display_name": getattr(node_class, "DISPLAY_NAME", class_name),
            "category": getattr(node_class, "CATEGORY", "unknown"),
            "description": getattr(node_class, "DESCRIPTION", ""),
            "input_types": {},
            "output_types": [],
            "output_names": [],
        }
        
        if hasattr(node_class, "INPUT_TYPES"):
            try:
                input_types = node_class.INPUT_TYPES()
                info["input_types"] = input_types
            except Exception:
                pass
        
        if hasattr(node_class, "RETURN_TYPES"):
            info["output_types"] = list(node_class.RETURN_TYPES) if node_class.RETURN_TYPES else []
        
        if hasattr(node_class, "OUTPUT_TOOLTIPS"):
            info["output_tooltips"] = list(node_class.OUTPUT_TOOLTIPS) if node_class.OUTPUT_TOOLTIPS else []
        
        if hasattr(node_class, "OUTPUT_NODE"):
            info["is_output_node"] = node_class.OUTPUT_NODE
        
        return info


class IPathManager(ABC):
    """
    Abstract interface for path management.
    
    Provides access to input/output/temp directories with user isolation support.
    Implementation should wrap ComfyUI's folder_paths module.
    """
    
    @abstractmethod
    def get_input_directory(self, user_id: str = "default") -> str:
        """
        Get the input directory path for a user.
        
        Args:
            user_id: The user identifier
            
        Returns:
            Absolute path to the user's input directory
        """
        pass
    
    @abstractmethod
    def get_output_directory(self, user_id: str = "default") -> str:
        """
        Get the output directory path for a user.
        
        Args:
            user_id: The user identifier
            
        Returns:
            Absolute path to the user's output directory
        """
        pass
    
    @abstractmethod
    def get_temp_directory(self, user_id: str = "default") -> str:
        """
        Get the temp directory path for a user.
        
        Args:
            user_id: The user identifier
            
        Returns:
            Absolute path to the user's temp directory
        """
        pass
    
    @abstractmethod
    def get_user_directory(self, user_id: str = "default") -> str:
        """
        Get the base user directory path.
        
        Args:
            user_id: The user identifier
            
        Returns:
            Absolute path to the user's base directory
        """
        pass
    
    @contextmanager
    def user_context(self, user_id: str):
        """
        Context manager for user-specific directory operations.
        
        Args:
            user_id: The user identifier
            
        Yields:
            self for chaining operations
        """
        yield self
    
    def ensure_user_directories(self, user_id: str = "default") -> None:
        """
        Ensure all user directories exist.
        
        Args:
            user_id: The user identifier
        """
        import os
        for dir_func in [self.get_input_directory, self.get_output_directory, 
                         self.get_temp_directory, self.get_user_directory]:
            path = dir_func(user_id)
            os.makedirs(path, exist_ok=True)


class ITaskQueue(ABC):
    """
    Abstract interface for task queue management.
    
    Provides methods for submitting and managing tasks.
    In distributed mode, this would interface with a message queue.
    """
    
    @abstractmethod
    async def submit(self, task_id: str, prompt: Dict[str, Any], 
                     extra_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Submit a task to the queue.
        
        Args:
            task_id: Unique task identifier
            prompt: The workflow prompt in API format
            extra_data: Additional data for execution
            
        Returns:
            True if submission successful
        """
        pass
    
    @abstractmethod
    async def get_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the current status of a task.
        
        Args:
            task_id: The task identifier
            
        Returns:
            Task status dict or None if not found
        """
        pass
    
    @abstractmethod
    async def cancel(self, task_id: str) -> bool:
        """
        Cancel a pending or running task.
        
        Args:
            task_id: The task identifier
            
        Returns:
            True if cancellation successful
        """
        pass
    
    @abstractmethod
    async def get_queue_size(self) -> int:
        """
        Get the current queue size.
        
        Returns:
            Number of pending tasks
        """
        pass


class IExecutionEngine(ABC):
    """
    Abstract interface for execution engine.
    
    Provides methods for validating and executing prompts.
    Implementation should wrap ComfyUI's execution module.
    """
    
    @abstractmethod
    async def validate_prompt(self, prompt_id: str, prompt: Dict[str, Any]) -> Tuple[bool, Optional[Dict], Optional[List], Optional[Dict]]:
        """
        Validate a prompt before execution.
        
        Args:
            prompt_id: Unique identifier for the prompt
            prompt: The workflow prompt in API format
            
        Returns:
            Tuple of (is_valid, error_info, outputs_to_execute, node_errors)
        """
        pass
    
    @abstractmethod
    async def execute(self, prompt: Dict[str, Any], 
                      extra_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a prompt.
        
        Args:
            prompt: The workflow prompt in API format
            extra_data: Additional execution data
            
        Returns:
            Execution result dict
        """
        pass
    
    @abstractmethod
    def interrupt(self) -> None:
        """
        Interrupt current execution.
        """
        pass


class IProgressReporter(ABC):
    """
    Abstract interface for progress reporting.
    
    Used by workers to report progress back to master.
    """
    
    @abstractmethod
    async def report_progress(self, task_id: str, progress: float, 
                              current_node: str = "", message: str = "") -> None:
        """
        Report task progress.
        
        Args:
            task_id: The task identifier
            progress: Progress value (0.0 to 1.0)
            current_node: Currently executing node
            message: Optional status message
        """
        pass
    
    @abstractmethod
    async def report_completion(self, task_id: str, result: Dict[str, Any]) -> None:
        """
        Report task completion.
        
        Args:
            task_id: The task identifier
            result: Execution result
        """
        pass
    
    @abstractmethod
    async def report_error(self, task_id: str, error: str, 
                           details: Optional[Dict[str, Any]] = None) -> None:
        """
        Report task error.
        
        Args:
            task_id: The task identifier
            error: Error message
            details: Optional error details
        """
        pass


class IStorageBackend(ABC):
    """
    Abstract interface for storage backend.
    
    Provides methods for persisting and retrieving webapp and task data.
    Can be implemented with filesystem, database, or cloud storage.
    """
    
    @abstractmethod
    async def save_webapp(self, webapp_id: str, data: Dict[str, Any], 
                          user_id: str = "default") -> bool:
        """
        Save webapp data.
        
        Args:
            webapp_id: The webapp identifier
            data: Webapp data dict
            user_id: The user identifier
            
        Returns:
            True if save successful
        """
        pass
    
    @abstractmethod
    async def load_webapp(self, webapp_id: str, 
                          user_id: str = "default") -> Optional[Dict[str, Any]]:
        """
        Load webapp data.
        
        Args:
            webapp_id: The webapp identifier
            user_id: The user identifier
            
        Returns:
            Webapp data dict or None if not found
        """
        pass
    
    @abstractmethod
    async def delete_webapp(self, webapp_id: str, 
                            user_id: str = "default") -> bool:
        """
        Delete webapp data.
        
        Args:
            webapp_id: The webapp identifier
            user_id: The user identifier
            
        Returns:
            True if deletion successful
        """
        pass
    
    @abstractmethod
    async def list_webapps(self, user_id: str = "default", 
                           status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all webapps for a user.
        
        Args:
            user_id: The user identifier
            status: Optional status filter
            
        Returns:
            List of webapp data dicts
        """
        pass
    
    @abstractmethod
    async def save_task(self, task_id: str, data: Dict[str, Any], 
                        user_id: str = "default") -> bool:
        """
        Save task data.
        
        Args:
            task_id: The task identifier
            data: Task data dict
            user_id: The user identifier
            
        Returns:
            True if save successful
        """
        pass
    
    @abstractmethod
    async def load_task(self, task_id: str, 
                        user_id: str = "default") -> Optional[Dict[str, Any]]:
        """
        Load task data.
        
        Args:
            task_id: The task identifier
            user_id: The user identifier
            
        Returns:
            Task data dict or None if not found
        """
        pass
    
    @abstractmethod
    async def list_tasks(self, user_id: str = "default", 
                         status: Optional[str] = None,
                         limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List tasks for a user.
        
        Args:
            user_id: The user identifier
            status: Optional status filter
            limit: Maximum number of results
            offset: Result offset for pagination
            
        Returns:
            List of task data dicts
        """
        pass
