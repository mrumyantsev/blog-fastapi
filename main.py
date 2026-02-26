from fastapi import FastAPI

from config import settings
from routers import api, posts, comments, users


# HTTP server setup.
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    swagger_ui_parameters={"defaultModelsExpandDepth": -1}
)

# Routes registering.
app.include_router(api.router)
app.include_router(posts.router)
app.include_router(comments.router)
app.include_router(users.router)
