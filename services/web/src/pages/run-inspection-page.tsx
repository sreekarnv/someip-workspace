import {
  CircleStop,
  Download,
  ExternalLink,
  FileText,
  TerminalSquare,
} from "lucide-react";
import { useState } from "react";
import { Link, useOutletContext, useParams } from "react-router";
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
import { ScrollArea } from "~/components/ui/scroll-area";
import { Tabs, TabsList, TabsTrigger } from "~/components/ui/tabs";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "~/components/ui/table";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "~/components/ui/tooltip";
import {
  useGetRunInspectionQuery,
  useStopRunMutation,
  type RunEvent,
} from "~/generated/workflow-api";
import { captureHref } from "~/lib/captures";
import { Notice } from "~/components/layout";
import { Empty, Loading, Status } from "~/ui/app-frame";
import type { ProjectOutletContext } from "~/pages/project-frame";

export function RunInspectionPage() {
  const { project } = useOutletContext<ProjectOutletContext>();
  const { runId = "" } = useParams();
  const {
    data: inspection,
    isLoading,
    error,
  } = useGetRunInspectionQuery(runId, { pollingInterval: 4500 });
  const [stop, stopState] = useStopRunMutation();
  const [view, setView] = useState("timeline");

  if (isLoading && !inspection)
    return <Loading label="Reading run evidence..." />;
  if (error || !inspection)
    return (
      <Notice tone="bad">Run inspection could not be loaded.</Notice>
    );

  const { run, scenario_result: scenario, evidence, artifacts } = inspection;
  return (
    <div className="grid min-w-0 gap-6">
      <Card className="min-w-0 p-6">
        <CardHeader className="flex-wrap">
          <div className="min-w-0">
            <p className="mb-2 font-mono text-sm font-medium text-accent">Run inspection</p>
            <CardTitle className="text-3xl">{run.scenario_name}</CardTitle>
            <CardDescription>
              <code className="break-all">{run.id}</code>
            </CardDescription>
          </div>
          <div className="flex flex-wrap gap-2">
            <Status value={run.status} />
            {run.status === "running" && (
              <Button
                variant="danger"
                onClick={() => stop(run.id)}
                disabled={stopState.isLoading}
              >
                <CircleStop size={17} />
                Stop
              </Button>
            )}
          </div>
        </CardHeader>
        <div className="grid gap-4 [grid-template-columns:repeat(auto-fit,minmax(min(14rem,100%),1fr))]">
          <Verdict
            label="Scenario"
            value={scenario.status}
            detail={scenario.detail}
          />
          <Verdict
            label="Capture"
            value={evidence.capture_status}
            detail={`${evidence.capture_count} packet snapshot${evidence.capture_count === 1 ? "" : "s"}`}
          />
          <Verdict
            label="SOME/IP"
            value={evidence.someip_observation}
            detail="Packet observation from saved capture evidence"
          />
          <Verdict
            label="SOME/IP-SD"
            value={evidence.service_discovery_observation}
            detail="Discovery evidence visible to Wireshark"
          />
        </div>
        {scenario.limitations?.map((limitation) => (
          <Alert
            className="mt-5 border-amber-500/35 bg-amber-400/15"
            key={limitation}
          >
            <AlertTitle>Inspection limitation</AlertTitle>
            <AlertDescription>{limitation}</AlertDescription>
          </Alert>
        ))}
      </Card>
      <div className="grid min-w-0 gap-6 xl:grid-cols-[minmax(24rem,.78fr)_minmax(34rem,1.22fr)]">
        <div className="grid content-start gap-6">
          <Card className="p-6">
            <CardHeader>
              <div>
                <CardTitle>Node lifecycle</CardTitle>
                <CardDescription>
                  Latest structured state per simulated node.
                </CardDescription>
              </div>
            </CardHeader>
            <div className="grid gap-3">
              {(inspection.node_lifecycle || []).map((node) => (
                <article
                  className="grid min-w-0 items-center gap-3 rounded-lg border border-border bg-white/70 p-4 [grid-template-columns:minmax(8rem,1fr)_auto] [&>span:last-child]:col-span-full"
                  key={node.node_id}
                >
                  <strong className="break-words">{node.node_id}</strong>
                  <Status value={node.status} />
                  <span className="break-all text-xs text-muted-foreground">
                    {node.timestamp || "timestamp pending"}
                  </span>
                </article>
              ))}
            </div>
            {!inspection.node_lifecycle?.length && (
              <Empty>No node lifecycle events have been recorded.</Empty>
            )}
          </Card>
          <Card className="p-6">
            <CardHeader>
              <div>
                <CardTitle>Packet captures</CardTitle>
                <CardDescription>
                  Open live Wireshark or download saved `.pcapng` evidence.
                </CardDescription>
              </div>
            </CardHeader>
            <div className="flex flex-wrap gap-3">
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button asChild variant="secondary">
                    <a
                      href={
                        evidence.wireshark_url ||
                        run.capture?.wireshark_url ||
                        "https://localhost:3001/"
                      }
                      target="_blank"
                      rel="noreferrer"
                    >
                      Wireshark
                      <ExternalLink size={16} />
                    </a>
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  Open the packet inspection session.
                </TooltipContent>
              </Tooltip>
              <code className="inline-flex max-w-full [overflow-wrap:anywhere] rounded-md border border-border bg-muted px-3 py-2">someip || someipsd</code>
            </div>
            <div className="mt-5 grid min-w-0 gap-3">
              {(artifacts.captures || run.captures || []).map((capture) => (
                <article
                  className="grid min-w-0 items-center gap-3 rounded-lg border border-border bg-white/70 p-4 [grid-template-columns:minmax(0,1fr)_auto] max-md:grid-cols-1"
                  key={capture.name}
                >
                  <div className="min-w-0">
                    <strong className="block break-all font-mono text-sm">
                      {capture.name}
                    </strong>
                    <span className="text-sm text-muted-foreground">
                      {capture.bytes} bytes
                    </span>
                  </div>
                  <Button asChild variant="secondary">
                    <a href={captureHref(run.id, capture.name)}>
                      <Download size={16} />
                      Download
                    </a>
                  </Button>
                </article>
              ))}
            </div>
            {!artifacts.captures?.length && !run.captures?.length && (
              <Empty>No saved capture yet.</Empty>
            )}
          </Card>
        </div>
        <Card className="min-w-0 p-6">
          <CardHeader className="flex-wrap">
            <div>
              <CardTitle>Debug record</CardTitle>
              <CardDescription>
                Events first; generated files and logs stay available when the
                verdict is not enough.
              </CardDescription>
            </div>
            <Button asChild variant="secondary">
              <Link to={`/projects/${project.id}/simulate`}>New run</Link>
            </Button>
          </CardHeader>
          <Tabs value={view} onValueChange={setView}>
            <TabsList className="mb-5">
              <TabsTrigger value="timeline">Timeline</TabsTrigger>
              <TabsTrigger value="artifacts">Artifacts</TabsTrigger>
              <TabsTrigger value="logs">Logs</TabsTrigger>
            </TabsList>
          </Tabs>
          {view === "timeline" && (
            <ScrollArea className="h-[min(68vh,56rem)] pr-3">
              <Timeline events={inspection.timeline || []} />
            </ScrollArea>
          )}
          {view === "artifacts" && <Artifacts files={artifacts.files || []} />}
          {view === "logs" && (
            <SavedLogs
              compose={artifacts.compose_log}
              capture={artifacts.capture_log}
            />
          )}
        </Card>
      </div>
    </div>
  );
}

function Verdict({
  label,
  value,
  detail,
}: {
  label: string;
  value: string;
  detail: string;
}) {
  return (
    <article className="grid min-w-0 gap-3 rounded-lg border border-border bg-white/70 p-4">
      <span className="text-sm text-muted-foreground">{label}</span>
      <Status value={value} />
      <p className="mb-0 text-sm">{detail}</p>
    </article>
  );
}

function Timeline({ events }: { events: RunEvent[] }) {
  if (!events.length)
    return <Empty>Structured run events will appear here.</Empty>;
  return (
    <div className="grid min-w-0 gap-3">
      {events
        .slice()
        .reverse()
        .map((event, index) => (
          <article
            className="grid min-w-0 items-start gap-3 rounded-lg border border-border bg-white/70 p-4 [grid-template-columns:auto_auto_minmax(0,1fr)] max-md:grid-cols-1"
            key={`${event.timestamp}-${index}`}
          >
            <code className="[overflow-wrap:anywhere]">{event.type}</code>
            <Status value={event.status || "event"} />
            <div className="min-w-0">
              <strong className="break-all">
                {event.node_id || event.run_id || ""}
              </strong>
              <p className="mb-0 break-words text-sm">
                {event.detail || event.timestamp || "Event recorded."}
              </p>
            </div>
          </article>
        ))}
    </div>
  );
}

function Artifacts({
  files,
}: {
  files: Array<{ name: string; bytes: number }>;
}) {
  if (!files.length)
    return <Empty>No rendered artifact index is saved for this run.</Empty>;
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Artifact</TableHead>
          <TableHead className="text-right">Bytes</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {files.map((file) => (
          <TableRow key={file.name}>
            <TableCell>
              <code className="break-all">{file.name}</code>
            </TableCell>
            <TableCell className="text-right text-muted-foreground">
              {file.bytes}
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

function SavedLogs({
  compose,
  capture,
}: {
  compose?: string;
  capture?: string;
}) {
  return (
    <Accordion
      type="multiple"
      defaultValue={["compose"]}
      className="rounded-lg border border-border px-5"
    >
      <AccordionItem value="compose">
        <AccordionTrigger>
          <span className="flex items-center gap-2">
            <TerminalSquare size={17} />
            Compose log
          </span>
        </AccordionTrigger>
        <AccordionContent>
          <pre>{compose || "No compose log saved."}</pre>
        </AccordionContent>
      </AccordionItem>
      <AccordionItem value="capture">
        <AccordionTrigger>
          <span className="flex items-center gap-2">
            <FileText size={17} />
            Capture log
          </span>
        </AccordionTrigger>
        <AccordionContent>
          <pre>{capture || "No capture log saved."}</pre>
        </AccordionContent>
      </AccordionItem>
    </Accordion>
  );
}
