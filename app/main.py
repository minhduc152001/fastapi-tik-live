import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.auth_routes import auth_router
from app.routes.bank_routes import bank_routes
from app.routes.comment_routes import comment_router
from app.routes.customer_routes import customer_router
from app.routes.live_routes import live_routes
from app.routes.order_routes import order_router
from app.routes.qr_routes import qr_routes
from app.routes.room_routes import room_routes
from app.routes.webhook_routes import webhook_routes
from app.services.customer_service import process_pending_customers

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
app.include_router(comment_router, prefix="/api/v1/comments", tags=["comments"])
app.include_router(customer_router, prefix="/api/v1/customers", tags=["customers"])
app.include_router(order_router, prefix="/api/v1/orders", tags=["orders"])
app.include_router(bank_routes, prefix="/api/v1/banks", tags=["banks"])
app.include_router(qr_routes, prefix="/api/v1/qr", tags=["qr"])
app.include_router(webhook_routes, prefix="/api/v1/webhook", tags=["webhooks"])

async def start_background_tasks():
    asyncio.create_task(process_pending_customers())
@app.on_event("startup")
async def startup_event():
    await start_background_tasks()

@app.get("/", tags=["root"])
async def root():
    return {"message": "Server is running!"}
