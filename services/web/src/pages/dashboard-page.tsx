import {
  Box,
  Cable,
  Camera,
  CircleStop,
  FolderKanban,
  RefreshCw,
  Timer,
} from "lucide-react";
import { Link } from "react-router";
import {
  useGetWorkbenchOverviewQuery,
  useStopRunMutation,
  type RunSummary,
} from "~/generated/workflow-api";
import { Button } from "~/components/ui/button";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "~/components/ui/card";
import { Progress } from "~/components/ui/progress";
import { Separator } from "~/components/ui/separator";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "~/components/ui/table";
import { Page, Hero, Notice } from "~/components/layout";
import { Empty, Loading, Status } from "~/ui/app-frame";

export function DashboardPage() {
  const {
    data: overview,
    error,
    isLoading,
    refetch,
  } = useGetWorkbenchOverviewQuery(undefined, { pollingInterval: 9000 });
  const [stopRun] = useStopRunMutation();
  const projects = overview?.projects || [];

  if (isLoading && !overview)
    return <Loading label="Reading Docker, generator, and run state..." />;

  return (
    <Page data-testid="dashboard-page">
      <Hero>
        <div className="grid gap-4">
          <p className="m-0 font-mono text-sm text-accent">Global workbench</p>
          <h1>Operations</h1>
          <p className="mb-0 max-w-2xl text-lg">
            Runtime health, project readiness, active simulations, and captures
            waiting for inspection.
          </p>
        </div>
        <Button variant="secondary" onClick={() => refetch()}>
          <RefreshCw size={17} />
          Refresh
        </Button>
      </Hero>
      {error && (
        <Notice tone="bad">Dashboard overview could not be loaded.</Notice>
      )}
      {overview && (
        <>
          <div
            className="grid gap-5 md:grid-cols-3"
            aria-label="Workbench summary"
          >
            <RackItem
              icon={<FolderKanban />}
              label="Projects"
              value={projects.length}
            />
            <RackItem
              icon={<Timer />}
              label="Active runs"
              value={(overview.active_runs || []).length}
            />
            <RackItem
              icon={<Camera />}
              label="Runs with captures"
              value={
                (overview.recent_runs || []).filter(
                  (run) => (run.captures || []).length,
                ).length
              }
            />
          </div>
          <div className="grid gap-6 xl:grid-cols-[minmax(25rem,.82fr)_minmax(34rem,1.18fr)]">
            <Card data-testid="runtime-readiness-card">
              <CardHeader>
                <div>
                  <CardTitle>Runtime readiness</CardTitle>
                  <CardDescription>
                    The local tools that project runs depend on.
                  </CardDescription>
                </div>
              </CardHeader>
              <div className="grid gap-2">
                <Ready
                  label="FastAPI"
                  ready={overview.runtime.api.ready}
                  detail={overview.runtime.api.detail}
                  icon={<Cable />}
                />
                <Ready
                  label="Docker daemon"
                  ready={overview.runtime.docker.ready}
                  detail={overview.runtime.docker.detail}
                  icon={<Box />}
                />
                <Ready
                  label="vsomeip runtime"
                  ready={overview.runtime.vsomeip.ready}
                  detail={overview.runtime.vsomeip.detail}
                  icon={<Cable />}
                />
                <Ready
                  label="Core generator"
                  ready={overview.runtime.generators.core.ready}
                  detail={overview.runtime.generators.core.path}
                  icon={<Cable />}
                />
                <Ready
                  label="SOME/IP generator"
                  ready={overview.runtime.generators.someip.ready}
                  detail={overview.runtime.generators.someip.path}
                  icon={<Cable />}
                />
                <Ready
                  label="Wireshark"
                  ready={overview.runtime.wireshark.status === "running"}
                  detail={overview.runtime.wireshark.status}
                  icon={<Camera />}
                />
              </div>
            </Card>
            <Card>
              <CardHeader>
                <div>
                  <CardTitle>Project health</CardTitle>
                  <CardDescription>
                    Open a project when its author, build, and run signals need
                    attention.
                  </CardDescription>
                </div>
              </CardHeader>
              <div className="grid gap-3">
                {projects.length ? (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Project</TableHead>
                        <TableHead>Shape</TableHead>
                        <TableHead>Author</TableHead>
                        <TableHead>Build</TableHead>
                        <TableHead>Run</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {projects.map((project) => (
                        <TableRow key={project.id}>
                          <TableCell>
                            <Link
                              className="font-bold hover:text-primary"
                              to={`/projects/${project.id}`}
                            >
                              {project.name}
                            </Link>
                          </TableCell>
                          <TableCell className="text-muted-foreground">
                            {project.node_count || 0} nodes,{" "}
                            {project.scenario_count || 0} scenarios
                          </TableCell>
                          <TableCell>
                            <Status value={project.latest_status.validation} />
                          </TableCell>
                          <TableCell>
                            <Status value={project.latest_status.build} />
                          </TableCell>
                          <TableCell>
                            <Status value={project.latest_status.last_run} />
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                ) : null}
                {!projects.length && (
                  <Empty>
                    No projects exist yet. Create one from the Projects page.
                  </Empty>
                )}
              </div>
            </Card>
          </div>
          <div className="grid gap-6 xl:grid-cols-2">
            <Card>
              <CardHeader>
                <div>
                  <CardTitle>Active runs</CardTitle>
                  <CardDescription>
                    Only project-scoped Docker simulations appear here.
                  </CardDescription>
                </div>
              </CardHeader>
              <RunTable
                runs={overview.active_runs || []}
                stop={(runId) => stopRun(runId)}
                empty="No active simulations."
              />
            </Card>
            <Card>
              <CardHeader>
                <div>
                  <CardTitle>Recent runs and captures</CardTitle>
                  <CardDescription>
                    Jump straight into the run inspector and packet artifacts.
                  </CardDescription>
                </div>
              </CardHeader>
              <RunTable
                runs={(overview.recent_runs || []).slice(0, 10)}
                empty="Completed run history will appear here."
              />
            </Card>
          </div>
        </>
      )}
    </Page>
  );
}

function RackItem({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: number;
}) {
  return (
    <Card className="grid min-h-32 grid-cols-[2rem_1fr] content-between gap-4 p-6 [&_svg]:text-accent">
      {icon}
      <span className="text-muted-foreground">{label}</span>
      <strong className="col-span-2 font-display text-5xl font-semibold">
        {value}
      </strong>
    </Card>
  );
}

function Ready({
  label,
  ready,
  detail,
  icon,
}: {
  label: string;
  ready: boolean;
  detail?: string | null;
  icon: React.ReactNode;
}) {
  return (
    <div className="grid gap-3 py-3 last:pb-0 sm:grid-cols-[1.5rem_minmax(9rem,.75fr)_auto_1fr] sm:items-center [&_svg]:text-accent">
      {icon}
      <strong>{label}</strong>
      <Status value={ready ? "ready" : "unavailable"} />
      <span className="break-all text-sm text-muted-foreground">
        {detail || ""}
      </span>
      <Progress className="col-span-full h-1.5" value={ready ? 100 : 24} />
      <Separator className="col-span-full last:hidden" />
    </div>
  );
}

function RunTable({
  runs,
  stop,
  empty,
}: {
  runs: RunSummary[];
  stop?: (runId: string) => void;
  empty: string;
}) {
  if (!runs.length) return <Empty>{empty}</Empty>;
  return (
    <div className="grid">
      {runs.map((run) => (
        <div
          className="grid gap-3 border-b border-border py-4 last:border-b-0 sm:grid-cols-[minmax(12rem,1fr)_auto_auto_auto] sm:items-center"
          key={run.id}
        >
          <Link
            className="grid rounded-md p-1 transition hover:bg-muted"
            to={`/projects/${run.project_id}/runs/${run.id}`}
          >
            <strong>{run.scenario_name}</strong>
            <span className="font-mono text-sm text-muted-foreground">
              {run.project_id}
            </span>
          </Link>
          <Status value={run.status} />
          <span className="text-sm text-muted-foreground">
            {(run.captures || []).length} captures
          </span>
          {stop && (
            <Button
              variant="danger"
              className="size-11 p-0"
              aria-label={`Stop ${run.scenario_name}`}
              onClick={() => stop(run.id)}
            >
              <CircleStop size={18} />
            </Button>
          )}
        </div>
      ))}
    </div>
  );
}
