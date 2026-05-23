import { ArrowRight } from "lucide-react";
import { Link, Outlet, useMatch, useParams, useResolvedPath } from "react-router";
import {
  useGetProjectOverviewQuery,
  type ProjectOverview,
} from "~/generated/workflow-api";
import { Button } from "~/components/ui/button";
import { Progress } from "~/components/ui/progress";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "~/components/ui/breadcrumb";
import { Notice } from "~/components/layout";
import { Loading, Status } from "~/ui/app-frame";
import { cn } from "~/lib/utils";

export type ProjectOutletContext = { project: ProjectOverview };

const destinations = [
  {
    to: "",
    end: true,
    label: "Overview",
    detail: "Readiness",
  },
  {
    to: "author",
    label: "Author",
    detail: "Contracts",
  },
  {
    to: "build",
    label: "Build",
    detail: "Pipeline",
  },
  {
    to: "simulate",
    label: "Simulate",
    detail: "Scenarios",
  },
];

export function ProjectFrame() {
  const { projectId = "" } = useParams();
  const {
    data: project,
    isLoading,
    error,
  } = useGetProjectOverviewQuery(projectId, { pollingInterval: 7000 });

  if (isLoading && !project)
    return <Loading label="Opening project workflow..." />;
  if (error || !project)
    return (
      <section className="min-w-0 animate-in fade-in slide-in-from-bottom-1 duration-200">
        <Notice tone="bad">Project overview could not be loaded.</Notice>
      </section>
    );

  return (
    <section
      className="grid min-w-0 gap-6 animate-in fade-in slide-in-from-bottom-1 duration-200"
      data-testid="project-shell"
    >
      <header
        className="grid min-w-0 gap-6 rounded-lg border border-border bg-card p-6 shadow-bench xl:grid-cols-[minmax(17rem,.72fr)_minmax(0,1fr)_auto] xl:items-end xl:p-8"
        data-testid="project-card"
      >
        <div className="grid min-w-0 gap-4">
          <Breadcrumb>
            <BreadcrumbList>
              <BreadcrumbItem>
                <BreadcrumbLink href="/projects">Projects</BreadcrumbLink>
              </BreadcrumbItem>
              <BreadcrumbSeparator />
              <BreadcrumbItem>
                <BreadcrumbPage>{project.name}</BreadcrumbPage>
              </BreadcrumbItem>
            </BreadcrumbList>
          </Breadcrumb>
          <div className="grid min-w-0 gap-2">
            <code className="break-all text-sm text-accent">{project.id}</code>
            <h1 className="[overflow-wrap:anywhere] text-[2.75rem]">
              {project.name}
            </h1>
          </div>
          <div className="grid gap-2">
            <div className="flex items-center justify-between gap-3 text-sm text-muted-foreground">
              <span>Readiness</span>
              <b className="font-mono text-foreground">{project.readiness}%</b>
            </div>
            <Progress value={project.readiness} />
          </div>
        </div>

        <div className="grid min-w-0 gap-4" data-testid="recommended-action-card">
          <div className="grid gap-2">
            <p className="mb-1 font-mono text-sm font-medium text-accent">
              Recommended next action
            </p>
            <h2>{project.recommended_action.title}</h2>
            <p className="mb-0 max-w-3xl">
              {project.recommended_action.detail}
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Status value={project.status.validation} />
            <Status value={project.status.generation} />
            <Status value={project.status.build} />
            <span className="text-sm text-muted-foreground">
              SD <code>{project.network.sd_port}</code>
            </span>
          </div>
        </div>

        <Button asChild className="xl:justify-self-end">
          <Link
            to={actionPath(
              project.recommended_action.kind,
              project.recent_runs?.[0]?.id,
            )}
          >
            Open {project.recommended_action.kind}
            <ArrowRight size={18} />
          </Link>
        </Button>
      </header>

      <nav
        className="grid min-w-0 gap-2 rounded-lg border border-border bg-card/80 p-2 shadow-bench sm:grid-cols-4"
        aria-label="Project workflow"
        data-testid="project-tabs"
      >
        {destinations.map((item) => (
          <ProjectNav key={item.label} {...item} />
        ))}
      </nav>

      <div className="grid min-w-0 gap-6" data-testid="project-content">
        <Outlet context={{ project } satisfies ProjectOutletContext} />
      </div>
    </section>
  );
}

function ProjectNav({
  to,
  end,
  label,
  detail,
}: {
  to: string;
  end?: boolean;
  label: string;
  detail: string;
}) {
  const resolved = useResolvedPath(to || ".");
  const match = useMatch({ path: resolved.pathname, end: Boolean(end) });
  const active = Boolean(match);

  return (
    <Button
      asChild
      variant={active ? "secondary" : "ghost"}
      className={cn(
        "h-auto min-h-14 w-full justify-start px-4 py-3 text-left sm:justify-center sm:text-center",
        active && "border-[#9db5b3] bg-white/90 shadow-bench",
      )}
      data-testid={`project-tab-${label.toLowerCase()}`}
    >
      <Link to={to || "."}>
        <span className="grid gap-0.5">
          <strong className="block text-foreground">{label}</strong>
          <small className="block font-normal text-muted-foreground">
            {detail}
          </small>
        </span>
      </Link>
    </Button>
  );
}

function actionPath(
  kind: ProjectOverview["recommended_action"]["kind"],
  latestRunId?: string,
) {
  if (kind === "author") return "author";
  if (kind === "build") return "build";
  if (kind === "simulate") return "simulate";
  return latestRunId ? `runs/${latestRunId}` : "simulate";
}
