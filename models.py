# models.py
from pydantic import BaseModel
from typing import List, Optional

class InvoiceItem(BaseModel):
    item_description: Optional[str]
    quantity: Optional[str]
    unit_price: Optional[str]
    total_amount: Optional[str]

class Invoice(BaseModel):
    invoice_number: Optional[str]
    invoice_date: Optional[str]
    customer_name: Optional[str]
    vendor_name: Optional[str]
    total_amount: Optional[str]
    items: List[InvoiceItem] = []