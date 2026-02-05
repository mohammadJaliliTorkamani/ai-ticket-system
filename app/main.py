from fastapi import FastAPI

app = FastAPI(title="Welcome to AI Ticket Backend!")

@app.get("/health")
def health_check():
    return {"status":"ok"}