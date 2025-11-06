from fastapi import APIRouter,HTTPException,Depends,status
from sqlalchemy.orm import Session
from app import models
from app.databases import engine,Base,SessionLocal

from app.schema import OrderCreate,OrderOut,OrderUpdate

router=APIRouter(
    prefix='/orders',
    tags=['Orders']
)

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post('/create',response_model=OrderOut,status_code=status.HTTP_201_CREATED)
async def create_order(order:OrderCreate,db:Session=Depends(get_db)):
    product=db.query(models.Product).get(order.product_id)
    if not product:
        raise HTTPException(status_code=404,detail="Product not found")
    if product.stock <order.quantity:
        raise HTTPException(status_code=409,detail="Insufficient stock ")
    product.stock -=order.quantity
    new_order=models.Order(**order.model_dump())
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order

    
@router.get('/orders/{id}',response_model=OrderOut)
async def get_order(id:int,db:Session=Depends(get_db)):
    order=db.query(models.Order).get(id)
    if not order:
        raise HTTPException(status_code=404,detail="Order Not found")
    return order


@router.put('/update/{id}',response_model=OrderOut)
async def update_order(id:int,order_update:OrderUpdate,db:Session=Depends(get_db)):
    order=db.query(models.Order).get(id)
    if not order:
        raise HTTPException(status_code=404,detail="Order not found")
    allowed_status=["PENDING", "PAID", "SHIPPED", "CANCELED"]
    if order_update.status not in allowed_status :
        raise HTTPException(status_code=401,detail="Status not allowed ")
    update_dict=order_update.model_dump(exclude_unset=True)
    for key,value in update_dict.items():
        setattr(order,key,value)
    db.commit()
    db.refresh(order)
    return order

@router.delete('/delete/{id}')
async def delete_order(id:int,db:Session=Depends(get_db)):
    order=db.query(models.Order).get(id)
    if not order:
        raise HTTPException(status_code=404,detail="order not found")
    if order.status != 'PENDING':
        raise HTTPException(status_code=409,detail="Order can't be deleted as it is in pending state")
    db.delete(order)
    db.commit()

