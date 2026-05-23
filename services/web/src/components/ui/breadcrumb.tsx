import { ChevronRight } from "lucide-react";
import * as React from "react";
import { cn } from "~/lib/utils";

export function Breadcrumb({ ...props }: React.ComponentProps<"nav">) {
  return <nav aria-label="breadcrumb" {...props} />;
}
export function BreadcrumbList({
  className,
  ...props
}: React.ComponentProps<"ol">) {
  return (
    <ol
      className={cn(
        "flex min-w-0 flex-wrap items-center gap-2 text-sm text-muted-foreground",
        className,
      )}
      {...props}
    />
  );
}
export function BreadcrumbItem({
  className,
  ...props
}: React.ComponentProps<"li">) {
  return (
    <li
      className={cn("inline-flex min-w-0 items-center gap-2", className)}
      {...props}
    />
  );
}
export function BreadcrumbLink({
  className,
  ...props
}: React.ComponentProps<"a">) {
  return (
    <a
      className={cn("transition hover:text-foreground", className)}
      {...props}
    />
  );
}
export function BreadcrumbPage({
  className,
  ...props
}: React.ComponentProps<"span">) {
  return (
    <span
      aria-current="page"
      className={cn("truncate font-medium text-foreground", className)}
      {...props}
    />
  );
}
export function BreadcrumbSeparator() {
  return (
    <li role="presentation" aria-hidden="true" className="text-border">
      <ChevronRight size={15} />
    </li>
  );
}
