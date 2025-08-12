from fastapi import FastAPI

app = FastAPI(
    title="Azure Emulator",
    description="A mock server for the Azure REST API.",
    version="0.1.0",
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Azure Emulator"}
