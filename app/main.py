import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.auth_routes import auth_router
from app.routes.balance_routes import balance_router
from app.routes.bank_routes import bank_routes
from app.routes.comment_routes import comment_router
from app.routes.customer_routes import customer_router
from app.routes.invoice_routes import invoice_router
from app.routes.live_routes import live_routes
from app.routes.order_routes import order_router
from app.routes.price_routes import price_router
from app.routes.qr_routes import qr_router
from app.routes.room_routes import room_routes
from app.routes.sms_routes import sms_router
from app.routes.webhook_routes import webhook_routes
from app.routes.ws_routes import ws_router
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
app.include_router(qr_router, prefix= "/api/v1/qr", tags=["qr"])
app.include_router(webhook_routes, prefix="/api/v1/webhook", tags=["webhooks"])
app.include_router(sms_router, prefix="/api/v1/sms", tags=["admin", "sms"])
app.include_router(balance_router, prefix="/api/v1/balance-movements", tags=["admin", "balance-movements"])
app.include_router(invoice_router, prefix="/api/v1/invoices", tags=["admin", "invoices"])
app.include_router(price_router, prefix="/api/v1/pricing", tags=["admin", "pricing"])
app.include_router(ws_router, prefix="/api/v1/ws", tags=["ws"])

async def start_background_tasks():
    asyncio.create_task(process_pending_customers())
@app.on_event("startup")
async def startup_event():
    await start_background_tasks()

@app.get("/", tags=["root"])
async def root():
    return {"message": "Server is running!"}
