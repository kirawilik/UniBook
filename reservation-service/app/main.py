from fastapi import FastAPI

app = FastAPI(title="Reservation Service")


@app.get("/health")
def health():
    return {"status": "ok"}