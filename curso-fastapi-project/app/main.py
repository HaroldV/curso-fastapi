import zoneinfo
from datetime import datetime
from typing import Annotated

from fastapi import FastAPI, status, HTTPException
from fastapi.params import Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from db import create_all_tables
from .routers import plans, customers, invoices, transactions


app = FastAPI(lifespan=create_all_tables)
app.include_router(customers.router)
app.include_router(invoices.router)
app.include_router(transactions.router)
app.include_router(plans.router)

security = HTTPBasic()

@app.get("/")
async def root(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    print(credentials)
    if credentials.username == "haroldcv2" and credentials.password == "supersecret":
        return {"message": f"Hello, {credentials.username}!"}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


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



