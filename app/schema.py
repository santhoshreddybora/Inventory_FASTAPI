from pydantic import BaseModel,Field,ConfigDict
from typing import Optional
from datetime import datetime

class ProductBase(BaseModel):
    sku:str =Field(...,description="Unique product code")
    name:str
    price:float = Field(...,gt=0)
    stock:int =Field(...,ge=0)

class ProductCreate(ProductBase):
    pass 

class ProductUpdate(BaseModel):
    name:Optional[str]=None
    price:Optional[float]=Field(None,gt=0)
    stock:Optional[int]=Field(None,ge=0)

class ProductOut(ProductBase):
    id:int
    model_config=ConfigDict(from_attributes=True)

class ProductResponse(BaseModel):
    message: str
    data: ProductOut

    model_config=ConfigDict(from_attributes=True)



class OrderBase(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)
    status: str

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    status: Optional[str] = None
    quantity: Optional[int] = Field(None, gt=0)

class OrderOut(OrderBase):
    id: int
    created_at: datetime
    model_config=ConfigDict(from_attributes=True)


