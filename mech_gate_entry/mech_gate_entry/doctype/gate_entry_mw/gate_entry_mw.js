// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Gate Entry MW", {
	setup: function(frm) {
        frm.set_query('purchase_order', function() {
            if (frm.doc.supplier == null){
                frappe.msgprint("Please Select Supplier First.")
            }
            return {
                query: 'mech_gate_entry.mech_gate_entry.doctype.gate_entry_mw.gate_entry_mw.purchase_order_query',
                filters : {
                    'supplier' : frm.doc.supplier
                }
            }
        });

        frm.set_query('supplier', function() {
            return {
                query: 'mech_gate_entry.mech_gate_entry.doctype.gate_entry_mw.gate_entry_mw.supplier_query',
            }
        });

        frm.set_query('customer', function() {
            return {
                query: 'mech_gate_entry.mech_gate_entry.doctype.gate_entry_mw.gate_entry_mw.customer_query',
            }
        });

        frm.set_query('sales_order', function() {
            if (frm.doc.customer == null){
                frappe.msgprint("Please Select Customer First.")
            }
            return {
                query: 'mech_gate_entry.mech_gate_entry.doctype.gate_entry_mw.gate_entry_mw.sales_order_query',
                filters: {
                    'customer' : frm.doc.customer
                }
            }
        });
    },

    purchase_order: function (frm) {
        frm.call({
            doc: frm.doc,
            method: 'fetch_items'
        })
    },

    sales_order: function (frm) {
        frm.call({
            doc: frm.doc,
            method: 'fetch_items'
        })
    }
});
