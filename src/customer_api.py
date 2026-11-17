from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.models import Customer
from src.schemas import CustomerCreate, CustomerOut, CustomerUpdate
from src.security import verify_api_key

app = FastAPI(
    title="Customer API", description="API to manage customer records", version="1.0.0"
)


@app.get("/health")
def health_check():
    return {"status": "healthy"}


def get_database(db: Session = Depends(get_db)):
    return db


@app.post("/customers", response_model=CustomerOut, status_code=status.HTTP_201_CREATED)
def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_database),
    api_key: str = Depends(verify_api_key),
):
    existing_customer = (
        db.query(Customer).filter(Customer.email == customer.email).first()
    )

    if existing_customer:
        raise HTTPException(status_code=409, detail="Email already exists")

    new_customer = Customer(**customer.model_dump())

    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)

    return new_customer


@app.get("/customers", response_model=list[CustomerOut])
def get_customers(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_database),
    api_key: str = Depends(verify_api_key),
):
    offset = (page - 1) * per_page
    customers = db.query(Customer).offset(offset).limit(per_page).all()

    return customers


@app.get("/customers/{customer_id}", response_model=CustomerOut)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_database),
    api_key: str = Depends(verify_api_key),
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()

    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    return customer


@app.put("/customers/{customer_id}", response_model=CustomerOut)
def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    db: Session = Depends(get_database),
    api_key: str = Depends(verify_api_key),
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()

    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    update_data = customer_data.model_dump(exclude_unset=True)

    if "email" in update_data:
        existing_customer = (
            db.query(Customer)
            .filter(Customer.email == update_data["email"], Customer.id != customer_id)
            .first()
        )

        if existing_customer:
            raise HTTPException(status_code=409, detail="Email already exists")

    for key, value in update_data.items():
        setattr(customer, key, value)

    db.commit()
    db.refresh(customer)

    return customer


@app.delete("/customers/{customer_id}")
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_database),
    api_key: str = Depends(verify_api_key),
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()

    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    db.delete(customer)
    db.commit()

    return {"message": "Customer deleted successfully"}
