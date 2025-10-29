from dns.e164 import query
from fastapi import APIRouter, status, HTTPException, Query

from models import Customer, CustomerCreate, CustomerUpdate, Plan, CustomerPlan, StatusEnum
from db import SessionDep

from sqlmodel import select

router = APIRouter()

db_customers: list[Customer] = []

@router.post(
    "/customers",
        response_model=Customer,
        status_code=status.HTTP_201_CREATED,
        tags=['customers'])
async def create_customer(customer_data: CustomerCreate, session: SessionDep):
    customer = Customer.model_validate(customer_data.model_dump())
    session.add(customer) # lo agregamos a la base de datos
    session.commit() # ejecutamos la sentencia sql
    session.refresh(customer) # refrescamos esta variable en memoria
    
    # customer.id = len(db_customers)
    # db_customers.append(customer)
    return customer

@router.get("/customers/{customer_id}", response_model=Customer, tags=['customers'])
async def read_customer(customer_id: int, session: SessionDep):
    customer_db = session.get(Customer, customer_id) 
    if not customer_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Customer don't exist")

@router.get("/customers", response_model=list[Customer], tags=['customers'])
async def list_customers(session: SessionDep):
    return session.exec(select(Customer)).all()
    # return db_customers


@router.delete("/customers/{customer_id}", tags=['customers'])
async def delete_customer(customer_id: int, session: SessionDep):
    customer_db = session.get(Customer, customer_id) 
    if not customer_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Customer don't exist")
    session.delete(customer_db)
    session.commit()
    return {"detail": "Customer Deleted"}

@router.patch("/customers/{customer_id}", response_model=Customer, status_code=status.HTTP_201_CREATED, tags=['customers'])
async def update_customer(customer_id: int,customer_data: CustomerUpdate, session: SessionDep):
    customer_db = session.get(Customer, customer_id) 
    if not customer_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Customer don't exist")
    
    customer_data_dic = customer_data.model_dump(exclude_unset=True)
    customer_db.sqlmodel_update(customer_data_dic)
    session.add(customer_db)
    session.commit()
    session.refresh(customer_db)
    return customer_db


@router.post("/customers/{customer_id}/plans/{plan_id}")
async def subscribe_customer_to_plan(customer_id: int,
                                     plan_id: int,
                                     session: SessionDep,
                                     plan_status: StatusEnum = Query()
                                     ):
    customer_db = session.get(Customer, customer_id)
    plan_db = session.get(Plan, plan_id)

    if not customer_db or not plan_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The customer or plan doesn't exist"
        )

    customer_plan_db = CustomerPlan(plan_id=plan_db.id, customer_id=customer_db.id, status=plan_status)

    session.add(customer_plan_db)
    session.commit()
    session.refresh(customer_plan_db)

    return customer_plan_db


@router.post("/customers/{customer_id}/plans/")
async def get_customer_to_plan(customer_id: int,
                               session: SessionDep,
                               plan_status: StatusEnum = Query()):
    customer_db = session.get(Customer, customer_id)

    if not customer_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    query_str = (
        select(CustomerPlan)
         .where(CustomerPlan.customer_id == customer_id)
         .where(CustomerPlan.status == plan_status)
    )

    plans = session.exec(query_str).all()

    return plans