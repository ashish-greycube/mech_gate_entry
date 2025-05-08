# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class GateEntryMW(Document):
	@frappe.whitelist()
	def fetch_items(self):
		if self.entry_type == "Inward":
			purchase_order = self.purchase_order
			po_doc = frappe.get_doc('Purchase Order', purchase_order)

			if po_doc != None:
				self.items = []
				for item in po_doc.items:
					self.append('items', {
						'item_code' : item.item_code,
						'item_name' : item.item_name,
						'description' : item.description,
						'quantity' : item.qty
					})
			
		elif self.entry_type == "Outward":
			sales_order = self.sales_order
			so_doc = frappe.get_doc('Sales Order', sales_order)
			
			if so_doc != None:
				self.items = []
				for item in so_doc.items:
					self.append('items', {
						'item_code' : item.item_code,
						'item_name' : item.item_name,
						'description' : item.description,
						'quantity' : item.qty
					})


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def supplier_query(doctype, txt, searchfield, start, page_len, filters, as_dict=False):
	suppliers = frappe.db.sql(
				'''
					SELECT DISTINCT(tpo.supplier)
					FROM `tabPurchase Order` tpo 
					WHERE tpo.docstatus = 1 AND supplier like %(txt)s AND tpo.name NOT IN (SELECT purchase_order FROM `tabGate Entry MW` tgem WHERE tgem.entry_type = "Inward");
				''', {"txt": "%%%s%%" % txt})
	return suppliers

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def purchase_order_query(doctype, txt, searchfield, start, page_len, filters, as_dict=False):
	purchaseOrders = frappe.db.sql(
				'''
					SELECT 
						tpo.name 
					FROM 
						`tabPurchase Order` tpo
					WHERE 
						tpo.docstatus = 1 
					AND 
						tpo.supplier = '{0}' AND name like %(txt)s  AND tpo.name NOT IN (SELECT tgem.purchase_order FROM `tabGate Entry MW` tgem WHERE tgem.entry_type = "Inward")
				'''.format(filters.get('supplier')),  {"txt": "%%%s%%" % txt})
	return purchaseOrders

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def customer_query(doctype, txt, searchfield, start, page_len, filters, as_dict=False):
	customers = frappe.db.sql(
				'''
					SELECT DISTINCT(tso.customer)
					FROM `tabSales Order` tso 
					WHERE tso.docstatus = 1 AND customer like %(txt)s AND tso.name NOT IN (SELECT sales_order FROM `tabGate Entry MW` tgem WHERE tgem.entry_type = "Outward");
				''',{"txt": "%%%s%%" % txt})
	return customers


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def sales_order_query(doctype, txt, searchfield, start, page_len, filters, as_dict=False):
	salesOrders = frappe.db.sql(
		'''
			SELECT 
				tso.name 
			FROM 
				`tabSales Order` tso
			WHERE 
				tso.docstatus = 1 
			AND 
				tso.customer = '{0}' AND tso.name NOT IN (SELECT tgem.sales_order FROM `tabGate Entry MW` tgem WHERE tgem.entry_type = "Outward");
		'''.format(filters.get('customer')), {"txt": "%%%s%%" % txt})
	return salesOrders
