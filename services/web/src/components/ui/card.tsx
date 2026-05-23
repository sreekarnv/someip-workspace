import * as React from "react";
import { cn } from "~/lib/utils";

export function Card({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <section
      className={cn(
        "relative min-w-0 overflow-hidden rounded-lg border border-border bg-card p-6 shadow-bench",
        className,
      )}
      {...props}
    />
  );
}
export function CardHeader({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <header
      className={cn(
        "mb-5 flex min-w-0 items-start justify-between gap-4",
        className,
      )}
      {...props}
    />
  );
}
export function CardTitle({
  className,
  ...props
}: React.HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h2
      className={cn("m-0 text-lg font-bold text-foreground", className)}
      {...props}
    />
  );
}
export function CardDescription({
  className,
  ...props
}: React.HTMLAttributes<HTMLParagraphElement>) {
  return (
    <p
      className={cn(
        "mb-0 mt-1 max-w-prose text-sm text-muted-foreground",
        className,
      )}
      {...props}
    />
  );
}
