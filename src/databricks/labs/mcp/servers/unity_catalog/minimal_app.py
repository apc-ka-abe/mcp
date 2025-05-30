from fastapi import FastAPI
import uvicorn
import os

app = FastAPI()

@app.get("/")
def root():
    return {"message": "App is alive"}

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    # port = int(os.getenv("DATABRICKS_APP_PORT", "5000"))
    port = 5000
    print("Running on port", port)
    uvicorn.run(app, host="0.0.0.0", port=port)