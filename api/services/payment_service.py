import json
import os
import secrets
import string
from fastapi import HTTPException, status
from datetime import datetime
from typing import Optional, List, Dict
from session_calculator import generate_payment_hash, generate_transaction_validation_hash
from storage_utils import load_data_db_table,delete_data, create_data,get_item_db,change_data
from models.payment_models import PaymentBase, PaymentRefund, PaymentUpdate, PaymentOut, PaymentCreate
from services.validation_service import ValidationService
class PaymentService:

    def get_session(token: str) -> Optional[dict]:
        return ValidationService.validate_session_token(token)


    # --------------------------
    # Data storage
    # --------------------------


    def save_payment_data(data: List[Dict]):
        with open("payments.json", "w") as f:
            json.dump(data, f, indent=2)


    # --------------------------
    # Helper utilities
    # --------------------------
    def generate_payment_hash(username: str, timestamp: str):
        return f"PAY-{hash(username + timestamp)}"


    def generate_transaction_validation_hash():
        return f"HASH-{datetime.now().timestamp()}"


    # --------------------------
    # Core business operations
    # --------------------------


    def create_payment(payment: PaymentCreate, session_user: dict) -> Dict:
        transaction_id = generate_payment_hash(session_user['id'], {'licenseplate': payment.license_plate})

        chars = string.ascii_uppercase + string.digits
        issuer_string = ''

        for i in range(0,10):
            issuer_result = ''.join(secrets.choice(chars) for _ in range(8))
            return_value = get_item_db('issuer',issuer_result,'payments')
            if not return_value:
                issuer_string = issuer_result
                break
            if i == 9 and len(issuer_string) < 1:
                raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many attempts. Please try again later."
            )
        find_session_to_pay =  get_item_db('id', payment.session_id, 'payments')[0]
        if find_session_to_pay['stopped'] == None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot create a payment for a stil active session, please cancel it first"
            )
        
        new_payment = {
            "transaction": transaction_id,
            "amount": find_session_to_pay['cost'],
            "initiator": session_user["username"],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "completed": None,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "method":None,
            "issuer":None,
            "bank":None,
            "hash": generate_transaction_validation_hash(),
            "session_id":session_user['id'],
            "parking_lot_id":find_session_to_pay['parking_lot_id']
        }
        create_data('payments',new_payment)
        return new_payment


    def refund_payment(payment: PaymentOut, session_user: dict) -> Dict:

        transaction_id = generate_payment_hash(session_user['id'], {'licenseplate': payment.license_plate})

        refund_entry = {
            "transaction": transaction_id,
            "amount": -abs(payment.amount),
            "coupled_to": payment.coupled_to,
            "processed_by": session_user["username"],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "completed": False,
            "hash": generate_transaction_validation_hash(),
        }
        
        create_data('refunds',refund_entry)
        return refund_entry


    def update_payment(transaction_id: str, update: PaymentUpdate, session) -> Dict:

        pmnt = get_item_db('id', transaction_id, 'payments')
        user = get_item_db('username', session["username"], 'users')
        parking_session = get_item_db('id', pmnt["session_id"], 'parking_sessions')

        pmnt = pmnt [0]

        if not pmnt:
            raise ValueError("Payment not found")
        # if pmnt["hash"] != update.validation:
        #     raise PermissionError("Validation failed")


        pmnt["completed"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pmnt["method"] = update.method
        pmnt["bank"] = update.bank
        pmnt["issuer"] = update.issuer

        if update.disc_code != None :
            disc_code = get_item_db('code', update.disc_code, 'discounts')[0]
            if(disc_code and disc_code["expiration_date"]):

                # If the discount code has a user_id or a lot_id, ensure the current payment is correct for either 
                if disc_code["user_id"] != None :
                    if disc_code["user_id"] != user['id'] : 
                        raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="The discount codes alloted user id is not compatible with the current users id."
                    )
                if disc_code["lot_id"] != None :
                    if disc_code["lot_id"] != pmnt["parking_lot_id"] : 
                        raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="The discount codes alloted parking lot id is not compatible with the payment's parking lot id."
                    )

                # Remove the discounted value from the current to be payed amount 
                if disc_code["amount"] != None :
                    pmnt["amount"] -= disc_code["amount"]

                elif disc_code["percentage"] != None:
                    perc = (100 - disc_code["percentage"]) / 100
                    x = pmnt["amount"]
                    pmnt["amount"] = x * perc
                
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Discount code not found."
                )
            
        # Apply the changes to payments and parking_sessions 
        change_data('payments',pmnt,'transaction')
        
        parking_session['status'] = 'paid'
        
        change_data('parking_sessions', parking_session, 'id')
        return pmnt


    def get_user_payments(username: str) -> List[Dict]:
        user_pmnts = get_item_db("initiator",username,"payments")
        return user_pmnts


    def get_all_user_payments(admin_session: dict, username: str) -> List[Dict]:
        if admin_session.get("role") != "ADMIN":
            raise PermissionError("Access denied")
        payments = load_data_db_table("payments")
        return [p for p in payments if p.get("initiator") == username]

    def delete_payment(admin_session: dict, transaction_id: str) -> List[Dict]:
      
        payments = load_data_db_table("payments")
        if admin_session.get("role") != "ADMIN":
            raise PermissionError("Access denied")
        delete_data(transaction_id, "transaction_id", "payments")
        return any(x["transaction_id"] == transaction_id for x in payments)
