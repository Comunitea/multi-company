# -*- coding: utf-8 -*-
from openerp import api, fields, models, _, SUPERUSER_ID
from openerp.exceptions import ValidationError


class res_company(models.Model):

    _inherit = 'res.company'

    so_from_po = fields.Boolean(
        string="Create Sale Orders when buying to this company",
        help="Generate a Sale Order when a Purchase Order with this company "
        "as supplier is created.\n The intercompany user must at least be "
        "Sale User.")
    po_from_so = fields.Boolean(
        string="Create Purchase Orders when selling to this company",
        help="Generate a Purchase Order when a Sale Order with this company "
        "as customer is created.\n The intercompany user must at least be "
        "Purchase User.")
    auto_generate_invoices = fields.Boolean(
        string="Create Invoices/Refunds when encoding invoices/refunds "
        "made to this company",
        help="Generate Customer/Supplier Invoices (and refunds) "
        "when encoding invoices (or refunds) made to this company.\n "
        "e.g: Generate a Customer Invoice when a Supplier Invoice with "
        "this company as supplier is created.")
    auto_validation = fields.Boolean(
        string="Auto Validation",
        help="When a Sale Order/Purchase Order/Invoice is created by "
        "a multi company rule for this company, "
        "it will automatically validate it")
    intercompany_user_id = fields.Many2one(
        "res.users", string="Inter Company User",
        help="Responsible user for creation of documents triggered by "
        "intercompany rules. You cannot select the administrator, because "
        "the administrator by-passes the record rules, which is a problem "
        "when Odoo reads taxes on products.")
    warehouse_id = fields.Many2one(
        "stock.warehouse", string="Warehouse For Orders",
        help="Default value to set on Orders that "
        "will be created based on Orders made to this company")

    @api.model
    def _find_company_from_partner(self, partner_id):
        company = self.sudo().search([('partner_id', '=', partner_id)],
                                     limit=1)
        return company or False

    @api.one
    @api.constrains('po_from_so', 'so_from_po', 'auto_generate_invoices')
    def _check_intercompany_missmatch_selection(self):
        if ((self.po_from_so or self.so_from_po) and
                self.auto_generate_invoices):
            raise ValidationError(_(
                '''You cannot select to create invoices based on other invoices
                   simultaneously with another option '
                   ('Create Sale Orders when buying to this company' or
                   'Create Purchase Orders when selling to this company')!'''))

    @api.one
    @api.constrains('intercompany_user_id')
    def _check_intercompany_user_id(self):
        if self.intercompany_user_id:
            if self.intercompany_user_id.id == SUPERUSER_ID:
                raise ValidationError(_(
                    'You cannot use the administrator as the Inter Company '
                    'User, because the administrator by-passes record rules.'
                    ))
            if self.intercompany_user_id.company_id != self:
                raise ValidationError(_(
                    "The Inter Company User '%s' is attached to company "
                    "'%s', so you cannot select it for company '%s'.") % (
                        self.intercompany_user_id.name,
                        self.intercompany_user_id.company_id.name,
                        self.name))
            if len(self.intercompany_user_id.company_ids) > 1:
                raise ValidationError(_(
                    "You should not select '%s' as Inter Company User "
                    "because he is allowed to switch between several "
                    "companies, so there is no warranty that he will "
                    "stay in this company.") % self.intercompany_user_id.name)
