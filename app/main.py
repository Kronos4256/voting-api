from fastapi import FastAPI

from app.api import auth, candidates, voters, votes
from app.core.errors import register_exception_handlers

app = FastAPI(
    title="Voting API",
    version="1.0.0",
    description="REST API to manage voters, candidates and votes.",
)
register_exception_handlers(app)

app.include_router(auth.router)
app.include_router(voters.router)
app.include_router(candidates.router)
app.include_router(votes.router)


@app.get("/health", tags=["Health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
