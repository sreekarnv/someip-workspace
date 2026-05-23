import * as TabsPrimitive from "@radix-ui/react-tabs";
import { buttonVariants } from "~/components/ui/button";
import { cn } from "~/lib/utils";

export const Tabs = TabsPrimitive.Root;
export function TabsList({
  className,
  ...props
}: React.ComponentPropsWithoutRef<typeof TabsPrimitive.List>) {
  return (
    <TabsPrimitive.List
      className={cn(
        "flex gap-2 overflow-x-auto rounded-lg border border-border bg-card/80 p-2 shadow-bench",
        className,
      )}
      {...props}
    />
  );
}
export function TabsTrigger({
  className,
  ...props
}: React.ComponentPropsWithoutRef<typeof TabsPrimitive.Trigger>) {
  return (
    <TabsPrimitive.Trigger
      className={cn(
        buttonVariants({ variant: "ghost" }),
        "min-w-28 px-4 capitalize data-[state=active]:border-border data-[state=active]:bg-card data-[state=active]:text-foreground data-[state=active]:shadow-bench",
        className,
      )}
      {...props}
    />
  );
}
