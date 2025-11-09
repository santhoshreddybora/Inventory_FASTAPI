from fastapi import FastAPI,APIRouter,HTTPException,status,Depends,Request
from sqlalchemy.orm import Session
from app.databases import SessionLocal
from app import models
import os,hmac,hashlib,json,time
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
router=APIRouter(
    prefix='/webhook',tags=['Webhooks']
)
WEBHOOK_SECRET=os.getenv('WEBHOOK_SECRET','changeme')
print("FROM_ENV:",WEBHOOK_SECRET)
SIGNATURE_HEADER="X-Signature-SHA256"
TIMESTAMP_HEADER = "X-Timestamp"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_signature(secret:str,body:bytes,header_value:str)->bool:
    if not header_value:
        return False
    if header_value.startswith("sha256="):
        sig=header_value.split("=",1)[1]
    else:
        sig=header_value
    print("signature in verify_signature:",sig)
    computed=hmac.new(secret.encode(),body,hashlib.sha256).hexdigest()
    print("computed in verify_signature:",computed)
    return hmac.compare_digest(computed,sig)

@router.post("/payment")
async def payment_webhook(request:Request,db:Session=Depends(get_db)):
    # 1. Read raw body
    body=await request.body()
    print("Raw body received by FastAPI:", body.decode())

    #2 verify header signature
    head_sign=request.headers.get(SIGNATURE_HEADER)
    print("Received header:", head_sign)
    computed = "sha256=" + hmac.new(WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
    print("Computed signature:", computed)
    print("WEBHOOK SECRET:" ,WEBHOOK_SECRET)
    if not verify_signature(WEBHOOK_SECRET,body=body,header_value=head_sign):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invlaid signature")
    #3 Verify timestamp
    ts_header = request.headers.get(TIMESTAMP_HEADER)
    if ts_header:
        try:
            ts = int(ts_header)
            now = int(time.time())
            if abs(now - ts) > 300:  # 5 minutes tolerance
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Stale timestamp")
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid timestamp header")

    payload = json.loads(body.decode())

    #excepting payload contains event_type and event_id and order_id
    event_id=payload.get("event_id")
    event_type=payload.get("event_type")
    order_id=payload.get("order_id")

    if not event_id or not event_type or not order_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Missing event_id,event_type,order_id")
    
    try:
        existing=db.query(models.WebhookEvent).filter(models.WebhookEvent.event_id==event_id).first()

        if existing:
            return {"detail":"Event id already processed"}
        
        web_event=models.WebhookEvent(event_id=event_id,event_type=event_type,raw_payload=body.decode(),
                                      received_at=datetime.now())
        db.add(web_event)
        db.flush()

        if event_type=="payment.succeeded":
            order=db.query(models.Order).get(order_id)
            if not order_id:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Order not found")
            order.status='PAID'
            order.paid_at=datetime.now()

            db.add(order)
        
        db.commit()
        
    except Exception as e:
        db.rollback()
        print("❌ Webhook error:", str(e))

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Webhook processing failed")

    return {"detail": "Webhook processed"}

