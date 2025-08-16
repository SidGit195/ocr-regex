# main.py
from fastapi import FastAPI, File, UploadFile, HTTPException
from models import Invoice, InvoiceItem
import invoice_parser
import tempfile
import os

app = FastAPI()

@app.post("/process-invoice/", response_model=Invoice)
async def process_invoice(file: UploadFile = File(...)):
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        # Process invoice
        text = invoice_parser.extract_text(temp_path)
        invoice_parser.debug_ocr(text)  # Check OCR output
        invoice_data = invoice_parser.parse_invoice(text)
        items = invoice_parser.extract_items(text)
        
        # Clean up temp file
        os.unlink(temp_path)
        
        # Prepare response
        return Invoice(
            invoice_number=invoice_data["invoice_number"],
            invoice_date=invoice_data["invoice_date"],
            customer_name=invoice_data["customer_name"],
            vendor_name=invoice_data["vendor_name"],
            total_amount=invoice_data["total_amount"],
            items=[InvoiceItem(**item) for item in items]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)