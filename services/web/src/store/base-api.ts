import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

export const baseApi = createApi({
  baseQuery: fetchBaseQuery({ baseUrl: import.meta.env.VITE_API_ORIGIN || "" }),
  endpoints: () => ({}),
  reducerPath: "workflowApi",
  tagTypes: ["Workbench", "Projects", "Authoring", "Pipeline", "Runs", "Jobs"],
});
