import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { MemoryRouter } from "react-router";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ProjectsPage } from "~/pages/projects-page";

const createProject = vi.fn();

vi.mock("~/generated/workflow-api", () => ({
  useGetProjectsQuery: () => ({
    data: {
      projects: [],
      presets: [
        {
          id: "starter",
          name: "Starter",
          source_example: null,
          runnable: false,
          default_project_id: "sample-lab",
          default_name: "Sample Lab",
        },
        {
          id: "climate-control",
          name: "Climate Control",
          source_example: null,
          runnable: false,
          default_project_id: "climate-control",
          default_name: "Climate Control",
        },
      ],
    },
  }),
  useCreateProjectMutation: () => [createProject, {}],
  useImportProjectMutation: () => [vi.fn(), {}],
}));

describe("ProjectsPage", () => {
  beforeEach(() => {
    createProject.mockReset();
    createProject.mockReturnValue({ unwrap: () => Promise.resolve({ id: "sample-lab" }) });
  });

  it("offers creation and import surfaces", async () => {
    render(
      <MemoryRouter>
        <ProjectsPage />
      </MemoryRouter>,
    );
    expect(await screen.findByTestId("projects-page")).toBeInTheDocument();
    expect(screen.getByTestId("new-project-button")).toBeInTheDocument();
    expect(screen.getByTestId("import-project-button")).toBeInTheDocument();
  });

  it("submits typed project text fields as strings", async () => {
    render(
      <MemoryRouter>
        <ProjectsPage />
      </MemoryRouter>,
    );

    fireEvent.click(screen.getByTestId("new-project-button"));
    const dialog = await screen.findByRole("dialog");
    fireEvent.change(within(dialog).getByPlaceholderText("body-control"), {
      target: { value: "climate-control" },
    });
    fireEvent.change(within(dialog).getByPlaceholderText("Body Control"), {
      target: { value: "Climate Control" },
    });
    fireEvent.click(within(dialog).getByRole("button", { name: /create project/i }));

    await waitFor(() =>
      expect(createProject).toHaveBeenCalledWith({
        project_id: "climate-control",
        name: "Climate Control",
        preset_id: "starter",
        source_example: null,
      }),
    );
  });
});
