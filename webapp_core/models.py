"""
Data models for ComfyUI WebApp Core.

These models are shared between master and worker components.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum
import json
import uuid
from datetime import datetime, timezone, timedelta


BEIJING_TZ = timezone(timedelta(hours=8))


def beijing_now() -> datetime:
    """Get current time in Beijing timezone (without timezone info)."""
    return datetime.now(BEIJING_TZ).replace(tzinfo=None)


class FieldType(Enum):
    """Field type enumeration for node inputs."""
    STRING = "STRING"
    IMAGE = "IMAGE"
    AUDIO = "AUDIO"
    VIDEO = "VIDEO"
    INT = "INT"
    FLOAT = "FLOAT"
    BOOLEAN = "BOOLEAN"
    LIST = "LIST"


class WebAppStatus(Enum):
    """WebApp status enumeration."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


@dataclass
class NodeField:
    """
    Represents an editable field in a workflow node.
    
    Attributes:
        nodeId: The ID of the node in the workflow
        nodeName: The class type name of the node
        fieldName: The name of the input field
        fieldValue: The current value of the field
        fieldType: The type of the field (STRING, IMAGE, etc.)
        displayName: Human-readable display name
        description: Field description/tooltip
        fieldData: Additional data (e.g., options for LIST type)
        required: Whether the field is required
        editable: Whether the field can be edited
        fileContent: Base64 encoded file content (for file uploads)
        originalFilename: Original filename for uploaded files
    """
    nodeId: str
    nodeName: str
    fieldName: str
    fieldValue: Any
    fieldType: str
    displayName: str = ""
    description: str = ""
    fieldData: Optional[List[Any]] = None
    required: bool = True
    editable: bool = True
    fileContent: Optional[str] = None
    originalFilename: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {
            "nodeId": self.nodeId,
            "nodeName": self.nodeName,
            "fieldName": self.fieldName,
            "fieldValue": self.fieldValue,
            "fieldType": self.fieldType,
            "displayName": self.displayName or self.fieldName,
            "description": self.description,
            "required": self.required,
            "editable": self.editable
        }
        if self.fieldData:
            result["fieldData"] = self.fieldData
        if self.fileContent:
            result["fileContent"] = self.fileContent
        if self.originalFilename:
            result["originalFilename"] = self.originalFilename
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "NodeField":
        """Create from dictionary."""
        return cls(
            nodeId=data.get("nodeId", ""),
            nodeName=data.get("nodeName", ""),
            fieldName=data.get("fieldName", ""),
            fieldValue=data.get("fieldValue"),
            fieldType=data.get("fieldType", "STRING"),
            displayName=data.get("displayName", data.get("fieldName", "")),
            description=data.get("description", ""),
            fieldData=data.get("fieldData"),
            required=data.get("required", True),
            editable=data.get("editable", True),
            fileContent=data.get("fileContent"),
            originalFilename=data.get("originalFilename")
        )


@dataclass
class WebApp:
    """
    Represents a WebApp - a simplified interface for a ComfyUI workflow.
    
    Attributes:
        id: Unique identifier
        name: Display name
        description: Description text
        workflow: The original workflow JSON
        nodeInfoList: List of editable fields extracted from the workflow
        status: Current status (draft, published, archived)
        cover_image: URL to cover image
        tags: List of tags for categorization
        created_at: Creation timestamp
        updated_at: Last update timestamp
        run_mode: GPU memory mode (8g, 16g, 24g, 32g, 48g)
    """
    id: str
    name: str
    description: str = ""
    workflow: Dict[str, Any] = field(default_factory=dict)
    nodeInfoList: List[NodeField] = field(default_factory=list)
    status: str = "draft"
    cover_image: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=beijing_now)
    updated_at: datetime = field(default_factory=beijing_now)
    run_mode: str = "8g"

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "workflow": self.workflow,
            "nodeInfoList": [f.to_dict() for f in self.nodeInfoList],
            "status": self.status,
            "cover_image": self.cover_image,
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "run_mode": self.run_mode
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WebApp":
        """Create from dictionary."""
        node_info_list = [NodeField.from_dict(f) for f in data.get("nodeInfoList", [])]
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", ""),
            description=data.get("description", ""),
            workflow=data.get("workflow", {}),
            nodeInfoList=node_info_list,
            status=data.get("status", "draft"),
            cover_image=data.get("cover_image"),
            tags=data.get("tags", []),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else beijing_now(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else beijing_now(),
            run_mode=data.get("run_mode", "8g")
        )


@dataclass
class TaskResult:
    """
    Represents the result of a WebApp execution task.
    
    Attributes:
        taskId: Unique task identifier
        status: Current status (pending, running, completed, failed, cancelled)
        webappId: ID of the WebApp being executed
        webappName: Name of the WebApp
        nodeInfoList: Parameters used for this execution
        outputs: Raw output data
        outputFiles: List of output files with URLs
        tempFiles: List of temporary files used
        error: Error message if failed
        failedReason: Detailed failure reason
        progress: Execution progress (0.0 to 1.0)
        current_node: Currently executing node name
        created_at: Task creation timestamp
        started_at: Execution start timestamp
        completed_at: Execution completion timestamp
        parentTaskId: Parent task ID for retries
        retryCount: Number of retry attempts
    """
    taskId: str
    status: str
    webappId: str = ""
    webappName: str = ""
    nodeInfoList: List[NodeField] = field(default_factory=list)
    outputs: List[Dict[str, Any]] = field(default_factory=list)
    outputFiles: List[Dict[str, Any]] = field(default_factory=list)
    tempFiles: List[str] = field(default_factory=list)
    error: Optional[str] = None
    failedReason: Optional[Dict[str, Any]] = None
    progress: float = 0.0
    current_node: str = ""
    created_at: datetime = field(default_factory=beijing_now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    parentTaskId: Optional[str] = None
    retryCount: int = 0

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "taskId": self.taskId,
            "status": self.status,
            "webappId": self.webappId,
            "webappName": self.webappName,
            "nodeInfoList": [n.to_dict() for n in self.nodeInfoList] if self.nodeInfoList else [],
            "outputs": self.outputs,
            "outputFiles": self.outputFiles,
            "tempFiles": self.tempFiles,
            "error": self.error,
            "failedReason": self.failedReason,
            "progress": self.progress,
            "current_node": self.current_node,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "parentTaskId": self.parentTaskId,
            "retryCount": self.retryCount
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "TaskResult":
        """Create from dictionary."""
        node_info_list = [NodeField.from_dict(n) for n in data.get("nodeInfoList", [])]
        return cls(
            taskId=data.get("taskId", ""),
            status=data.get("status", "pending"),
            webappId=data.get("webappId", ""),
            webappName=data.get("webappName", ""),
            nodeInfoList=node_info_list,
            outputs=data.get("outputs", []),
            outputFiles=data.get("outputFiles", []),
            tempFiles=data.get("tempFiles", []),
            error=data.get("error"),
            failedReason=data.get("failedReason"),
            progress=data.get("progress", 0.0),
            current_node=data.get("current_node", ""),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else beijing_now(),
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            parentTaskId=data.get("parentTaskId"),
            retryCount=data.get("retryCount", 0)
        )
