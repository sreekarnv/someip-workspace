import { CircleStop, FileCode2, Play, Radar, Save } from "lucide-react";
import { parseAsString, useQueryState } from "nuqs";
import { useState } from "react";
import { Link, useNavigate, useOutletContext } from "react-router";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "~/components/ui/accordion";
import { Alert, AlertDescription, AlertTitle } from "~/components/ui/alert";
import { Button } from "~/components/ui/button";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "~/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "~/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "~/components/ui/table";
import { WorkbenchEditor } from "~/components/workbench-editor";
import {
  useGetProjectDocumentQuery,
  useGetProjectSimulationsQuery,
  useSaveProjectDocumentMutation,
  useStartProjectSimulationMutation,
  useStopRunMutation,
  type RunSummary,
  type Scenario,
} from "~/generated/workflow-api";
import { apiMessage } from "~/lib/api-error";
import { clearDraft, draftKey, editDraft } from "~/store/workbench-slice";
import { useAppDispatch, useAppSelector } from "~/store/hooks";
import { Notice } from "~/components/layout";
import { Empty, Loading, Status } from "~/ui/app-frame";
import type { ProjectOutletContext } from "~/pages/project-frame";

export function SimulatePage() {
  const { project } = useOutletContext<ProjectOutletContext>();
  const {
    data: workspace,
    isLoading,
    error,
  } = useGetProjectSimulationsQuery(project.id, { pollingInterval: 6000 });
  const scenarios = workspace?.scenarios || [];
  const [scenarioId, setScenarioId] = useQueryState("scenario", parseAsString);
  const scenario =
    scenarios.find((item) => item.id === scenarioId) || scenarios[0];
  const [start, startState] = useStartProjectSimulationMutation();
  const navigate = useNavigate();

  async function startScenario() {
    if (!scenario) return;
    const run = await start({
      projectId: project.id,
      simulationStartRequest: { scenario_id: scenario.id },
    }).unwrap();
    navigate(`/projects/${project.id}/runs/${run.id}`);
  }

  if (isLoading && !workspace)
    return <Loading label="Reading saved simulation scenarios..." />;
  if (error || !workspace)
    return (
      <Notice tone="bad">Simulation workspace could not be loaded.</Notice>
    );

  return (
    <div className="grid min-w-0 gap-6">
      <div className="grid min-w-0 gap-6 xl:grid-cols-[minmax(25rem,.86fr)_minmax(28rem,1.14fr)]">
        <Card className="min-w-0 content-start p-6">
          <CardHeader>
            <div>
              <CardTitle>
                <Radar size={19} />
                Start simulation
              </CardTitle>
              <CardDescription>
                Choose one scenario, inspect blockers, then launch
                project-scoped Docker nodes and capture.
              </CardDescription>
            </div>
          </CardHeader>
          <label className="grid gap-2 text-sm font-bold text-muted-foreground">
            Scenario
            <Select value={scenario?.id || ""} onValueChange={setScenarioId}>
              <SelectTrigger>
                <SelectValue placeholder="Choose a scenario" />
              </SelectTrigger>
              <SelectContent>
                {scenarios.map((item) => (
                  <SelectItem value={item.id} key={item.id}>
                    {item.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </label>
          <div className="my-6 grid gap-3">
            {(workspace.blockers || []).map((blocker) => (
              <Alert
                className="border-amber-500/35 bg-amber-400/15"
                key={blocker.id}
              >
                <AlertTitle>{blocker.id}</AlertTitle>
                <AlertDescription>{blocker.message}</AlertDescription>
              </Alert>
            ))}
            {!workspace.blockers?.length && (
              <Notice tone="good">
                No run blockers. Built nodes can launch for this project.
              </Notice>
            )}
            {scenarioNeedsDriver(scenario) && (
              <Alert className="border-amber-500/35 bg-amber-400/15">
                <AlertTitle>Scenario driver boundary</AlertTitle>
                <AlertDescription>
                  Franca call/event steps still require a generated scenario
                  driver. The run can start nodes and packet capture now, and
                  inspection will keep that limitation visible.
                </AlertDescription>
              </Alert>
            )}
            {startState.error && (
              <Alert className="border-destructive/30 bg-destructive/10">
                <AlertDescription className="text-destructive">
                  {apiMessage(
                    startState.error,
                    "The scenario could not start.",
                  )}
                </AlertDescription>
              </Alert>
            )}
          </div>
          <div className="flex flex-wrap gap-3">
            <Button
              onClick={startScenario}
              disabled={
                !scenario ||
                Boolean(workspace.blockers?.length) ||
                startState.isLoading
              }
            >
              <Play size={17} />
              Run scenario
            </Button>
            <Button asChild variant="secondary">
              <Link to="../build">Open build</Link>
            </Button>
          </div>
        </Card>
        <Card className="p-6">
          <CardHeader>
            <div>
              <CardTitle>Participating nodes</CardTitle>
              <CardDescription>
                Runnable apps that the manifest sends into the run network.
              </CardDescription>
            </div>
          </CardHeader>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Node</TableHead>
                <TableHead>Role</TableHead>
                <TableHead>Interface</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {(workspace.nodes || []).map((node) => (
                <TableRow key={node.id}>
                  <TableCell>
                    <strong>{node.id}</strong>
                    <code className="block break-all text-xs text-muted-foreground">
                      {node.app_name}
                    </code>
                  </TableCell>
                  <TableCell>
                    <Status value={node.type} />
                  </TableCell>
                  <TableCell className="break-words text-muted-foreground">
                    {node.interface}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Card>
      </div>
      <div className="grid min-w-0 gap-6 xl:grid-cols-[minmax(30rem,1fr)_minmax(25rem,.8fr)]">
        <ScenarioSource projectId={project.id} scenario={scenario} />
        <RunHistory projectId={project.id} runs={workspace.recent_runs || []} />
      </div>
    </div>
  );
}

function ScenarioSource({
  projectId,
  scenario,
}: {
  projectId: string;
  scenario?: Scenario;
}) {
  const { data: document, isLoading } = useGetProjectDocumentQuery(
    { projectId, documentId: scenario?.file || "" },
    { skip: !scenario },
  );
  const dispatch = useAppDispatch();
  const draft = useAppSelector((state) =>
    document
      ? state.workbench.drafts[draftKey(projectId, document.id)]
      : undefined,
  );
  const content = draft?.content ?? document?.content ?? "";
  const [save, saveState] = useSaveProjectDocumentMutation();
  const [message, setMessage] = useState("");

  async function saveScenario() {
    if (!document) return;
    await save({
      projectId,
      documentId: document.id,
      documentUpdate: { content },
    }).unwrap();
    dispatch(clearDraft({ projectId, documentId: document.id }));
    setMessage("Scenario YAML saved.");
  }

  return (
    <Accordion
      type="single"
      collapsible
      defaultValue="scenario"
      className="min-w-0 overflow-hidden rounded-lg border border-border bg-card shadow-bench"
    >
      <AccordionItem value="scenario" className="border-b-0">
        <AccordionTrigger className="px-6">
          <span className="flex items-center gap-2">
            <FileCode2 size={18} />
            Scenario YAML
          </span>
        </AccordionTrigger>
        <AccordionContent className="grid min-w-0 gap-5 px-6 pb-6">
          <div className="flex min-w-0 flex-wrap items-center justify-between gap-3">
            <code className="break-all text-sm">
              {document?.id || scenario?.file || "No scenario selected"}
            </code>
            <Button
              variant="secondary"
              onClick={saveScenario}
              disabled={!draft?.dirty || saveState.isLoading}
            >
              <Save size={17} />
              Save
            </Button>
          </div>
          {isLoading && <Loading label="Loading scenario YAML..." />}
          {document ? (
            <div className="h-[min(62vh,38rem)] min-w-0">
              <WorkbenchEditor
                document={document}
                content={content}
                onChange={(next) =>
                  dispatch(
                    editDraft({
                      projectId,
                      documentId: document.id,
                      content: next,
                      original: document.content,
                    }),
                  )
                }
              />
            </div>
          ) : (
            !isLoading && (
              <Empty>Select a scenario with an editable YAML document.</Empty>
            )
          )}
          {message && <Notice tone="good">{message}</Notice>}
          {saveState.error && (
            <Notice tone="bad">{apiMessage(saveState.error)}</Notice>
          )}
        </AccordionContent>
      </AccordionItem>
    </Accordion>
  );
}

function RunHistory({
  projectId,
  runs,
}: {
  projectId: string;
  runs: RunSummary[];
}) {
  const [stop, stopState] = useStopRunMutation();
  return (
    <Card className="min-w-0 p-6">
      <CardHeader>
        <div>
          <CardTitle>Recent project runs</CardTitle>
          <CardDescription>
            Run inspection owns logs, captures, and event evidence.
          </CardDescription>
        </div>
      </CardHeader>
      {!runs?.length && (
        <Empty>No simulation history for this project yet.</Empty>
      )}
      <div className="grid gap-3">
        {(runs || []).map((run) => (
          <article
            className="grid min-w-0 items-center gap-3 rounded-lg border border-border bg-white/70 p-4 [grid-template-columns:minmax(0,1fr)_auto_auto]"
            key={run.id}
          >
            <Link
              className="min-w-0"
              to={`/projects/${projectId}/runs/${run.id}`}
            >
              <strong className="block truncate">{run.scenario_name}</strong>
              <code className="break-all text-xs text-muted-foreground">
                {run.id}
              </code>
            </Link>
            <Status value={run.status} />
            {run.status === "running" && (
              <Button
                variant="danger"
                className="size-11 p-0"
                aria-label={`Stop ${run.scenario_name}`}
                disabled={stopState.isLoading}
                onClick={() => stop(run.id)}
              >
                <CircleStop size={18} />
              </Button>
            )}
          </article>
        ))}
      </div>
    </Card>
  );
}

function scenarioNeedsDriver(scenario?: Scenario) {
  return Boolean(
    scenario?.steps?.some(
      (step) =>
        "call" in step || "subscribe" in step || "wait_for_event" in step,
    ),
  );
}
