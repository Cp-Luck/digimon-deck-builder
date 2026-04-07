from fastapi import FastAPI

from app.api import router

app = FastAPI(title="Deck Builder App")
app.include_router(router)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Deck Builder App API is running."}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
