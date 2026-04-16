from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import httpx

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ----------Helper
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "message": exc.detail}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"status": "error", "message": "Invalid or unprocessable input"}
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": "Internal server error"}
    )


# ---------Model---------
class Prediction(BaseModel):
    name: str
    gender: str | None
    probability: float | None
    sample_size: int | None
    is_confident: bool
    processed_at: str


class APIResponse(BaseModel):
    status: str
    data: Prediction


# ------------- Routes-------


@app.get("/api/classify", response_model=APIResponse)
async def predict_gender(name: str = None):
    # input validation
    if not name or name.strip() == "":
        raise HTTPException(status_code=400, detail="Missing or empty name")

    api_url = f"https://api.genderize.io?name={name}"

    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(api_url)
            response.raise_for_status()
            data = response.json()

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="External API timeout")

    except httpx.HTTPStatusError:
        raise HTTPException(status_code=502, detail="External API error")

    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Connection error")

    gender = data.get("gender")
    probability = data.get("probability")
    sample_size = data.get("count")

    # processing rules
    is_confident = False
    if probability is not None and probability >= 0.7 and sample_size >= 100:
        is_confident = True

    # Genderize edge cases
    if gender is None or sample_size == 0:
        raise HTTPException(
            status_code=404,
            detail="No prediction available for the provided name"
        )

    return {
        "status": "success",
        "data": Prediction(
            name=name,
            gender=gender,
            probability=probability,
            sample_size=sample_size,
            is_confident=is_confident,
            processed_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
    }
