from fastapi import FastAPI

app = FastAPI(title="auth-kit")


@app.get("/health")
async def health():
    return {"status": "ok"}
