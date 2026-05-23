import { createSlice, PayloadAction } from "@reduxjs/toolkit";

type Draft = { content: string; dirty: boolean };
type WorkbenchState = {
  drafts: Record<string, Draft>;
};

const initialState: WorkbenchState = {
  drafts: {},
};

function draftKey(projectId: string, documentId: string) {
  return `${projectId}:${documentId}`;
}

const workbenchSlice = createSlice({
  name: "workbench",
  initialState,
  reducers: {
    editDraft(
      state,
      action: PayloadAction<{
        projectId: string;
        documentId: string;
        content: string;
        original: string;
      }>,
    ) {
      const { projectId, documentId, content, original } = action.payload;
      state.drafts[draftKey(projectId, documentId)] = {
        content,
        dirty: content !== original,
      };
    },
    clearDraft(
      state,
      action: PayloadAction<{ projectId: string; documentId: string }>,
    ) {
      delete state.drafts[
        draftKey(action.payload.projectId, action.payload.documentId)
      ];
    },
  },
});

export const { editDraft, clearDraft } = workbenchSlice.actions;
export const workbenchReducer = workbenchSlice.reducer;
export { draftKey };
