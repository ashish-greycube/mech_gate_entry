import frappe
from frappe import _
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.desk.page.setup_wizard.setup_wizard import make_records

def after_migrate():
    custom_fields = {
        "Purchase Order Item" : [
            {
                'fieldname' : 'custom_gate_entry_qty',
                'fieldtype' : 'Float',
                'label' : _('Gate Entry Qty'),
                'is_custom_field' : 1,
                'is_system_generated' : 0,
                'allow_on_submit' : 1,
                'insert_after' : 'stock_qty',
                'read_only' : 1,
            }
        ], 

        "Subcontracting Order Item" : [
            {
                'fieldname' : 'custom_gate_entry_qty',
                'fieldtype' : 'Float',
                'label' : _('Gate Entry Qty'),
                'is_custom_field' : 1,
                'is_system_generated' : 0,
                'allow_on_submit' : 1,
                'insert_after' : 'conversion_factor',
                'read_only' : 1,
            }
        ],

        "Purchase Receipt Item" : [
            {
                'fieldname' : 'custom_gate_entry_qty',
                'fieldtype' : 'Float',
                'label' : _('Gate Entry Qty'),
                'is_custom_field' : 1,
                'is_system_generated' : 0,
                'allow_on_submit' : 1,
                'insert_after' : 'sample_quantity',
                'read_only' : 1,
            }
        ],

        "Delivery Note Item" : [
            {
                'fieldname' : 'custom_gate_entry_qty',
                'fieldtype' : 'Float',
                'label' : _('Gate Entry Qty'),
                'is_custom_field' : 1,
                'is_system_generated' : 0,
                'allow_on_submit' : 1,
                'insert_after' : 'returned_qty',
                'read_only' : 1,
            }
        ],

        "Stock Entry Detail" : [
            {
                'fieldname' : 'custom_gate_entry_qty',
                'fieldtype' : 'Float',
                'label' : _('Gate Entry Qty'),
                'is_custom_field' : 1,
                'is_system_generated' : 0,
                'allow_on_submit' : 1,
                'insert_after' : 'sample_quantity',
                'read_only' : 1,
            }
        ]
    }

    print("Adding Custom Fields In PO, SE, DN, PR & SCO.....")
    for dt, fields in custom_fields.items():
        print("*******\n %s: " % dt, [d.get("fieldname") for d in fields])
    create_custom_fields(custom_fields)