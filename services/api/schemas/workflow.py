from enum import Enum
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    api: str


class ApiError(BaseModel):
    detail: str


class ProjectStatus(BaseModel):
    validation: str
    generation: str
    build: str
    last_run: str


class RuntimeItem(BaseModel):
    ready: bool
    detail: Optional[str] = None


class GeneratorRuntime(RuntimeItem):
    path: str


class WiresharkRuntime(BaseModel):
    status: str
    url: Optional[str] = None


class RuntimeReadiness(BaseModel):
    api: RuntimeItem
    docker: RuntimeItem
    wireshark: WiresharkRuntime
    generators: Dict[str, GeneratorRuntime]


class CaptureFile(BaseModel):
    name: str
    bytes: int
    wireshark_path: Optional[str] = None


class CaptureSession(BaseModel):
    wireshark_url: Optional[str] = None
    wireshark_root: Optional[str] = None
    display_filter: Optional[str] = None
    files: List[CaptureFile] = Field(default_factory=list)


class ContainerState(BaseModel):
    name: str
    status: str


class RunSummary(BaseModel):
    id: str
    project_id: str
    scenario_id: str
    scenario_name: str
    status: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    capture: CaptureSession = Field(default_factory=CaptureSession)
    captures: List[CaptureFile] = Field(default_factory=list)
    containers: Dict[str, ContainerState] = Field(default_factory=dict)


class ProjectSummary(BaseModel):
    id: str
    name: str
    document_count: int = 0
    node_count: int = 0
    scenario_count: int = 0
    latest_status: ProjectStatus


class WorkbenchOverview(BaseModel):
    projects: List[ProjectSummary] = Field(default_factory=list)
    active_runs: List[RunSummary] = Field(default_factory=list)
    recent_runs: List[RunSummary] = Field(default_factory=list)
    runtime: RuntimeReadiness


class StarterPreset(BaseModel):
    id: str
    name: str
    source_example: Optional[str] = None
    description: Optional[str] = None
    category: str = "sample"
    runnable: bool = False
    default_project_id: Optional[str] = None
    default_name: Optional[str] = None


class ProjectCollection(BaseModel):
    projects: List[ProjectSummary] = Field(default_factory=list)
    presets: List[StarterPreset] = Field(default_factory=list)


class ProjectCreateRequest(BaseModel):
    project_id: str
    name: str
    preset_id: Optional[str] = None
    source_example: Optional[str] = None


class ProjectImportRequest(BaseModel):
    source_path: str


class DocumentRef(BaseModel):
    id: str
    name: str
    kind: str


class DocumentFile(DocumentRef):
    content: str


class DocumentUpdate(BaseModel):
    content: str


class DocumentWriteResult(BaseModel):
    id: str
    name: str
    bytes: int


class Diagnostic(BaseModel):
    severity: str
    file: str
    message: str


class InterfaceSummary(BaseModel):
    document: str
    package: Optional[str] = None
    name: Optional[str] = None
    methods: List[str] = Field(default_factory=list)
    events: List[str] = Field(default_factory=list)
    structs: List[str] = Field(default_factory=list)
    enums: List[str] = Field(default_factory=list)


class DeploymentSummary(BaseModel):
    document: str
    ids: Dict[str, List[str]] = Field(default_factory=dict)
    reliable_ports: List[str] = Field(default_factory=list)


class InterfaceIndex(BaseModel):
    interfaces: List[InterfaceSummary] = Field(default_factory=list)
    deployments: List[DeploymentSummary] = Field(default_factory=list)


class ValidationResult(BaseModel):
    valid: bool
    diagnostics: List[Diagnostic] = Field(default_factory=list)
    interface_index: InterfaceIndex = Field(default_factory=InterfaceIndex)


class AuthoringWorkspace(BaseModel):
    project_id: str
    documents: List[DocumentRef] = Field(default_factory=list)
    validation_status: str
    diagnostics: List[Diagnostic] = Field(default_factory=list)
    interface_index: Optional[InterfaceIndex] = None


class NetworkSettings(BaseModel):
    service_discovery: bool = True
    multicast: str = "224.224.224.245"
    sd_port: int = 30490


class TopologyNode(BaseModel):
    id: str
    type: str
    interface: str
    app_name: str


class ReadinessGate(BaseModel):
    id: str
    label: str
    status: str
    ready: bool
    detail: str


class RecommendedAction(BaseModel):
    kind: Literal["author", "build", "simulate", "inspect"]
    title: str
    detail: str


class ProjectOverview(BaseModel):
    id: str
    name: str
    source_example: Optional[str] = None
    status: ProjectStatus
    readiness: int
    readiness_gates: List[ReadinessGate] = Field(default_factory=list)
    recommended_action: RecommendedAction
    network: NetworkSettings
    nodes: List[TopologyNode] = Field(default_factory=list)
    interface_index: Optional[InterfaceIndex] = None
    documents: List[DocumentRef] = Field(default_factory=list)
    scenario_count: int = 0
    recent_runs: List[RunSummary] = Field(default_factory=list)


class PipelineStage(BaseModel):
    id: Literal["validation", "generation", "build"]
    label: str
    status: str
    ready: bool
    detail: str
    warnings: List[str] = Field(default_factory=list)


class PipelineOverview(BaseModel):
    project_id: str
    status: ProjectStatus
    stages: List[PipelineStage] = Field(default_factory=list)


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskResponse(BaseModel):
    task_id: str
    status: TaskStatus
    message: str


class ProjectBuildRequest(BaseModel):
    clean: bool = False
    generate: bool = True


class Job(BaseModel):
    task_id: str
    type: str
    status: str
    project_id: Optional[str] = None
    log: str = ""
    error: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class JobEvent(BaseModel):
    type: Literal["job.log", "job.status"]
    job_id: str
    text: Optional[str] = None
    status: Optional[str] = None
    error: Optional[str] = None


class Scenario(BaseModel):
    id: str
    name: str
    file: str
    steps: List[Dict[str, Any]] = Field(default_factory=list)


class RunBlocker(BaseModel):
    id: str
    message: str


class SimulationWorkspace(BaseModel):
    project_id: str
    scenarios: List[Scenario] = Field(default_factory=list)
    blockers: List[RunBlocker] = Field(default_factory=list)
    nodes: List[TopologyNode] = Field(default_factory=list)
    recent_runs: List[RunSummary] = Field(default_factory=list)


class SimulationStartRequest(BaseModel):
    scenario_id: str


class RunEvent(BaseModel):
    type: str
    run_id: Optional[str] = None
    status: Optional[str] = None
    detail: Optional[str] = None
    node_id: Optional[str] = None
    timestamp: Optional[str] = None


class RunDetail(RunSummary):
    events: List[RunEvent] = Field(default_factory=list)
    scenario_capabilities: List[str] = Field(default_factory=list)


class ArtifactFile(BaseModel):
    name: str
    bytes: int


class RunArtifacts(BaseModel):
    run_id: str
    files: List[ArtifactFile] = Field(default_factory=list)
    capture: CaptureSession = Field(default_factory=CaptureSession)
    compose_log: str = ""
    capture_log: str = ""
    captures: List[CaptureFile] = Field(default_factory=list)


class ScenarioResult(BaseModel):
    status: str
    detail: str
    limitations: List[str] = Field(default_factory=list)


class NodeLifecycle(BaseModel):
    node_id: str
    status: str
    timestamp: Optional[str] = None


class EvidenceState(BaseModel):
    capture_status: str
    capture_count: int
    wireshark_url: Optional[str] = None
    packet_snapshot_saved: bool
    someip_observation: Literal["captured", "unknown", "unavailable"]
    service_discovery_observation: Literal["captured", "unknown", "unavailable"]


class RunInspection(BaseModel):
    run: RunDetail
    scenario_result: ScenarioResult
    node_lifecycle: List[NodeLifecycle] = Field(default_factory=list)
    evidence: EvidenceState
    timeline: List[RunEvent] = Field(default_factory=list)
    artifacts: RunArtifacts
