from sqlalchemy import Column,Integer,String,Float,Index,ForeignKey,DateTime,CheckConstraint,Text
from app.databases import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sku = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)
    __table_args__ = (
        Index('idx_sku', 'sku'),
        CheckConstraint('price>0',name='check_quantity_positive'),
        CheckConstraint('stock>=0',name='stock_price_checking')
    )


class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product")
    __table_args__=(
        CheckConstraint('quantity>0',name='check_quantity_positive'),
    )

    # Constraint Check for statuses
    @staticmethod
    def validate_status(status):
        allowed_statuses = ["PENDING", "PAID", "SHIPPED", "CANCELED"]
        if status not in allowed_statuses:
            raise ValueError(f"Status must be one of the following: {allowed_statuses}")

class WebhookEvent(Base):
    __tablename__="Webhook_events"

    id=Column(Integer,primary_key=True)
    event_id=Column(String,nullable=False,unique=True)
    event_type=Column(String,nullable=False)
    raw_payload=Column(Text)
    received_at=Column(DateTime(timezone=True),server_default=func.now())

