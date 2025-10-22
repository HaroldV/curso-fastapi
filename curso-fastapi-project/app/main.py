import zoneinfo
from datetime import datetime
from fastapi import FastAPI
from models import Transaction
from db import create_all_tables
from .routers import customers, invoices, transactions


app = FastAPI(lifespan=create_all_tables)
app.include_router(customers.router)
app.include_router(invoices.router)
app.include_router(transactions.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}


country_codes = {
    "CO": "America/Bogota",
    "VE": "America/La_Paz",
    "MX": "America/Mexico_City"
}

@app.get("/time/{iso_code}")
async def time(iso_code: str):
    iso = iso_code.upper()
    timezone_str = country_codes.get(iso)
    tz = zoneinfo.ZoneInfo(timezone_str)

    return { "time": datetime.now(tz)}



