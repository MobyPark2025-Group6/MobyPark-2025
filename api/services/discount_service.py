import datetime
from fastapi import HTTPException, status
from typing import Optional
from datetime import datetime
from storage_utils import create_data,load_data_db_table,delete_data,get_item_db,change_data
from services.validation_service import ValidationService
import secrets
import string

class DiscountService:
    #Will return a string of 10 random letters of various capitalisations 
    @staticmethod
    def generate_discount_automatic(token, discount):
        #10 tries before relaying an error to the user, to decrease the chance of duplicates causing a rejection of an auto generated discount code 
        amount = discount.amount 
        loid = discount.lot_id
        perc = discount.percentage
        exp_date = discount.expiration_date
        uid = discount.user_id

        session_user = ValidationService.validate_session_token(token)
        if ValidationService.check_valid_admin(session_user):
            for i in range(0,10) :
                alphabet = string.ascii_letters  # a–z + A–Z
                code = ''.join(secrets.choice(alphabet) for _ in range(10))
                c = get_item_db('code',code,'discounts')
                if not c :
                    discount = {
                        "amount" : None if amount == 0 else amount,
                        "created_at" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "lot_id" : None if loid == 0 else loid,
                        "code" : code,
                        "percentage" : None if perc == 0 else perc,
                        "expiration_date" :None if exp_date == None else exp_date,
                        "user_id" : None if uid == 0 else uid
                    }
                    print(discount)
                    return create_data('discounts',discount)
                 
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many attempts. Please try again later."
            )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user is not an admin.",
        )
          

    #Admin chosen discount string 
    @staticmethod
    def generate_discount_manual(token, discount):
        
        
        amount = discount.amount 
       
        loid = discount.lot_id
        disc_str = discount.code
        perc = discount.percentage
        exp_date = discount.expiration_date
        uid = discount.user_id
  
        session_user = ValidationService.validate_session_token(token)
        if ValidationService.check_valid_admin(session_user):

            c = get_item_db('code',disc_str,'discounts')

            if not c :
                    if len(c) > 30 or not disc_str.isalpha():
                        raise HTTPException(
                                    status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Ensure the discount name has only letters, and is shorter than 30 characters."
                                )
                    discount = {
                        "amount" : None if amount == 0 else amount,
                        "created_at" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "lot_id" : None if loid == 0 else loid,
                        "code" : disc_str,
                        "percentage" : None if perc == 0 else perc,
                        "expiration_date" :None if exp_date == None else exp_date,
                        "user_id" : None if uid == 0 else uid
                        
                    }
           
                    create_data('discounts', discount)
                    return discount
            
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This value already exists."
            )        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user is not an admin.",
        )

    @staticmethod
    def edit_discount(token, id , discount):

        amount = discount.amount 
        loid = discount.lot_id
        code = discount.code
        perc = discount.percentage
        exp_date = discount.expiration_date
        uid = discount.user_id
        

        session_user = ValidationService.validate_session_token(token)
        if ValidationService.check_valid_admin(session_user):
            disc = get_item_db('id', id, 'discounts')[0]

            if disc :
                disc['amount'] = disc['amount'] if amount == None else amount
                disc['lot_id'] =  disc['lot_id'] if loid == 0 else loid
                disc['code'] = disc['code'] if code == None else code
                disc['percentage'] = disc['percentage'] if perc == 0 else perc
                disc['expiration_date'] = disc['expiration_date'] if exp_date == None else exp_date
                disc['user_id'] = disc['user_id'] if uid == 0 else uid

                
                change_data('discounts',disc,'id')
                
                return disc 
            else:
                 raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Item not found."
                )
            
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user is not an admin.",
        )
    
    @staticmethod
    def delete_discount(token, id):
        session_user = ValidationService.validate_session_token(token)
        if ValidationService.check_valid_admin(session_user):
            delete_data(id,'id','discounts')
            return {"Succes"}
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The user is not an admin.",
            )
        