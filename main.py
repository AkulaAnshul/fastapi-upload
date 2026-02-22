from fastapi import FastAPI, File, UploadFile, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware
import pandas as pd
import uvicorn
import io

app = FastAPI()

class NgrokSkipMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS":
            response = Response()
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "*"
            response.headers["ngrok-skip-browser-warning"] = "true"
            return response
        response = await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["ngrok-skip-browser-warning"] = "true"
        return response

app.add_middleware(NgrokSkipMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

SECRET_TOKEN   = "qa58blms081kh6me"
MAX_SIZE_BYTES = 81 * 1024
ALLOWED_EXTS   = {".csv", ".json", ".txt"}

@app.options("/upload")
async def options_upload():
    return Response(
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    x_upload_token_3709: str = Header(default=None)
):
    if x_upload_token_3709 != SECRET_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

    filename = file.filename or ""
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTS:
        raise HTTPException(status_code=400, detail="Bad Request: invalid file type")

    content = await file.read()

    if len(content) > MAX_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="Payload Too Large")

    df = pd.read_csv(io.BytesIO(content))
    total_value     = round(float(df["value"].sum()), 2)
    category_counts = df["category"].value_counts().to_dict()

    return JSONResponse(
        content={
            "email":          "24f2004163@ds.study.iitm.ac.in",
            "filename":       filename,
            "rows":           len(df),
            "columns":        list(df.columns),
            "totalValue":     total_value,
            "categoryCounts": category_counts
        },
        headers={"Access-Control-Allow-Origin": "*"}
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
