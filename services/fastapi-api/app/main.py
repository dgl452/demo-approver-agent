from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api import health, items
from app.repositories.items import ItemNotFoundError

app = FastAPI(title="FastAPI Demo API", version="1.0.0")
app.include_router(health.router)
app.include_router(items.router)


@app.exception_handler(ItemNotFoundError)
async def item_not_found_handler(
    request: Request, exception: ItemNotFoundError
) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={
            "error": {
                "code": "ITEM_NOT_FOUND",
                "message": f"Item '{exception.item_id}' was not found",
                "details": None,
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    request: Request, exception: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": None,
            }
        },
    )
