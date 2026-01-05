import json
import os
from datetime import datetime
from typing import Optional, List, Dict
from session_calculator import generate_payment_hash, generate_transaction_validation_hash
from storage_utils import load_data_db_table, save_payment_data,delete_data, create_data,get_item_db,change_data
from models.payment_models import PaymentBase, PaymentRefund, PaymentUpdate, PaymentOut
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

    def create_payment(payment: PaymentBase, session_user: dict) -> Dict:

        transaction_id = payment.transaction or generate_payment_hash(session_user["username"], str(datetime.now()))


        new_payment = {
            "transaction": transaction_id,
            "amount": payment.amount,
            "initiator": session_user["username"],
            "created_at": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            "completed": False,
            "date":payment.date,
            "method":payment.method,
            "issuer":payment.issuer,
            "bank":payment.bank,
            "hash": generate_transaction_validation_hash(),
            "session_id":payment.session_id,
            "parking_lot_id":payment.parking_lot_id
        }
        create_data('payments',new_payment)
        return new_payment


    def refund_payment(payment: PaymentRefund, session_user: dict) -> Dict:
        payments = load_data_db_table("refunds")
        transaction_id = payment.transaction or generate_payment_hash(session_user["username"], str(datetime.now()))

        refund_entry = {
            "transaction": transaction_id,
            "amount": -abs(payment.amount),
            "coupled_to": payment.coupled_to,
            "processed_by": session_user["username"],
            "created_at": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            "completed": False,
            "hash": generate_transaction_validation_hash(),
        }
        payments.append(refund_entry)
        save_payment_data(payments)
        return refund_entry


    def update_payment(transaction_id: str, update: PaymentUpdate) -> Dict:

        pmnt = get_item_db('transaction',transaction_id,'payments')[0]

        if not pmnt:
            raise ValueError("Payment not found")
        if pmnt["hash"] != update.validation:
            raise PermissionError("Validation failed")

        pmnt["completed"] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        pmnt["t_data"] = update.t_data
        change_data('payments',pmnt,)
        return pmnt


    def get_user_payments(username: str) -> List[Dict]:
        payments = load_data_db_table("payments")

        while True:
            for p in payments:
                print(p)
                break
            break
        return [p for p in payments if p.get("initiator") == username]


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
