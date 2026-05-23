/** @type {import("@rtk-query/codegen-openapi").ConfigFile} */
const config = {
  schemaFile: "../api/openapi/v1.json",
  apiFile: "./src/store/base-api.ts",
  apiImport: "baseApi",
  outputFile: "./src/generated/workflow-api.ts",
  exportName: "workflowApi",
  hooks: true,
  flattenArg: true,
};

export default config;
