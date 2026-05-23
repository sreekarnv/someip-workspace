import { baseApi as api } from "../store/base-api";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    getWorkbenchOverview: build.query<
      GetWorkbenchOverviewApiResponse,
      GetWorkbenchOverviewApiArg
    >({
      query: () => ({ url: `/api/v1/workbench/overview` }),
    }),
    getProjects: build.query<GetProjectsApiResponse, GetProjectsApiArg>({
      query: () => ({ url: `/api/v1/projects` }),
    }),
    createProject: build.mutation<
      CreateProjectApiResponse,
      CreateProjectApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v1/projects`,
        method: "POST",
        body: queryArg,
      }),
    }),
    importProject: build.mutation<
      ImportProjectApiResponse,
      ImportProjectApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v1/projects/import`,
        method: "POST",
        body: queryArg,
      }),
    }),
    getProjectOverview: build.query<
      GetProjectOverviewApiResponse,
      GetProjectOverviewApiArg
    >({
      query: (queryArg) => ({ url: `/api/v1/projects/${queryArg}/overview` }),
    }),
    getProjectAuthoring: build.query<
      GetProjectAuthoringApiResponse,
      GetProjectAuthoringApiArg
    >({
      query: (queryArg) => ({ url: `/api/v1/projects/${queryArg}/authoring` }),
    }),
    getProjectDocument: build.query<
      GetProjectDocumentApiResponse,
      GetProjectDocumentApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v1/projects/${queryArg.projectId}/documents/${queryArg.documentId}`,
      }),
    }),
    saveProjectDocument: build.mutation<
      SaveProjectDocumentApiResponse,
      SaveProjectDocumentApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v1/projects/${queryArg.projectId}/documents/${queryArg.documentId}`,
        method: "PUT",
        body: queryArg.documentUpdate,
      }),
    }),
    validateProjectAuthoring: build.mutation<
      ValidateProjectAuthoringApiResponse,
      ValidateProjectAuthoringApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v1/projects/${queryArg}/authoring/validate`,
        method: "POST",
      }),
    }),
    getProjectPipeline: build.query<
      GetProjectPipelineApiResponse,
      GetProjectPipelineApiArg
    >({
      query: (queryArg) => ({ url: `/api/v1/projects/${queryArg}/pipeline` }),
    }),
    generateProjectArtifacts: build.mutation<
      GenerateProjectArtifactsApiResponse,
      GenerateProjectArtifactsApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v1/projects/${queryArg}/pipeline/generate`,
        method: "POST",
      }),
    }),
    buildProjectNodes: build.mutation<
      BuildProjectNodesApiResponse,
      BuildProjectNodesApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v1/projects/${queryArg.projectId}/pipeline/build`,
        method: "POST",
        body: queryArg.projectBuildRequest,
      }),
    }),
    getJob: build.query<GetJobApiResponse, GetJobApiArg>({
      query: (queryArg) => ({ url: `/api/v1/jobs/${queryArg}` }),
    }),
    getProjectSimulations: build.query<
      GetProjectSimulationsApiResponse,
      GetProjectSimulationsApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v1/projects/${queryArg}/simulations`,
      }),
    }),
    startProjectSimulation: build.mutation<
      StartProjectSimulationApiResponse,
      StartProjectSimulationApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v1/projects/${queryArg.projectId}/simulations`,
        method: "POST",
        body: queryArg.simulationStartRequest,
      }),
    }),
    getProjectRuns: build.query<
      GetProjectRunsApiResponse,
      GetProjectRunsApiArg
    >({
      query: (queryArg) => ({ url: `/api/v1/projects/${queryArg}/runs` }),
    }),
    getRun: build.query<GetRunApiResponse, GetRunApiArg>({
      query: (queryArg) => ({ url: `/api/v1/runs/${queryArg}` }),
    }),
    stopRun: build.mutation<StopRunApiResponse, StopRunApiArg>({
      query: (queryArg) => ({
        url: `/api/v1/runs/${queryArg}/stop`,
        method: "POST",
      }),
    }),
    getRunInspection: build.query<
      GetRunInspectionApiResponse,
      GetRunInspectionApiArg
    >({
      query: (queryArg) => ({ url: `/api/v1/runs/${queryArg}/inspection` }),
    }),
    downloadRunCapture: build.query<
      DownloadRunCaptureApiResponse,
      DownloadRunCaptureApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v1/runs/${queryArg.runId}/captures/${queryArg.captureName}`,
      }),
    }),
    getHealth: build.query<GetHealthApiResponse, GetHealthApiArg>({
      query: () => ({ url: `/health` }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as workflowApi };
export type GetWorkbenchOverviewApiResponse =
  /** status 200 Successful Response */ WorkbenchOverview;
export type GetWorkbenchOverviewApiArg = void;
export type GetProjectsApiResponse =
  /** status 200 Successful Response */ ProjectCollection;
export type GetProjectsApiArg = void;
export type CreateProjectApiResponse =
  /** status 200 Successful Response */ ProjectOverview;
export type CreateProjectApiArg = ProjectCreateRequest;
export type ImportProjectApiResponse =
  /** status 200 Successful Response */ ProjectOverview;
export type ImportProjectApiArg = ProjectImportRequest;
export type GetProjectOverviewApiResponse =
  /** status 200 Successful Response */ ProjectOverview;
export type GetProjectOverviewApiArg = string;
export type GetProjectAuthoringApiResponse =
  /** status 200 Successful Response */ AuthoringWorkspace;
export type GetProjectAuthoringApiArg = string;
export type GetProjectDocumentApiResponse =
  /** status 200 Successful Response */ DocumentFile;
export type GetProjectDocumentApiArg = {
  projectId: string;
  documentId: string;
};
export type SaveProjectDocumentApiResponse =
  /** status 200 Successful Response */ DocumentWriteResult;
export type SaveProjectDocumentApiArg = {
  projectId: string;
  documentId: string;
  documentUpdate: DocumentUpdate;
};
export type ValidateProjectAuthoringApiResponse =
  /** status 200 Successful Response */ ValidationResult;
export type ValidateProjectAuthoringApiArg = string;
export type GetProjectPipelineApiResponse =
  /** status 200 Successful Response */ PipelineOverview;
export type GetProjectPipelineApiArg = string;
export type GenerateProjectArtifactsApiResponse =
  /** status 200 Successful Response */ TaskResponse;
export type GenerateProjectArtifactsApiArg = string;
export type BuildProjectNodesApiResponse =
  /** status 200 Successful Response */ TaskResponse;
export type BuildProjectNodesApiArg = {
  projectId: string;
  projectBuildRequest: ProjectBuildRequest;
};
export type GetJobApiResponse = /** status 200 Successful Response */ Job;
export type GetJobApiArg = string;
export type GetProjectSimulationsApiResponse =
  /** status 200 Successful Response */ SimulationWorkspace;
export type GetProjectSimulationsApiArg = string;
export type StartProjectSimulationApiResponse =
  /** status 200 Successful Response */ RunDetail;
export type StartProjectSimulationApiArg = {
  projectId: string;
  simulationStartRequest: SimulationStartRequest;
};
export type GetProjectRunsApiResponse =
  /** status 200 Successful Response */ RunSummary[];
export type GetProjectRunsApiArg = string;
export type GetRunApiResponse = /** status 200 Successful Response */ RunDetail;
export type GetRunApiArg = string;
export type StopRunApiResponse =
  /** status 200 Successful Response */ RunDetail;
export type StopRunApiArg = string;
export type GetRunInspectionApiResponse =
  /** status 200 Successful Response */ RunInspection;
export type GetRunInspectionApiArg = string;
export type DownloadRunCaptureApiResponse =
  /** status 200 Successful Response */ any;
export type DownloadRunCaptureApiArg = {
  runId: string;
  captureName: string;
};
export type GetHealthApiResponse =
  /** status 200 Successful Response */ HealthResponse;
export type GetHealthApiArg = void;
export type ProjectStatus = {
  validation: string;
  generation: string;
  build: string;
  last_run: string;
};
export type ProjectSummary = {
  id: string;
  name: string;
  document_count?: number;
  node_count?: number;
  scenario_count?: number;
  latest_status: ProjectStatus;
};
export type CaptureFile = {
  name: string;
  bytes: number;
  wireshark_path?: string | null;
};
export type CaptureSession = {
  wireshark_url?: string | null;
  wireshark_root?: string | null;
  display_filter?: string | null;
  files?: CaptureFile[];
};
export type ContainerState = {
  name: string;
  status: string;
};
export type RunSummary = {
  id: string;
  project_id: string;
  scenario_id: string;
  scenario_name: string;
  status: string;
  created_at?: string | null;
  updated_at?: string | null;
  capture?: CaptureSession;
  captures?: CaptureFile[];
  containers?: {
    [key: string]: ContainerState;
  };
};
export type RuntimeItem = {
  ready: boolean;
  detail?: string | null;
};
export type WiresharkRuntime = {
  status: string;
  url?: string | null;
};
export type GeneratorRuntime = {
  ready: boolean;
  detail?: string | null;
  path: string;
};
export type RuntimeReadiness = {
  api: RuntimeItem;
  docker: RuntimeItem;
  vsomeip: RuntimeItem;
  wireshark: WiresharkRuntime;
  generators: {
    [key: string]: GeneratorRuntime;
  };
};
export type WorkbenchOverview = {
  projects?: ProjectSummary[];
  active_runs?: RunSummary[];
  recent_runs?: RunSummary[];
  runtime: RuntimeReadiness;
};
export type StarterPreset = {
  id: string;
  name: string;
  description?: string | null;
  category?: string;
  runnable?: boolean;
  runtime_kind?: "generated-vsomeip";
  default_project_id?: string | null;
  default_name?: string | null;
};
export type ProjectCollection = {
  projects?: ProjectSummary[];
  presets?: StarterPreset[];
};
export type ReadinessGate = {
  id: string;
  label: string;
  status: string;
  ready: boolean;
  detail: string;
};
export type RecommendedAction = {
  kind: "author" | "build" | "simulate" | "inspect";
  title: string;
  detail: string;
};
export type NetworkSettings = {
  service_discovery?: boolean;
  multicast?: string;
  sd_port?: number;
};
export type TopologyNode = {
  id: string;
  type: string;
  interface: string;
  app_name: string;
};
export type InterfaceSummary = {
  document: string;
  package?: string | null;
  name?: string | null;
  methods?: string[];
  events?: string[];
  structs?: string[];
  enums?: string[];
};
export type DeploymentSummary = {
  document: string;
  ids?: {
    [key: string]: string[];
  };
  reliable_ports?: string[];
};
export type InterfaceIndex = {
  interfaces?: InterfaceSummary[];
  deployments?: DeploymentSummary[];
};
export type DocumentRef = {
  id: string;
  name: string;
  kind: string;
};
export type ProjectOverview = {
  id: string;
  name: string;
  runtime_kind?: "generated-vsomeip";
  status: ProjectStatus;
  readiness: number;
  readiness_gates?: ReadinessGate[];
  recommended_action: RecommendedAction;
  network: NetworkSettings;
  nodes?: TopologyNode[];
  interface_index?: InterfaceIndex | null;
  documents?: DocumentRef[];
  scenario_count?: number;
  recent_runs?: RunSummary[];
};
export type ApiError = {
  detail: string;
};
export type ValidationError = {
  loc: (string | number)[];
  msg: string;
  type: string;
  input?: any;
  ctx?: object;
};
export type HttpValidationError = {
  detail?: ValidationError[];
};
export type ProjectCreateRequest = {
  project_id: string;
  name: string;
  preset_id?: string | null;
};
export type ProjectImportRequest = {
  source_path: string;
};
export type Diagnostic = {
  severity: string;
  file: string;
  message: string;
};
export type AuthoringWorkspace = {
  project_id: string;
  documents?: DocumentRef[];
  validation_status: string;
  diagnostics?: Diagnostic[];
  interface_index?: InterfaceIndex | null;
};
export type DocumentFile = {
  id: string;
  name: string;
  kind: string;
  content: string;
};
export type DocumentWriteResult = {
  id: string;
  name: string;
  bytes: number;
};
export type DocumentUpdate = {
  content: string;
};
export type ValidationResult = {
  valid: boolean;
  diagnostics?: Diagnostic[];
  interface_index?: InterfaceIndex;
};
export type PipelineStage = {
  id: "validation" | "generation" | "build";
  label: string;
  status: string;
  ready: boolean;
  detail: string;
  warnings?: string[];
};
export type PipelineOverview = {
  project_id: string;
  status: ProjectStatus;
  stages?: PipelineStage[];
};
export type TaskStatus = "pending" | "running" | "completed" | "failed";
export type TaskResponse = {
  task_id: string;
  status: TaskStatus;
  message: string;
};
export type ProjectBuildRequest = {
  clean?: boolean;
  generate?: boolean;
};
export type Job = {
  task_id: string;
  type: string;
  status: string;
  project_id?: string | null;
  log?: string;
  error?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
};
export type Scenario = {
  id: string;
  name: string;
  file: string;
  steps?: {
    [key: string]: any;
  }[];
};
export type RunBlocker = {
  id: string;
  message: string;
};
export type SimulationWorkspace = {
  project_id: string;
  scenarios?: Scenario[];
  blockers?: RunBlocker[];
  nodes?: TopologyNode[];
  recent_runs?: RunSummary[];
};
export type RunEvent = {
  type: string;
  run_id?: string | null;
  status?: string | null;
  detail?: string | null;
  node_id?: string | null;
  timestamp?: string | null;
};
export type RunDetail = {
  id: string;
  project_id: string;
  scenario_id: string;
  scenario_name: string;
  status: string;
  created_at?: string | null;
  updated_at?: string | null;
  capture?: CaptureSession;
  captures?: CaptureFile[];
  containers?: {
    [key: string]: ContainerState;
  };
  events?: RunEvent[];
  scenario_capabilities?: string[];
};
export type SimulationStartRequest = {
  scenario_id: string;
};
export type ScenarioResult = {
  status: string;
  detail: string;
  limitations?: string[];
};
export type NodeLifecycle = {
  node_id: string;
  status: string;
  timestamp?: string | null;
};
export type EvidenceState = {
  capture_status: string;
  capture_count: number;
  wireshark_url?: string | null;
  packet_snapshot_saved: boolean;
  someip_observation: "captured" | "unknown" | "unavailable";
  service_discovery_observation: "captured" | "unknown" | "unavailable";
};
export type ArtifactFile = {
  name: string;
  bytes: number;
};
export type RunArtifacts = {
  run_id: string;
  files?: ArtifactFile[];
  capture?: CaptureSession;
  compose_log?: string;
  capture_log?: string;
  captures?: CaptureFile[];
};
export type RunInspection = {
  run: RunDetail;
  scenario_result: ScenarioResult;
  node_lifecycle?: NodeLifecycle[];
  evidence: EvidenceState;
  timeline?: RunEvent[];
  artifacts: RunArtifacts;
};
export type HealthResponse = {
  status: string;
  api: string;
};
export const {
  useGetWorkbenchOverviewQuery,
  useGetProjectsQuery,
  useCreateProjectMutation,
  useImportProjectMutation,
  useGetProjectOverviewQuery,
  useGetProjectAuthoringQuery,
  useGetProjectDocumentQuery,
  useSaveProjectDocumentMutation,
  useValidateProjectAuthoringMutation,
  useGetProjectPipelineQuery,
  useGenerateProjectArtifactsMutation,
  useBuildProjectNodesMutation,
  useGetJobQuery,
  useGetProjectSimulationsQuery,
  useStartProjectSimulationMutation,
  useGetProjectRunsQuery,
  useGetRunQuery,
  useStopRunMutation,
  useGetRunInspectionQuery,
  useDownloadRunCaptureQuery,
  useGetHealthQuery,
} = injectedRtkApi;
