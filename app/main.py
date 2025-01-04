from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.auth_routes import auth_router
from app.routes.live_routes import live_routes
from app.routes.room_routes import room_routes

app = FastAPI()

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gắn các router
app.include_router(auth_router, prefix="/api/v1/users", tags=["users"])
app.include_router(live_routes, prefix="/api/v1/live", tags=["live"])
app.include_router(room_routes, prefix="/api/v1/rooms", tags=["rooms"])

@app.get("/")
async def root():
    return {"message": "Server is running!"}
