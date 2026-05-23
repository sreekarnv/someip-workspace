import { zodResolver } from "@hookform/resolvers/zod";
import { FolderInput, FolderPlus, Network, Plus } from "lucide-react";
import { useEffect } from "react";
import { Controller, useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router";
import { z } from "zod";
import {
  useCreateProjectMutation,
  useGetProjectsQuery,
  useImportProjectMutation,
} from "~/generated/workflow-api";
import { Alert, AlertDescription } from "~/components/ui/alert";
import { Button } from "~/components/ui/button";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "~/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogTitle,
  DialogTrigger,
} from "~/components/ui/dialog";
import { Field, Input } from "~/components/ui/field";
import { Separator } from "~/components/ui/separator";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "~/components/ui/select";
import { Page, Hero, Notice } from "~/components/layout";
import { Empty, Loading, Status } from "~/ui/app-frame";

const newProjectSchema = z.object({
  project_id: z
    .string()
    .regex(/^[a-z][a-z0-9-]+$/, "Use lowercase letters, digits, and hyphens."),
  name: z.string().trim().min(2, "Give the workspace a display name."),
  seed: z.string().min(1, "Choose starter content."),
});
const importSchema = z.object({
  source_path: z.string().trim().min(1, "Choose a project directory path."),
});
type NewProjectValues = z.infer<typeof newProjectSchema>;
type ImportValues = z.infer<typeof importSchema>;

export function ProjectsPage() {
  const { data: library, isLoading, error } = useGetProjectsQuery();
  const projects = library?.projects || [];
  const presets = library?.presets || [];
  const [createProject, createState] = useCreateProjectMutation();
  const [importProject, importState] = useImportProjectMutation();
  const navigate = useNavigate();

  const createForm = useForm<NewProjectValues>({
    resolver: zodResolver(newProjectSchema),
    defaultValues: { project_id: "", name: "", seed: "starter" },
  });
  const projectImport = useForm<ImportValues>({
    resolver: zodResolver(importSchema),
    defaultValues: { source_path: "" },
  });

  function applyPresetDefaults(presetId: string, overwrite = false) {
    const preset = presets.find((item) => item.id === presetId);
    if (!preset) return;
    const current = createForm.getValues();
    if (preset.default_project_id && (overwrite || !current.project_id)) {
      createForm.setValue("project_id", preset.default_project_id, {
        shouldDirty: true,
        shouldValidate: true,
      });
    }
    if (preset.default_name && (overwrite || !current.name)) {
      createForm.setValue("name", preset.default_name, {
        shouldDirty: true,
        shouldValidate: true,
      });
    }
  }

  useEffect(() => {
    if (!presets.length) return;
    const currentSeed = createForm.getValues("seed");
    const nextSeed = presets.some((preset) => preset.id === currentSeed)
      ? currentSeed
      : presets[0].id;
    if (nextSeed !== currentSeed) {
      createForm.setValue("seed", nextSeed, { shouldValidate: true });
    }
    applyPresetDefaults(nextSeed);
  }, [presets]);

  async function create(values: NewProjectValues) {
    try {
      const detail = await createProject({
        project_id: values.project_id,
        name: values.name,
        preset_id: values.seed,
      }).unwrap();
      navigate(`/projects/${detail.id}`);
    } catch (reason) {
      createForm.setError("root", { message: apiMessage(reason) });
    }
  }

  async function importManifest(values: ImportValues) {
    try {
      const detail = await importProject({
        source_path: values.source_path,
      }).unwrap();
      navigate(`/projects/${detail.id}`);
    } catch (reason) {
      projectImport.setError("root", { message: apiMessage(reason) });
    }
  }

  return (
    <Page data-testid="projects-page">
      <Hero className="lg:items-center">
        <div className="grid gap-4">
          <p className="m-0 font-mono text-sm text-accent">Project library</p>
          <h1>Projects</h1>
          <p className="mb-0 max-w-2xl text-lg">
            A project owns the Franca contract, build outputs, scenario runs,
            and the evidence you debug later.
          </p>
        </div>
        <div className="flex flex-wrap gap-3 lg:justify-end">
          <Dialog>
            <DialogTrigger asChild>
              <Button data-testid="new-project-button">
                <Plus size={17} />
                New project
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogTitle>New project</DialogTitle>
              <DialogDescription>
                Start from generic Franca files or a vehicle contract that
                generates runnable SOME/IP transport nodes.
              </DialogDescription>
              <form
                className="grid gap-4"
                onSubmit={createForm.handleSubmit(create)}
              >
                <Field
                  label="Project ID"
                  hint="Used in URLs and project folder names."
                  error={createForm.formState.errors.project_id?.message}
                >
                  <Input
                    placeholder="body-control"
                    {...createForm.register("project_id")}
                  />
                </Field>
                <Field
                  label="Display name"
                  error={createForm.formState.errors.name?.message}
                >
                  <Input
                    placeholder="Body Control"
                    {...createForm.register("name")}
                  />
                </Field>
                <Field
                  label="Starter content"
                  error={createForm.formState.errors.seed?.message}
                >
                  <Controller
                    control={createForm.control}
                    name="seed"
                    render={({ field }) => (
                      <Select
                        value={field.value}
                        onValueChange={(next) => {
                          field.onChange(next);
                          applyPresetDefaults(next, true);
                        }}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {presets.map((preset) => (
                            <SelectItem value={preset.id} key={preset.id}>
                              {preset.name}
                              {preset.runtime_kind ? " generated" : " files"}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    )}
                  />
                </Field>
                {createForm.formState.errors.root?.message && (
                  <Alert className="border-destructive/30 bg-destructive/10">
                    <AlertDescription className="text-destructive">
                      {createForm.formState.errors.root.message}
                    </AlertDescription>
                  </Alert>
                )}
                <Button disabled={createState.isLoading}>
                  <FolderPlus size={17} />
                  Create project
                </Button>
              </form>
            </DialogContent>
          </Dialog>
          <Dialog>
            <DialogTrigger asChild>
              <Button variant="secondary" data-testid="import-project-button">
                <FolderInput size={17} />
                Import
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogTitle>Import project</DialogTitle>
              <DialogDescription>
                Point at a local directory containing `project.yaml`.
              </DialogDescription>
              <form
                className="grid gap-4"
                onSubmit={projectImport.handleSubmit(importManifest)}
              >
                <Field
                  label="Local project directory"
                  error={projectImport.formState.errors.source_path?.message}
                >
                  <Input
                    placeholder="/work/someip-project"
                    {...projectImport.register("source_path")}
                  />
                </Field>
                {projectImport.formState.errors.root?.message && (
                  <Alert className="border-destructive/30 bg-destructive/10">
                    <AlertDescription className="text-destructive">
                      {projectImport.formState.errors.root.message}
                    </AlertDescription>
                  </Alert>
                )}
                <Button disabled={importState.isLoading}>
                  Import manifest
                </Button>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </Hero>
      {error && <Notice tone="bad">Project list could not be loaded.</Notice>}
      {isLoading ? (
        <Loading label="Scanning manifest-backed projects..." />
      ) : (
        <div className="grid content-start gap-6 xl:grid-cols-[minmax(0,1fr)_22rem]">
          <div className="grid content-start gap-5 lg:grid-cols-2">
            {projects.map((project) => (
              <Link
                className="group grid min-h-80 gap-6 rounded-lg border border-border bg-card p-6 shadow-bench transition hover:-translate-y-0.5 hover:border-accent"
                to={`/projects/${project.id}`}
                key={project.id}
              >
                <header className="flex items-center justify-between gap-3 font-mono text-sm text-accent">
                  <Network size={23} />
                  <code>{project.id}</code>
                </header>
                <strong className="font-display text-4xl font-semibold leading-tight">
                  {project.name}
                </strong>
                <Separator />
                <div className="grid gap-3 sm:grid-cols-3">
                  <Metric
                    value={project.document_count || 0}
                    label="editable files"
                  />
                  <Metric value={project.node_count || 0} label="nodes" />
                  <Metric
                    value={project.scenario_count || 0}
                    label="scenarios"
                  />
                </div>
                <footer className="mt-auto flex flex-wrap gap-2">
                  <Status value={project.latest_status.validation} />
                  <Status value={project.latest_status.generation} />
                  <Status value={project.latest_status.build} />
                </footer>
              </Link>
            ))}
            {!projects.length && (
              <Card>
                <CardHeader>
                  <div>
                    <CardTitle>No projects yet</CardTitle>
                    <CardDescription>
                      Create a starter project to write Franca, generate code,
                      build containers, and run scenarios from one workspace.
                    </CardDescription>
                  </div>
                </CardHeader>
              </Card>
            )}
          </div>
          <Card className="grid content-start gap-5">
            <CardHeader>
              <div>
                <CardTitle>Workbench rhythm</CardTitle>
                <CardDescription>
                  Each project advances through the same traceable loop.
                </CardDescription>
              </div>
            </CardHeader>
            <ol className="grid gap-4 text-sm text-muted-foreground">
              <FlowStep
                index="01"
                title="Author"
                detail="Shape Franca and deployment IDs."
              />
              <FlowStep
                index="02"
                title="Build"
                detail="Generate code and runnable nodes."
              />
              <FlowStep
                index="03"
                title="Simulate"
                detail="Start a project scenario in Docker."
              />
              <FlowStep
                index="04"
                title="Inspect"
                detail="Keep logs, pcapng, and run history."
              />
            </ol>
          </Card>
        </div>
      )}
    </Page>
  );
}

function Metric({ value, label }: { value: number; label: string }) {
  return (
    <span className="grid min-h-20 content-center rounded-md border border-border bg-muted/70 p-3 text-sm text-muted-foreground">
      <b className="font-mono text-lg text-foreground">{value}</b>
      {label}
    </span>
  );
}

function FlowStep({
  index,
  title,
  detail,
}: {
  index: string;
  title: string;
  detail: string;
}) {
  return (
    <li className="grid grid-cols-[2.2rem_1fr] gap-3">
      <span className="font-mono text-accent">{index}</span>
      <span>
        <b className="block text-foreground">{title}</b>
        {detail}
      </span>
    </li>
  );
}

function apiMessage(reason: unknown) {
  if (typeof reason === "object" && reason && "data" in reason) {
    const data = (reason as { data?: { detail?: string } }).data;
    if (data?.detail) return data.detail;
  }
  return "The project operation failed.";
}
