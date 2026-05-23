import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router";
import { describe, expect, it, vi } from "vitest";
import { ProjectFrame } from "~/pages/project-frame";

vi.mock("~/generated/workflow-api", () => ({
  useGetProjectOverviewQuery: () => ({
    data: {
      id: "door-control",
      name: "Door Control",
      status: {
        validation: "valid",
        generation: "transport-only",
        build: "ready",
        last_run: "stopped",
      },
      readiness: 75,
      recommended_action: {
        kind: "simulate",
        title: "Run a scenario",
        detail: "Start a project run.",
      },
      readiness_gates: [],
      network: { service_discovery: true, sd_port: 30490 },
      nodes: [],
      documents: [],
      recent_runs: [],
    },
  }),
}));

describe("ProjectFrame", () => {
  it("keeps authoring on a nested workflow route", async () => {
    render(
      <MemoryRouter initialEntries={["/projects/door-control/author"]}>
        <Routes>
          <Route path="/projects/:projectId" element={<ProjectFrame />}>
            <Route path="author" element={<p>Author route</p>} />
          </Route>
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByTestId("project-content")).toBeInTheDocument();
    expect(screen.getByTestId("project-card")).toBeInTheDocument();
    expect(screen.getByTestId("recommended-action-card")).toBeInTheDocument();
  });
});
