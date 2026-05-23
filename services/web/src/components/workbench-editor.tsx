import { yaml } from "@codemirror/lang-yaml";
import { EditorView } from "@codemirror/view";
import CodeMirror from "@uiw/react-codemirror";
import { useMemo } from "react";
import type {
  Diagnostic,
  DocumentFile,
  InterfaceIndex,
  TopologyNode,
} from "~/generated/workflow-api";
import { Notice } from "~/components/layout";
import { Empty, Status } from "~/ui/app-frame";
import { cn } from "~/lib/utils";

export function WorkbenchEditor({
  document,
  content,
  onChange,
}: {
  document: DocumentFile;
  content: string;
  onChange: (next: string) => void;
}) {
  const extensions = useMemo(
    () => [
      EditorView.lineWrapping,
      ...(document.kind === "yaml" || document.kind === "yml" ? [yaml()] : []),
    ],
    [document.kind],
  );
  return (
    <CodeMirror
      className="h-full min-h-88 min-w-0 overflow-hidden rounded-lg border border-[#375b5e] [&_.cm-editor]:h-full [&_.cm-scroller]:h-full"
      value={content}
      height="100%"
      theme="dark"
      extensions={extensions}
      onChange={onChange}
      basicSetup={{ foldGutter: false }}
    />
  );
}

export function Diagnostics({
  diagnostics,
  dirty,
  valid,
}: {
  diagnostics?: Diagnostic[];
  dirty?: boolean;
  valid?: boolean;
}) {
  if (dirty)
    return (
      <Notice tone="warn">
        Unsaved source changes. Save and validate before generation.
      </Notice>
    );
  if (!diagnostics?.length)
    return (
      <Notice tone={valid ? "good" : "default"}>
        {valid ? "Validation passed." : "No diagnostics recorded yet."}
      </Notice>
    );
  return (
    <div className="grid min-w-0 gap-2">
      {diagnostics.map((item) => (
        <div
          className={
            item.severity === "error"
              ? "min-w-0 rounded-lg border border-[#e3b2af] bg-[#fae1df] p-4 text-destructive [overflow-wrap:anywhere]"
              : "min-w-0 rounded-lg border border-[#e5cb7c] bg-[#fff1cc] p-4 text-[#875b05] [overflow-wrap:anywhere]"
          }
          key={`${item.file}-${item.message}`}
        >
          <strong className="break-all">{item.file}</strong>
          <span className="break-words">{item.message}</span>
        </div>
      ))}
    </div>
  );
}

export function InterfaceIndexView({
  index,
  compact = false,
}: {
  index?: InterfaceIndex | null;
  compact?: boolean;
}) {
  if (!index)
    return (
      <Empty>
        Validate the editable contract to derive interfaces and deployment IDs.
      </Empty>
    );
  return (
    <div className={cn("grid min-w-0", compact ? "gap-2" : "gap-3")}>
      {(index.interfaces || []).map((item) => (
        <article
          className={cn(
            "grid min-w-0 rounded-lg border border-border bg-white/70",
            compact
              ? "gap-3 p-3"
              : "items-center gap-4 p-4 max-md:grid-cols-1 md:grid-cols-[minmax(0,1fr)_auto_auto]",
          )}
          key={item.document}
        >
          <div className="min-w-0">
            <strong className="block [overflow-wrap:anywhere]">
              {[item.package, item.name].filter(Boolean).join(".") ||
                item.document}
            </strong>
            <span className="block truncate text-sm text-muted-foreground">
              {item.document}
            </span>
          </div>
          {compact ? (
            <div className="flex flex-wrap gap-x-4 gap-y-1 text-sm text-muted-foreground">
              <span>{(item.methods || []).length} methods</span>
              <span>{(item.events || []).length} events</span>
            </div>
          ) : (
            <>
              <span className="text-sm text-muted-foreground">
                {(item.methods || []).length} methods
              </span>
              <span className="text-sm text-muted-foreground">
                {(item.events || []).length} events
              </span>
            </>
          )}
        </article>
      ))}
      {(index.deployments || []).map((item) => (
        <article
          className={cn(
            "rounded-md border border-border bg-muted/55",
            compact ? "p-3" : "p-4",
          )}
          key={item.document}
        >
          <strong
            className={cn(
              "block break-all font-mono",
              compact ? "text-xs" : "text-sm",
            )}
          >
            {item.document}
          </strong>
          <span
            className={cn(
              "mt-2 block break-words text-muted-foreground",
              compact ? "text-xs leading-5" : "text-sm",
            )}
          >
            {Object.entries(item.ids || {})
              .map(([key, values]) => `${key}: ${values.join(", ")}`)
              .join(" | ") || "No deployment IDs indexed."}
          </span>
        </article>
      ))}
    </div>
  );
}

export function TopologyView({
  nodes,
  multicast,
  port,
  compact = false,
}: {
  nodes?: TopologyNode[];
  multicast?: string;
  port?: number;
  compact?: boolean;
}) {
  return (
    <div
      className={cn("grid min-w-0", compact ? "gap-2" : "gap-3")}
      data-testid="topology-preview"
    >
      <div
        className={cn(
          "grid min-w-0 gap-1 rounded-lg border border-accent/20 bg-accent/10",
          compact ? "p-3" : "p-4",
        )}
      >
        <span className="font-bold text-foreground">SOME/IP-SD network</span>
        <code className="max-w-full [overflow-wrap:anywhere] text-sm text-muted-foreground">
          {multicast || "multicast unset"}:{port ?? "port unset"}
        </code>
      </div>
      {(nodes || []).map((node) => (
        <article
          className={cn(
            "grid min-w-0 rounded-lg border border-border bg-white/70",
            compact ? "gap-3 p-3" : "gap-4 p-4",
          )}
          key={node.id}
        >
          <div className="flex min-w-0 flex-wrap items-start justify-between gap-3">
            <strong className="min-w-0 [overflow-wrap:anywhere]">
              {node.id}
            </strong>
            <Status value={node.type} />
          </div>
          <dl className={cn("m-0 grid min-w-0", compact ? "gap-2" : "gap-3")}>
            <div className="grid min-w-0 gap-1">
              <dt className="text-sm text-muted-foreground">Application</dt>
              <dd className="m-0 min-w-0 [overflow-wrap:anywhere] text-sm text-foreground">
                <code>{node.app_name || "app name unset"}</code>
              </dd>
            </div>
            <div className="grid min-w-0 gap-1">
              <dt className="text-sm text-muted-foreground">Interface</dt>
              <dd className="m-0 min-w-0 [overflow-wrap:anywhere] text-sm text-foreground">
                {node.interface || "interface unset"}
              </dd>
            </div>
          </dl>
        </article>
      ))}
      {!nodes?.length && (
        <Empty>No nodes are declared in the project manifest.</Empty>
      )}
    </div>
  );
}
