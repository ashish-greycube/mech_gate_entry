frappe.ui.form.on("Purchase Receipt", {
    custom_gate_entry_number: function (frm) {
        if (frm.doc.custom_gate_entry_number) {
            frappe.call({
                method: "mech_gate_entry.api.fetch_supplier_delivery_no_and_date_from_gate_entry",
                args: {
                    "gate_entry_no": frm.doc.custom_gate_entry_number
                },
                callback: function (res) {
                    if (res && res.message) {
                        frm.set_value("bill_no", res.message.bill_no)
                        frm.set_value("supplier_invoice_date", res.message.bill_date)
                    }
                }
            })
        }
    }
});