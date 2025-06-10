# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def document_query(doctype, txt, searchfield, start, page_len, filters, as_dict=False):
	if filters.get('entry_type') == "Inward":
		doctype_list = frappe.db.sql('''
			SELECT tdt.name
			FROM tabDocType tdt 
			WHERE (tdt.module = 'Subcontracting' OR tdt.module = 'Buying')
			AND tdt.istable = 0 
			AND tdt.name LIKE  '%Order%';
		''', debug=1)
	
	elif filters.get('entry_type') == 'Outward':
		doctype_list = frappe.db.sql('''
			SELECT tdt.name
			FROM tabDocType tdt 
			WHERE tdt.module = 'Stock'
			AND tdt.istable = 0 
			AND tdt.name IN  ('Delivery Note', 'Stock Entry', 'Purchase Receipt');
		''')
	return doctype_list


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def stock_entry_query(doctype, txt, searchfield, start, page_len, filters, as_dict=False):
	stock_entries = frappe.db.sql(
		'''
            SELECT 
				IF(SUM(tsed.qty) != SUM(tsed.custom_gate_entry_qty), tse.name, NULL), tse.posting_date
			FROM 
				`tabStock Entry` tse
			INNER JOIN 
				`tabStock Entry Detail` tsed 
			ON 
				tse.name = tsed.parent
			WHERE
				tse.stock_entry_type = '{0}' AND tse.docstatus = 1 AND tse.name like %(txt)s
			GROUP BY 
				(tse.name);
        '''.format(filters.get('stock_entry_type')), {"txt": "%%%s%%" % txt}
		)
	entries = []
	for se in stock_entries:
		if None not in se:
			entries.append(se)
	return entries


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def delivery_note_query(doctype, txt, searchfield, start, page_len, filters, as_dict=False):
	dn_entries = frappe.db.sql(
		'''
            SELECT 
				IF(SUM(tdni.qty) != SUM(tdni.custom_gate_entry_qty), tdn.name, NULL), tdn.customer, tdn.posting_date
			FROM 
				`tabDelivery Note` tdn 
			INNER JOIN 
				`tabDelivery Note Item` tdni 
			ON 
				tdn.name = tdni.parent
			WHERE 
				tdn.docstatus = 1 AND tdn.name like %(txt)s
			GROUP BY 
				(tdn.name);
        ''', {"txt": "%%%s%%" % txt}
		)
	entries = []
	for dn in dn_entries:
		if None not in dn:
			entries.append(dn)
	return entries


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def purchase_receipt_query(doctype, txt, searchfield, start, page_len, filters, as_dict=False):
	pr_entries = frappe.db.sql(
		'''
           SELECT 
				IF(SUM(tpri.qty) != SUM(tpri.custom_gate_entry_qty), tpr.name, NULL), tpr.supplier, tpr.posting_date
			FROM 
			`tabPurchase Receipt` tpr 
			INNER JOIN 
				`tabPurchase Receipt Item` tpri 
			ON 
				tpr.name = tpri.parent
			WHERE 
				tpr.docstatus = 1 AND tpr.is_return = 1 AND tpr.name like %(txt)s
			GROUP BY 
				(tpr.name);
        ''', {"txt": "%%%s%%" % txt}
		)
	entries = []
	for pr in pr_entries:
		if None not in pr:
			entries.append(pr)
	return entries


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def purchase_order_query(doctype, txt, searchfield, start, page_len, filters, as_dict=False):
	po_entries = frappe.db.sql(
		'''
           SELECT 
				IF(SUM(tpoi.qty) != SUM(tpoi.custom_gate_entry_qty), tpo.name, NULL), tpo.supplier, tpo.transaction_date
			FROM 
			`tabPurchase Order` tpo 
			INNER JOIN 
				`tabPurchase Order Item` tpoi 
			ON 
				tpo.name = tpoi.parent
			WHERE 
				tpo.docstatus = 1 AND tpo.name like %(txt)s
			GROUP BY 
				(tpo.name);
        ''', {"txt": "%%%s%%" % txt}
		)
	entries = []
	for po in po_entries:
		if None not in po:
			entries.append(po)
	return entries


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def subcontracting_query(doctype, txt, searchfield, start, page_len, filters, as_dict=False):
	sc_entries = frappe.db.sql(
		'''
           	SELECT 
				IF(SUM(tsoi.qty) != SUM(tsoi.custom_gate_entry_qty), tso.name, NULL), tso.supplier, tso.transaction_date
			FROM 
			`tabSubcontracting Order` tso 
			INNER JOIN 
				`tabSubcontracting Order Item` tsoi 
			ON 
				tso.name = tsoi.parent
			WHERE 
				tso.docstatus = 1
			GROUP BY 
				(tso.name);
        ''', {"txt": "%%%s%%" % txt}
		)
	entries = []
	for sc in sc_entries:
		if None not in sc:
			entries.append(sc)
	return entries


class GateEntryMW(Document):
	def validate(self):
		self.validate_gate_qty()

	def on_submit(self):
		self.update_gate_qty_on_submit()

	def on_cancel(self):
		self.update_gate_entry_on_cancel()

	@frappe.whitelist()
	def fetch_items(self):
		if self.entry_type == "Inward":
			document_type = self.document_type
			document_name = self.document_name

			if document_type != None and document_name != None:
				if document_type == "Purchase Order":
					item_doc = frappe.get_doc("Purchase Order", document_name)
					self.supplier = frappe.db.get_value('Purchase Order', document_name, 'supplier')
				elif document_type == "Subcontracting Order":
					item_doc = frappe.get_doc("Subcontracting Order", document_name)
					self.supplier = frappe.db.get_value('Subcontracting Order', document_name, 'supplier')

				if item_doc != None:
					self.items = []
					for item in item_doc.items:
						self.append('items', {
							'item_code' : item.item_code,
							'item_name' : item.item_name,
							'description' : item.description,
							'original_qty' : item.qty,
							'gate_entry_quantity': item.qty - item.custom_gate_entry_qty,
							'hex_code' : item.name,
							'prev_gate_entry_quantity' : item.custom_gate_entry_qty
						})

		elif self.entry_type == "Outward":
			if self.entry_type == "Outward":
				document_type = self.document_type
				document_name = self.document_name

				if document_type != None and document_name != None:
					if document_type == "Delivery Note":
						item_doc = frappe.get_doc("Delivery Note", document_name)
						self.customer = frappe.db.get_value('Delivery Note', document_name, 'customer')
					elif document_type == "Purchase Receipt":
						item_doc = frappe.get_doc("Purchase Receipt", document_name)
						self.supplier = frappe.db.get_value('Purchase Receipt', document_name, 'supplier')
					elif document_type == "Stock Entry": 
						item_doc = frappe.get_doc("Stock Entry", document_name)

					if item_doc != None:
						self.items = []
						for item in item_doc.items:
							self.append('items', {
								'item_code' : item.item_code,
								'item_name' : item.item_name if item.item_name != None else " ",
								'description' : item.description,
								'original_qty' : item.qty,
								'gate_entry_quantity': item.qty - item.custom_gate_entry_qty,
								'hex_code' : item.name,
								'prev_gate_entry_quantity' : item.custom_gate_entry_qty
							})

	def validate_gate_qty(self):
		if self.items != None and self.document_type != None and self.document_name != None:
			for item in self.items:
				if item.hex_code != None:
					curr_gate_qty = item.gate_entry_quantity
					curr_prev_gate_qty = item.prev_gate_entry_quantity
					curr_org_qty = item.original_qty

					if 	self.document_type == "Purchase Receipt":
						if (curr_gate_qty < (curr_org_qty - curr_prev_gate_qty)):
							frappe.throw("Current Gate Entry Qty Should Be Less Than Remaining Qty For Item {0}".format(frappe.bold(item.item_code)))
					else:
						if (curr_gate_qty > (curr_org_qty - curr_prev_gate_qty)):
							frappe.throw("Current Gate Entry Qty Should Be Less Than Remaining Qty For Item {0}".format(frappe.bold(item.item_code)))

	def update_gate_qty_on_submit(self):
		document_type = self.document_type
		if document_type != None:
			if document_type == "Purchase Order":
				child_doc = "Purchase Order Item"
			elif document_type == "Subcontracting Order":
				child_doc = "Subcontracting Order Item"
			elif document_type == "Delivery Note":
				child_doc = "Delivery Note Item"
			elif document_type == "Purchase Receipt":
				child_doc = "Purchase Receipt Item"
			elif document_type == "Stock Entry":
				child_doc = "Stock Entry Detail"

			for item in self.items:
				if item.hex_code != None:
					prev_ge_qty = frappe.db.get_value(child_doc, item.hex_code, 'custom_gate_entry_qty')
					curr_ge_qty = item.gate_entry_quantity
					
					total_ge_qty = prev_ge_qty + curr_ge_qty
					frappe.db.set_value(child_doc, item.hex_code, 'custom_gate_entry_qty', total_ge_qty)
	
	def update_gate_entry_on_cancel(self):
		document_type = self.document_type
		if document_type != None:
			if document_type == "Purchase Order":
				child_doc = "Purchase Order Item"
			elif document_type == "Subcontracting Order":
				child_doc = "Subcontracting Order Item"
			elif document_type == "Delivery Note":
				child_doc = "Delivery Note Item"
			elif document_type == "Purchase Receipt":
				child_doc = "Purchase Receipt Item"
			elif document_type == "Stock Entry":
				child_doc = "Stock Entry Detail"	

			for item in self.items:
				if item.hex_code != None:
					prev_ge_qty = frappe.db.get_value(child_doc, item.hex_code, 'custom_gate_entry_qty')
					curr_ge_qty = item.gate_entry_quantity
					
					updated_ge_qty = prev_ge_qty - curr_ge_qty
					frappe.db.set_value(child_doc, item.hex_code, 'custom_gate_entry_qty', updated_ge_qty)