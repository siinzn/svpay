from fastapi import FastAPI
from routes.sv_pay import router as sv_pay_router

app = FastAPI(
    title="SV Pay Backend",
    description="Issuer-agnostic payment authorization simulator",
    version="0.1.0",
)

app.include_router(sv_pay_router)

@app.get("/health")
def health():
    return {"status": "ok"}
