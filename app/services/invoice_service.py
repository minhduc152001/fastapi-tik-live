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
            'total_months': invoice['total_months'],
            'total_month_cost': invoice['total_month_cost'],
            'total_tiktok_ids': invoice['total_tiktok_ids'],
            'total_amount': invoice['total_amount'],
            'VAT': invoice['VAT'],
            'created_at': invoice['created_at'],
        })
    return list_invoices