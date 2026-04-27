import frappe

@frappe.whitelist()
def fetch_supplier_delivery_no_and_date_from_gate_entry(gate_entry_no):
    id = None
    date = None
    if gate_entry_no:
        doc = frappe.get_doc("Gate Entry MW", gate_entry_no)
        if doc:
            id = doc.bill_no
            date = doc.bill_date

    return {
        "bill_no": id,
        "bill_date": frappe.utils.getdate(date.replace("/", "-"))
    }