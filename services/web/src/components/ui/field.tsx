import * as React from "react";
import { cn } from "~/lib/utils";

export const Input = React.forwardRef<
  HTMLInputElement,
  React.InputHTMLAttributes<HTMLInputElement>
>(({ className, ...props }, ref) => (
  <input
    ref={ref}
    className={cn(
      "min-h-12 w-full rounded-md border border-border bg-background px-3 text-foreground outline-none focus:ring-2 focus:ring-ring",
      className,
    )}
    {...props}
  />
));
Input.displayName = "Input";
export function Field({
  label,
  hint,
  error,
  className,
  children,
}: {
  label: string;
  hint?: string;
  error?: string;
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <label
      className={cn(
        "grid gap-2 text-sm font-bold text-muted-foreground",
        className,
      )}
    >
      <span>{label}</span>
      {children}
      {error ? (
        <span className="font-medium text-destructive">{error}</span>
      ) : hint ? (
        <span className="font-normal text-muted-foreground">{hint}</span>
      ) : null}
    </label>
  );
}
