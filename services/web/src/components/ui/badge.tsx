import { cva, type VariantProps } from "class-variance-authority";
import * as React from "react";
import { cn } from "~/lib/utils";

const badgeVariants = cva(
  "inline-flex max-w-full items-center rounded-full border px-2.5 py-1 text-xs capitalize",
  {
    variants: {
      variant: {
        default: "border-border bg-muted text-muted-foreground",
        good: "border-emerald-500/30 bg-emerald-500/15 text-emerald-800",
        warn: "border-amber-500/40 bg-amber-400/20 text-amber-800",
        bad: "border-destructive/30 bg-destructive/10 text-destructive",
      },
    },
    defaultVariants: { variant: "default" },
  },
);

export function Badge({
  className,
  variant,
  ...props
}: React.HTMLAttributes<HTMLSpanElement> & VariantProps<typeof badgeVariants>) {
  return (
    <span className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}
