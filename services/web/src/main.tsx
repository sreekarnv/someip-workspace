import React, { Suspense, lazy } from "react";
import { createRoot } from "react-dom/client";
import { Provider } from "react-redux";
import { Navigate, createBrowserRouter } from "react-router";
import { RouterProvider } from "react-router/dom";
import { NuqsAdapter } from "nuqs/adapters/react-router/v7";
import { AppFrame, Loading } from "~/ui/app-frame";
import { store } from "~/store/store";
import "./styles.css";

const DashboardPage = lazy(() =>
  import("./pages/dashboard-page").then((module) => ({
    default: module.DashboardPage,
  })),
);
const ProjectsPage = lazy(() =>
  import("./pages/projects-page").then((module) => ({
    default: module.ProjectsPage,
  })),
);
const ProjectFrame = lazy(() =>
  import("./pages/project-frame").then((module) => ({
    default: module.ProjectFrame,
  })),
);
const ProjectOverviewPage = lazy(() =>
  import("./pages/project-overview-page").then((module) => ({
    default: module.ProjectOverviewPage,
  })),
);
const AuthorPage = lazy(() =>
  import("./pages/author-page").then((module) => ({
    default: module.AuthorPage,
  })),
);
const BuildPage = lazy(() =>
  import("./pages/build-page").then((module) => ({
    default: module.BuildPage,
  })),
);
const SimulatePage = lazy(() =>
  import("./pages/simulate-page").then((module) => ({
    default: module.SimulatePage,
  })),
);
const RunInspectionPage = lazy(() =>
  import("./pages/run-inspection-page").then((module) => ({
    default: module.RunInspectionPage,
  })),
);

function LazyPage({ children }: { children: React.ReactNode }) {
  return <Suspense fallback={<Loading label="Loading page..." />}>{children}</Suspense>;
}

const router = createBrowserRouter([
  {
    element: <AppFrame />,
    children: [
      { path: "/", element: <Navigate to="/dashboard" replace /> },
      { path: "/dashboard", element: <LazyPage><DashboardPage /></LazyPage> },
      { path: "/projects", element: <LazyPage><ProjectsPage /></LazyPage> },
      {
        path: "/projects/:projectId",
        element: <LazyPage><ProjectFrame /></LazyPage>,
        children: [
          { index: true, element: <LazyPage><ProjectOverviewPage /></LazyPage> },
          { path: "author", element: <LazyPage><AuthorPage /></LazyPage> },
          { path: "build", element: <LazyPage><BuildPage /></LazyPage> },
          { path: "simulate", element: <LazyPage><SimulatePage /></LazyPage> },
          { path: "runs/:runId", element: <LazyPage><RunInspectionPage /></LazyPage> },
        ],
      },
      { path: "*", element: <Navigate to="/dashboard" replace /> },
    ],
  },
]);

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <Provider store={store}>
      <NuqsAdapter>
        <RouterProvider router={router} />
      </NuqsAdapter>
    </Provider>
  </React.StrictMode>,
);
