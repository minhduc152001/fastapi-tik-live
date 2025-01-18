from typing import List

from app.config.database import invoices_collection


async def list_invoices_service():
    invoices = invoices_collection.find()
    list_invoices: List[dict] = []
    for invoice in invoices:
        list_invoices.append({
            'id': str(invoice['_id']),
            'invoice_id': invoice['invoice_id'],
            'customer': invoice['customer'],
            'vendor': invoice['vendor'],
            'amount_per_month': invoice['amount_per_month'],
            'subscription_months': invoice['subscription_months'],
            'total_amount': invoice['total_amount'],
            'VAT': invoice['VAT'],
            'created_at': invoice['created_at'],
        })
    return list_invoices