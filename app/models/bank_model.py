from typing import Optional

from pydantic import BaseModel


class CreateBankModel(BaseModel):
    bank_code: str
    bank_name: str
    bank_account_number: str

class BankModel(BaseModel):
    bank_code: Optional[str] = None
    bank_name: Optional[str] = None
    bank_account_number: Optional[str] = None

class BankDetailsModel(BaseModel):
    id: str
    bank_code: str
    bank_name: str
    bank_account_number: str