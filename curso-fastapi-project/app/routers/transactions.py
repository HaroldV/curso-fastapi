
from fastapi import APIRouter, HTTPException, status

from db import SessionDep
from sqlmodel import select

from models import Customer, Transaction, TransactionCreate


router = APIRouter()

@router.post("/transactions", status_code=status.HTTP_201_CREATED, tags=['transactions'])
async def create_transaction(transaction_data: TransactionCreate, session: SessionDep):
    transaction_data_dic = transaction_data.model_dump()
    customer = session.get(Customer, transaction_data_dic.get('customer_id'))
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    transaction_db = Transaction.model_validate(transaction_data_dic)
    session.add(transaction_db)
    session.commit()
    session.refresh(transaction_db)

    return transaction_data


@router.get("/transactions", tags=['transactions'])
async def list_transactions(session: SessionDep):
    query = select(Transaction)
    transactions = session.exec(query).all()
    return transactions