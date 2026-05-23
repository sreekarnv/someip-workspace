from fastapi import HTTPException


def project_error(exc: Exception) -> HTTPException:
    if isinstance(exc, FileNotFoundError):
        return HTTPException(status_code=404, detail=str(exc))

    if isinstance(exc, FileExistsError):
        return HTTPException(status_code=409, detail=str(exc))

    return HTTPException(status_code=400, detail=str(exc))
