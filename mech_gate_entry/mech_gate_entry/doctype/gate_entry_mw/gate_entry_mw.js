// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Gate Entry MW", {
	setup:function(frm) {
        frm.set_query('document_type', function() {
            if(frm.doc.entry_type) {
                return {
                    query: 'mech_gate_entry.mech_gate_entry.doctype.gate_entry_mw.gate_entry_mw.document_query',
                    filters: {
                        'entry_type' : frm.doc.entry_type
                    }
                }
            }
        })

        frm.set_query('document_name', function() {
            if (frm.doc.document_type == "Stock Entry"){
                if (frm.doc.stock_entry_type == ""){
                    frappe.msgprint("Please Select Stock Entry Type First.")
                }
                return {
                    query: 'mech_gate_entry.mech_gate_entry.doctype.gate_entry_mw.gate_entry_mw.stock_entry_query',
                    filters: {
                        'stock_entry_type' : frm.doc.stock_entry_type
                    }
                }
            }

            if (frm.doc.document_type == "Purchase Receipt") {
                return {
                    filters: {
                        'is_return' : 1,
                        'docstatus' : 1
                    }
                }
            }

            return {
                filters: {
                    'docstatus' : 1
                }
            }
        })  
    },


    document_name: function (frm) {
        frm.call({
            doc: frm.doc,
            method: 'fetch_items'
        })
    },
});
