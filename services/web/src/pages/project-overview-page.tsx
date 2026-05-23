import { ArrowRight } from "lucide-react";
import { Link, useOutletContext } from "react-router";
import { Alert, AlertDescription, AlertTitle } from "~/components/ui/alert";
import { Button } from "~/components/ui/button";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "~/components/ui/card";
import {
  InterfaceIndexView,
  TopologyView,
} from "~/components/workbench-editor";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "~/components/ui/table";
import { Empty, Status } from "~/ui/app-frame";
import type { ProjectOutletContext } from "~/pages/project-frame";

export function ProjectOverviewPage() {
  const { project } = useOutletContext<ProjectOutletContext>();
  return (
    <div className="grid min-w-0 gap-6">
      <section
        className="grid gap-4 [grid-template-columns:repeat(auto-fit,minmax(min(14rem,100%),1fr))]"
        aria-label="Project readiness gates"
      >
        {(project.readiness_gates || []).map((gate) => (
          <article
            className="min-w-0 rounded-lg border border-border bg-card/80 p-5"
            key={gate.id}
          >
            <div className="flex items-start justify-between gap-3">
              <strong>{gate.label}</strong>
              <Status value={gate.status} />
            </div>
            <p className="mb-0 mt-3 text-sm">{gate.detail}</p>
          </article>
        ))}
      </section>
      {project.status.generation === "transport-only" && (
        <Alert className="border-amber-500/35 bg-amber-400/15">
          <AlertTitle>Generator output is transport-only</AlertTitle>
          <AlertDescription>
            The pinned CommonAPI path can build transport artifacts for this
            workbench, but missing Core proxy/stub output still limits generated
            Franca scenario assertions.
          </AlertDescription>
        </Alert>
      )}
      <div
        className="grid min-w-0 items-start gap-6 xl:grid-cols-[minmax(24rem,1fr)_minmax(24rem,1fr)]"
        data-testid="overview-lower-cards"
      >
        <div className="grid min-w-0 gap-6" data-testid="overview-left-column">
          <Card className="grid h-fit content-start gap-5 p-6">
            <CardHeader>
              <div>
                <CardTitle>Topology</CardTitle>
                <CardDescription>
                  The manifest path that a Docker simulation renders into nodes
                  and SOME/IP-SD config.
                </CardDescription>
              </div>
            </CardHeader>
            <TopologyView
              nodes={project.nodes}
              multicast={project.network.multicast}
              port={project.network.sd_port}
            />
          </Card>
          <Card
            className="grid h-fit content-start gap-4 p-6"
            data-testid="project-shape-card"
          >
            <CardHeader>
              <div>
                <CardTitle>Project shape</CardTitle>
                <CardDescription>
                  Editable inputs stay upstream from generated artifacts and
                  saved runs.
                </CardDescription>
              </div>
            </CardHeader>
            <div className="grid gap-3 sm:grid-cols-3">
              <Metric
                value={(project.documents || []).length}
                label="documents"
              />
              <Metric value={(project.nodes || []).length} label="nodes" />
              <Metric value={project.scenario_count || 0} label="scenarios" />
            </div>
            <div className="flex flex-wrap gap-2">
              {(project.documents || []).slice(0, 6).map((document) => (
                <code
                  className="inline-flex max-w-full [overflow-wrap:anywhere] rounded-md border border-border bg-muted px-3 py-2"
                  key={document.id}
                >
                  {document.name}
                </code>
              ))}
            </div>
          </Card>
        </div>
        <div className="grid min-w-0 gap-6" data-testid="overview-right-column">
          <Card className="grid h-fit content-start gap-5 p-6">
            <CardHeader>
              <div>
                <CardTitle>Interface evidence</CardTitle>
                <CardDescription>
                  Derived from validated Franca and deployment documents.
                </CardDescription>
              </div>
              <Button asChild variant="secondary">
                <Link to="author">
                  Edit
                  <ArrowRight size={16} />
                </Link>
              </Button>
            </CardHeader>
            <InterfaceIndexView index={project.interface_index} />
          </Card>
          <Card className="h-fit min-w-0 p-6" data-testid="latest-runs-card">
            <CardHeader>
              <div>
                <CardTitle>Latest runs</CardTitle>
                <CardDescription>
                  Inspection is a run debugger, not a project drawer.
                </CardDescription>
              </div>
              <Button asChild variant="secondary">
                <Link to="simulate">
                  Simulate
                  <ArrowRight size={16} />
                </Link>
              </Button>
            </CardHeader>
            <RunTable projectId={project.id} runs={project.recent_runs || []} />
          </Card>
        </div>
      </div>
    </div>
  );
}

function Metric({ value, label }: { value: number; label: string }) {
  return (
    <div className="grid min-h-24 content-center rounded-lg border border-border bg-card/80 p-5">
      <b className="font-mono text-2xl font-semibold text-foreground">{value}</b>
      <span className="mt-2 text-muted-foreground">{label}</span>
    </div>
  );
}

function RunTable({
  projectId,
  runs,
}: {
  projectId: string;
  runs: NonNullable<ProjectOutletContext["project"]["recent_runs"]>;
}) {
  if (!runs.length)
    return (
      <Empty>
        No run evidence yet. Build the project, then start a scenario.
      </Empty>
    );
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Scenario</TableHead>
          <TableHead>Status</TableHead>
          <TableHead>Capture</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {runs.map((run) => (
          <TableRow key={run.id}>
            <TableCell>
              <Link
                className="font-bold hover:text-primary"
                to={`/projects/${projectId}/runs/${run.id}`}
              >
                {run.scenario_name}
              </Link>
              <code className="block break-all text-xs text-muted-foreground">
                {run.id}
              </code>
            </TableCell>
            <TableCell>
              <Status value={run.status} />
            </TableCell>
            <TableCell className="text-muted-foreground">
              {(run.captures || []).length}
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
