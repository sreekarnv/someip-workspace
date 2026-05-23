import { Link, Outlet, useMatch, useResolvedPath } from "react-router";
import { Badge } from "~/components/ui/badge";
import { Button } from "~/components/ui/button";
import { TooltipProvider } from "~/components/ui/tooltip";
import { cn } from "~/lib/utils";

export function AppFrame() {
  return (
    <TooltipProvider>
      <div className="min-h-screen">
        <header className="sticky top-0 z-30 border-b border-border bg-background/88 text-foreground shadow-bench backdrop-blur">
          <div className="mx-auto flex min-h-20 max-w-[1720px] flex-wrap items-center justify-between gap-4 px-4 py-3 md:px-10">
            <div className="grid min-w-0 leading-tight">
              <strong className="font-mono text-base font-semibold">
                SOME/IP Workbench
              </strong>
              <span className="text-muted-foreground">
                Project simulation and packet inspection
              </span>
            </div>
            <nav className="flex min-w-0 gap-2" aria-label="Primary">
              <WorkbenchLink to="/dashboard">Dashboard</WorkbenchLink>
              <WorkbenchLink to="/projects">Projects</WorkbenchLink>
            </nav>
          </div>
        </header>
        <main className="mx-auto w-full max-w-[1720px] px-4 py-7 md:px-10 md:py-10">
          <Outlet />
        </main>
      </div>
    </TooltipProvider>
  );
}

function WorkbenchLink({
  to,
  children,
}: {
  to: string;
  children: React.ReactNode;
}) {
  const resolved = useResolvedPath(to);
  const active = Boolean(useMatch({ path: resolved.pathname, end: false }));

  return (
    <Button
      asChild
      variant={active ? "secondary" : "ghost"}
      className={cn("min-h-12 flex-1 px-4 md:flex-none", active && "shadow-bench")}
    >
      <Link to={to}>{children}</Link>
    </Button>
  );
}

export function Status({ value }: { value: string }) {
  const label = value || "unknown";
  return <Badge variant={tone(label)}>{label.replaceAll("_", " ")}</Badge>;
}

export function tone(value: string) {
  if (
    ["ready", "valid", "completed", "running", "active", "saved"].includes(
      value,
    )
  )
    return "good" as const;
  if (["failed", "blocked", "unavailable"].includes(value))
    return "bad" as const;
  if (
    [
      "transport-only",
      "stale",
      "starting",
      "rendered",
      "waiting_for_driver",
    ].includes(value)
  )
    return "warn" as const;
  return "default" as const;
}

export function Loading({ label = "Loading" }: { label?: string }) {
  return (
    <div className="rounded-lg border border-dashed border-border bg-card p-6 text-muted-foreground">
      {label}
    </div>
  );
}

export function Empty({ children }: { children: React.ReactNode }) {
  return (
    <div className="rounded-lg border border-dashed border-border bg-muted/60 p-5 text-muted-foreground">
      {children}
    </div>
  );
}
