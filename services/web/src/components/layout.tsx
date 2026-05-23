import * as React from "react";
import { cn } from "~/lib/utils";

export function Page({
  className,
  ...props
}: React.HTMLAttributes<HTMLElement>) {
  return (
    <section
      className={cn(
        "grid min-w-0 gap-8 animate-in fade-in slide-in-from-bottom-1 duration-200",
        className,
      )}
      {...props}
    />
  );
}

export function Hero({
  className,
  ...props
}: React.HTMLAttributes<HTMLElement>) {
  return (
    <header
      className={cn(
        "grid gap-6 rounded-lg border border-border bg-card px-6 py-7 shadow-bench lg:grid-cols-[minmax(0,1fr)_auto] lg:items-end lg:px-8",
        className,
      )}
      {...props}
    />
  );
}

export function SplitGrid({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("grid min-w-0 items-start gap-6 xl:grid-cols-2", className)}
      {...props}
    />
  );
}

export function Notice({
  tone = "default",
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement> & {
  tone?: "default" | "good" | "warn" | "bad";
}) {
  const tones = {
    default: "border-border bg-muted/80 text-muted-foreground",
    good: "border-[#94d5c1] bg-[#d9f2e7] text-primary",
    warn: "border-[#e5cb7c] bg-[#fff1cc] text-[#875b05]",
    bad: "border-[#e3b2af] bg-[#fae1df] text-destructive",
  };
  return (
    <div
      className={cn(
        "min-w-0 rounded-lg border p-4 [overflow-wrap:anywhere]",
        tones[tone],
        className,
      )}
      {...props}
    />
  );
}
