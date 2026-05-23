import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "~/lib/utils";

export const buttonVariants = cva(
  "inline-flex min-h-11 items-center justify-center gap-2 rounded-md border text-sm font-bold transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-45 [&_*]:text-current [&_svg]:shrink-0",
  {
    variants: {
      variant: {
        default:
          "border-primary bg-primary px-4 !text-primary-foreground shadow-bench visited:!text-primary-foreground hover:bg-primary/90 [&_*]:!text-primary-foreground",
        secondary:
          "border-border bg-card px-4 !text-foreground visited:!text-foreground hover:border-accent hover:bg-muted [&_*]:!text-foreground",
        outline:
          "border-border bg-transparent px-4 !text-foreground visited:!text-foreground hover:bg-muted [&_*]:!text-foreground",
        danger:
          "border-destructive/35 bg-destructive/10 px-4 !text-destructive visited:!text-destructive hover:bg-destructive/15 [&_*]:!text-destructive",
        ghost:
          "border-transparent px-3 !text-muted-foreground visited:!text-muted-foreground hover:bg-muted hover:!text-foreground [&_*]:!text-current",
        icon:
          "size-11 border-border bg-card p-0 !text-foreground visited:!text-foreground hover:bg-muted [&_*]:!text-current",
      },
    },
    defaultVariants: { variant: "default" },
  },
);

export interface ButtonProps
  extends
    React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ asChild, className, variant, ...props }, ref) => {
    const Component = asChild ? Slot : "button";
    return (
      <Component
        className={cn(buttonVariants({ variant }), className)}
        ref={ref}
        {...props}
      />
    );
  },
);
Button.displayName = "Button";
