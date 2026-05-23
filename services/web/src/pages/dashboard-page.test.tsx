import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router";
import { describe, expect, it, vi } from "vitest";
import { DashboardPage } from "~/pages/dashboard-page";

vi.mock("~/generated/workflow-api", () => ({
  useGetWorkbenchOverviewQuery: () => ({
    data: {
      projects: [
        {
          id: "door-control",
          name: "Door Control",
          document_count: 2,
          node_count: 2,
          scenario_count: 1,
          latest_status: {
            validation: "valid",
            generation: "transport-only",
            build: "ready",
            last_run: "stopped",
          },
        },
      ],
      active_runs: [],
      recent_runs: [],
      runtime: {
        api: { ready: true },
        docker: { ready: true, detail: "26" },
        vsomeip: { ready: true, detail: "ready" },
        wireshark: { status: "stopped" },
        generators: {
          core: { ready: true, path: "core" },
          someip: { ready: true, path: "someip" },
        },
      },
    },
    refetch: vi.fn(),
  }),
  useStopRunMutation: () => [vi.fn()],
}));

describe("DashboardPage", () => {
  it("shows project health and runtime state", async () => {
    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>,
    );
    expect(await screen.findByTestId("dashboard-page")).toBeInTheDocument();
    expect(screen.getByTestId("runtime-readiness-card")).toBeInTheDocument();
  });
});
