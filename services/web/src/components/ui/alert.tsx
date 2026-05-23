import * as React from "react";
import { cn } from "~/lib/utils";

export function Alert({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      role="alert"
      className={cn(
        "relative grid min-w-0 gap-2 rounded-lg border border-border bg-card p-5 text-sm text-foreground",
        className,
      )}
      {...props}
    />
  );
}

export function AlertTitle({
  className,
  ...props
}: React.HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h3
      className={cn("m-0 text-base font-bold tracking-normal", className)}
      {...props}
    />
  );
}

export function AlertDescription({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("min-w-0 text-muted-foreground [&_p]:mb-0", className)}
      {...props}
    />
  );
}
