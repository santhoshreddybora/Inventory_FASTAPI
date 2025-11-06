from pydantic import BaseModel

from fastapi import APIRouter,HTTPException,Depends,status
from sqlalchemy.orm import Session
from app import models
from app.databases import engine,Base,SessionLocal
from app.schema import ProductCreate,ProductOut,ProductUpdate,ProductResponse

router=APIRouter(
    prefix='/products',
    tags=['Products']
)

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/create",response_model=ProductResponse,status_code=status.HTTP_201_CREATED)
async def create_product(product:ProductCreate,db:Session=Depends(get_db)):
    existing=db.query(models.Product).filter(models.Product.sku==product.sku).first()
    if existing:
        raise HTTPException(status_code=409,detail="Duplicate SKU can be created")
    new_product=models.Product(**product.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return {"message":"Product Added Successfully",
            "data":new_product}

@router.get("/",response_model=list[ProductOut])
async def get_products(db:Session=Depends(get_db)):
    return db.query(models.Product).all()

@router.get("/{id}",response_model=ProductOut)
async def get_product_id(id:int,db:Session=Depends(get_db)):
    product=db.query(models.Product).get(id)
    if not product:
        raise HTTPException(401,detail="id not found")
    return product

@router.put("/update/{id}",response_model=ProductOut)
async def update_product_details(id:int,update_data:ProductUpdate,db:Session=Depends(get_db)):
    product=db.query(models.Product).get(id)
    if not product:
        raise HTTPException(401,detail="product not found")
    update_dict=update_data.model_dump(exclude_unset=True)

    if "sku" in update_dict.keys():
        raise HTTPException(status_code=404, detail="SKU cannot be updated once created.")

    for key,value in update_dict.items():
        if not hasattr(product,key):
            raise HTTPException(400,detail=f"Invalid field {key}")
        setattr(product,key,value)
    db.commit()
    db.refresh(product)
    return product

@router.delete("/delete/{id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(id:int,db:Session=Depends(get_db)):
    product=db.query(models.Product).get(id)
    if not product:
        raise HTTPException(404,detail="Prodcut not found")
    db.delete(product)
    db.commit()
    return product



