from schemas.workflow import ApiError

ERROR_RESPONSES = {
    400: {"model": ApiError, "description": "Invalid project or workflow state."},
    404: {
        "model": ApiError,
        "description": "Project, document, run, or job was not found.",
    },
    409: {
        "model": ApiError,
        "description": "The requested project resource already exists.",
    },
}
