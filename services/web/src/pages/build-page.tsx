import { Hammer, ScanSearch, Terminal, Waypoints } from "lucide-react";
import { parseAsString, useQueryState } from "nuqs";
import { Link, useOutletContext } from "react-router";
import { Alert, AlertDescription, AlertTitle } from "~/components/ui/alert";
import { Button } from "~/components/ui/button";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "~/components/ui/card";
import { Progress } from "~/components/ui/progress";
import {
  useBuildProjectNodesMutation,
  useGenerateProjectArtifactsMutation,
  useGetJobQuery,
  useGetProjectPipelineQuery,
  type PipelineStage,
} from "~/generated/workflow-api";
import { apiMessage } from "~/lib/api-error";
import { Notice } from "~/components/layout";
import { Empty, Loading, Status } from "~/ui/app-frame";
import type { ProjectOutletContext } from "~/pages/project-frame";

export function BuildPage() {
  const { project } = useOutletContext<ProjectOutletContext>();
  const {
    data: pipeline,
    isLoading,
    error,
    refetch,
  } = useGetProjectPipelineQuery(project.id, { pollingInterval: 6000 });
  const [jobId, setJobId] = useQueryState("job", parseAsString);
  const [generate, generateState] = useGenerateProjectArtifactsMutation();
  const [build, buildState] = useBuildProjectNodesMutation();
  const operationError = generateState.error || buildState.error;

  async function startGenerate() {
    const task = await generate(project.id).unwrap();
    setJobId(task.task_id);
    refetch();
  }

  async function startBuild() {
    const task = await build({
      projectId: project.id,
      projectBuildRequest: { clean: false, generate: true },
    }).unwrap();
    setJobId(task.task_id);
    refetch();
  }

  if (isLoading && !pipeline)
    return <Loading label="Reading build pipeline..." />;
  if (error || !pipeline)
    return (
      <Notice tone="bad">Build pipeline could not be loaded.</Notice>
    );

  return (
    <div className="grid min-w-0 gap-6 xl:grid-cols-[minmax(27rem,.92fr)_minmax(31rem,1.08fr)]">
      <div className="grid content-start gap-6">
        <Card className="p-6">
          <CardHeader>
            <div>
              <CardTitle>Build path</CardTitle>
              <CardDescription>
                Validation, code generation, and runnable node artifacts are
                separate gates.
              </CardDescription>
            </div>
          </CardHeader>
          <div className="grid gap-4">
            {(pipeline.stages || []).map((stage, index) => (
              <Stage key={stage.id} stage={stage} index={index + 1} />
            ))}
          </div>
          <div className="mt-6 flex flex-wrap gap-3">
            <Button asChild variant="secondary">
              <Link to="../author">
                <ScanSearch size={17} />
                Author and validate
              </Link>
            </Button>
            <Button
              variant="secondary"
              onClick={startGenerate}
              disabled={generateState.isLoading}
            >
              <Waypoints size={17} />
              Generate
            </Button>
            <Button onClick={startBuild} disabled={buildState.isLoading}>
              <Hammer size={17} />
              Build nodes
            </Button>
          </div>
          {operationError && (
            <Alert className="mt-5 border-destructive/30 bg-destructive/10">
              <AlertDescription className="text-destructive">
                {apiMessage(operationError)}
              </AlertDescription>
            </Alert>
          )}
        </Card>
        <GeneratorWarnings stages={pipeline.stages || []} />
      </div>
      <JobPanel jobId={jobId || ""} />
    </div>
  );
}

function Stage({ stage, index }: { stage: PipelineStage; index: number }) {
  return (
    <article className="grid min-w-0 items-start gap-x-4 gap-y-3 rounded-lg border border-border bg-white/70 p-4 [grid-template-columns:auto_minmax(0,1fr)]">
      <span className="font-mono font-semibold text-accent">{String(index).padStart(2, "0")}</span>
      <div className="min-w-0">
        <div className="flex min-w-0 flex-wrap items-center gap-3">
          <strong>{stage.label}</strong>
          <Status value={stage.status} />
        </div>
        <p className="mb-0 mt-2">{stage.detail}</p>
      </div>
      <Progress className="col-start-2" value={stage.ready ? 100 : 18} />
    </article>
  );
}

function GeneratorWarnings({ stages }: { stages: PipelineStage[] }) {
  const warnings = stages.flatMap((stage) => stage.warnings || []);
  if (!warnings.length)
    return (
      <Empty>
        Pipeline warnings will appear here when a generator or artifact stage is
        limited.
      </Empty>
    );
  return (
    <Alert className="border-amber-500/35 bg-amber-400/15">
      <AlertTitle>Generator boundary</AlertTitle>
      <AlertDescription className="grid gap-2">
        {warnings.map((warning) => (
          <span className="break-words" key={warning}>
            {warning}
          </span>
        ))}
      </AlertDescription>
    </Alert>
  );
}

function JobPanel({ jobId }: { jobId: string }) {
  const { data: job } = useGetJobQuery(jobId, {
    skip: !jobId,
    pollingInterval: jobId ? 1200 : 0,
  });
  return (
    <Card className="grid min-w-0 gap-4 p-6 [grid-template-rows:auto_minmax(28rem,72vh)_auto]">
      <CardHeader className="flex-wrap">
        <div>
          <CardTitle>
            <Terminal size={19} />
            Project job log
          </CardTitle>
          <CardDescription>
            {job
              ? `${job.type} is ${job.status}.`
              : "Generate or build to attach a persisted job to this view."}
          </CardDescription>
        </div>
        {job && <Status value={job.status} />}
      </CardHeader>
      <pre className="h-full whitespace-pre-wrap">{job?.log || "No build job selected."}</pre>
      {job?.error && <Notice tone="bad">{job.error}</Notice>}
    </Card>
  );
}
