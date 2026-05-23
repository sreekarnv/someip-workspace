import { Save, ScanSearch, Waypoints } from "lucide-react";
import { parseAsString, useQueryState } from "nuqs";
import { useState } from "react";
import { Link, useNavigate, useOutletContext } from "react-router";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "~/components/ui/accordion";
import { Alert, AlertDescription } from "~/components/ui/alert";
import { Button } from "~/components/ui/button";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "~/components/ui/card";
import { ScrollArea } from "~/components/ui/scroll-area";
import {
  Diagnostics,
  InterfaceIndexView,
  TopologyView,
  WorkbenchEditor,
} from "~/components/workbench-editor";
import {
  useGenerateProjectArtifactsMutation,
  useGetProjectAuthoringQuery,
  useGetProjectDocumentQuery,
  useSaveProjectDocumentMutation,
  useValidateProjectAuthoringMutation,
  type AuthoringWorkspace,
  type DocumentRef,
  type ValidationResult,
} from "~/generated/workflow-api";
import { apiMessage } from "~/lib/api-error";
import { cn } from "~/lib/utils";
import { clearDraft, draftKey, editDraft } from "~/store/workbench-slice";
import { useAppDispatch, useAppSelector } from "~/store/hooks";
import { Notice } from "~/components/layout";
import { Empty, Loading, Status } from "~/ui/app-frame";
import type { ProjectOutletContext } from "~/pages/project-frame";

export function AuthorPage() {
  const { project } = useOutletContext<ProjectOutletContext>();
  const {
    data: workspace,
    refetch,
    isLoading,
  } = useGetProjectAuthoringQuery(project.id);
  const sourceDocuments = (workspace?.documents || []).filter(
    (item) => item.kind === "fidl" || item.kind === "fdepl",
  );
  const [documentId, setDocumentId] = useQueryState("document", parseAsString);
  const documentRef =
    sourceDocuments.find((item) => item.id === documentId) ||
    sourceDocuments[0];
  const { data: document, isLoading: documentLoading } =
    useGetProjectDocumentQuery(
      { projectId: project.id, documentId: documentRef?.id || "" },
      { skip: !documentRef },
    );
  const dispatch = useAppDispatch();
  const draft = useAppSelector((state) =>
    document
      ? state.workbench.drafts[draftKey(project.id, document.id)]
      : undefined,
  );
  const content = draft?.content ?? document?.content ?? "";
  const [validation, setValidation] = useState<ValidationResult>();
  const [save, saveState] = useSaveProjectDocumentMutation();
  const [validate, validateState] = useValidateProjectAuthoringMutation();
  const [generate, generateState] = useGenerateProjectArtifactsMutation();
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  async function saveSource() {
    if (!document) return;
    await save({
      projectId: project.id,
      documentId: document.id,
      documentUpdate: { content },
    }).unwrap();
    dispatch(clearDraft({ projectId: project.id, documentId: document.id }));
    setMessage(`${document.name} saved.`);
  }

  async function validateSource() {
    const result = await validate(project.id).unwrap();
    setValidation(result);
    refetch();
  }

  async function generateFromAuthor() {
    if (draft?.dirty) await saveSource();
    const task = await generate(project.id).unwrap();
    navigate(`/projects/${project.id}/build?job=${task.task_id}`);
  }

  if (isLoading && !workspace)
    return <Loading label="Reading authoring documents..." />;

  return (
    <div className="grid min-w-0 items-start gap-6 xl:grid-cols-[18rem_minmax(0,1fr)] 2xl:grid-cols-[18rem_minmax(0,1fr)_24rem]">
      <ContractFilesCard
        documents={sourceDocuments}
        selectedId={documentRef?.id}
        onSelect={setDocumentId}
        onValidate={validateSource}
        onGenerate={generateFromAuthor}
        validateBusy={validateState.isLoading}
        generateBusy={generateState.isLoading}
      />

      <Card className="grid min-w-0 gap-4 p-[clamp(1.2rem,2vw,1.75rem)] [grid-template-rows:auto_minmax(36rem,70vh)_auto_auto] max-md:[grid-template-rows:auto_minmax(30rem,64vh)_auto_auto]">
        <CardHeader className="mb-0 flex-wrap">
          <div className="min-w-0">
            <CardTitle className="break-all font-mono text-base">
              {document?.id || "No file selected"}
            </CardTitle>
            <CardDescription>
              Save the contract before validation, generation, or simulation.
            </CardDescription>
          </div>
          <Button
            variant="secondary"
            onClick={saveSource}
            disabled={!draft?.dirty || saveState.isLoading}
          >
            <Save size={17} />
            Save
          </Button>
        </CardHeader>
        {documentLoading && <Loading label="Loading contract source..." />}
        {document ? (
          <WorkbenchEditor
            document={document}
            content={content}
            onChange={(next) =>
              dispatch(
                editDraft({
                  projectId: project.id,
                  documentId: document.id,
                  content: next,
                  original: document.content,
                }),
              )
            }
          />
        ) : (
          !documentLoading && (
            <Empty>Select a Franca or deployment document.</Empty>
          )
        )}
        {message && <Notice tone="good">{message}</Notice>}
        {(saveState.error || validateState.error || generateState.error) && (
          <Alert className="border-destructive/30 bg-destructive/10">
            <AlertDescription className="text-destructive">
              {apiMessage(
                saveState.error || validateState.error || generateState.error,
              )}
            </AlertDescription>
          </Alert>
        )}
      </Card>

      <InspectorCard
        workspace={workspace}
        project={project}
        validation={validation}
        dirty={Boolean(draft?.dirty)}
      />
    </div>
  );
}

function ContractFilesCard({
  documents,
  selectedId,
  onSelect,
  onValidate,
  onGenerate,
  validateBusy,
  generateBusy,
}: {
  documents: DocumentRef[];
  selectedId?: string;
  onSelect: (documentId: string) => void;
  onValidate: () => void;
  onGenerate: () => void;
  validateBusy?: boolean;
  generateBusy?: boolean;
}) {
  return (
    <Card
      className="grid h-fit min-w-0 content-start gap-5 p-5 xl:sticky xl:top-28"
      data-testid="contract-files-card"
    >
      <CardHeader className="mb-0 grid gap-1">
        <CardTitle>Contract files</CardTitle>
        <CardDescription>
          Franca interfaces and SOME/IP deployment source.
        </CardDescription>
      </CardHeader>

      <ScrollArea className="-mx-1 max-h-[24rem] px-1">
        <div className="grid gap-2 pr-2">
          {documents.map((item) => {
            const active = item.id === selectedId;
            return (
              <button
                className={cn(
                  "grid w-full min-w-0 grid-cols-[auto_minmax(0,1fr)] items-center gap-3 rounded-md border p-3 text-left transition hover:border-accent hover:bg-muted/80",
                  active
                    ? "border-primary/35 bg-primary/10 shadow-bench"
                    : "border-border bg-white/65",
                )}
                key={item.id}
                onClick={() => onSelect(item.id)}
                type="button"
              >
                <Status value={item.kind} />
                <span className="grid min-w-0 gap-0.5">
                  <strong className="truncate text-sm text-foreground">
                    {item.name}
                  </strong>
                  <code className="truncate text-xs text-muted-foreground">
                    {item.id}
                  </code>
                </span>
              </button>
            );
          })}
        </div>
      </ScrollArea>

      <div className="grid gap-2 border-t border-border pt-5">
        <Button
          className="w-full justify-start"
          variant="secondary"
          onClick={onValidate}
          disabled={validateBusy}
        >
          <ScanSearch size={17} />
          Validate contracts
        </Button>
        <Button
          className="w-full justify-start"
          onClick={onGenerate}
          disabled={generateBusy}
        >
          <Waypoints size={17} />
          Generate artifacts
        </Button>
      </div>

      {!documents.length && (
        <Empty>No authoring files are listed by the manifest.</Empty>
      )}
    </Card>
  );
}

function InspectorCard({
  workspace,
  project,
  validation,
  dirty,
}: {
  workspace?: AuthoringWorkspace;
  project: ProjectOutletContext["project"];
  validation?: ValidationResult;
  dirty: boolean;
}) {
  return (
    <Card
      className="grid h-fit min-w-0 content-start gap-5 p-5 xl:col-span-2 2xl:sticky 2xl:top-28 2xl:col-span-1"
      data-testid="author-inspector-card"
    >
      <CardHeader className="mb-0 flex-wrap">
        <div className="min-w-0">
          <CardTitle>Inspector</CardTitle>
          <CardDescription>
            Validation, interface IDs, and topology preview.
          </CardDescription>
        </div>
        <Status value={workspace?.validation_status || project.status.validation} />
      </CardHeader>

      <Diagnostics
        diagnostics={validation?.diagnostics || workspace?.diagnostics}
        dirty={dirty}
        valid={validation?.valid}
      />

      <Accordion
        type="multiple"
        defaultValue={["interfaces"]}
        className="grid min-w-0 gap-2"
      >
        <AccordionItem
          value="interfaces"
          className="rounded-lg border border-border bg-white/55 px-4 last:border-b"
        >
          <AccordionTrigger>Interfaces and IDs</AccordionTrigger>
          <AccordionContent>
            <InterfaceIndexView
              compact
              index={validation?.interface_index || workspace?.interface_index}
            />
          </AccordionContent>
        </AccordionItem>
        <AccordionItem
          value="topology"
          className="rounded-lg border border-border bg-white/55 px-4 last:border-b"
        >
          <AccordionTrigger>Topology preview</AccordionTrigger>
          <AccordionContent>
            <TopologyView
              compact
              nodes={project.nodes}
              multicast={project.network.multicast}
              port={project.network.sd_port}
            />
          </AccordionContent>
        </AccordionItem>
      </Accordion>

      <Button asChild variant="secondary" className="w-full justify-start">
        <Link to="../build">Open build pipeline</Link>
      </Button>
    </Card>
  );
}
