"""
ComfyUI WebApp Core Library

A shared library for ComfyUI WebApp functionality, designed for
distributed master-worker deployment scenarios.

Features:
- Data models for WebApp, NodeField, TaskResult
- Node mapper for workflow conversion
- User directory management for multi-user isolation
- Abstract interfaces for dependency injection

Usage:
    from webapp_core import (
        WebApp, NodeField, TaskResult,
        NodeMapper, node_mapper,
        BaseUserDirectoryManager, user_dir_manager,
        INodeRegistry, IPathManager, ITaskQueue, IExecutionEngine
    )
    
    # Create a WebApp from workflow
    webapp = node_mapper.create_webapp_from_workflow(workflow, "My App")
    
    # Use user-specific directories
    with user_dir_manager.user_context("user123"):
        # Operations use user123's directories
        pass

Installation:
    pip install comfyui-webapp-core
    
Or from git:
    pip install comfyui-webapp-core @ git+https://github.com/dibowei1980/comfy-webapp-core.git
"""

__version__ = "0.1.0"
__author__ = "dibowei"
__license__ = "Apache-2.0"

from .models import (
    FieldType,
    WebAppStatus,
    NodeField,
    WebApp,
    TaskResult,
    beijing_now,
)

from .interfaces import (
    INodeRegistry,
    IPathManager,
    ITaskQueue,
    IExecutionEngine,
    IProgressReporter,
    IStorageBackend,
)

from .node_mapper import (
    NodeMapper,
    node_mapper,
)

from .user_directory import (
    BaseUserDirectoryManager,
    user_dir_manager,
)

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__license__",
    
    # Models
    "FieldType",
    "WebAppStatus",
    "NodeField",
    "WebApp",
    "TaskResult",
    "beijing_now",
    
    # Interfaces
    "INodeRegistry",
    "IPathManager",
    "ITaskQueue",
    "IExecutionEngine",
    "IProgressReporter",
    "IStorageBackend",
    
    # Node Mapper
    "NodeMapper",
    "node_mapper",
    
    # User Directory
    "BaseUserDirectoryManager",
    "user_dir_manager",
]
