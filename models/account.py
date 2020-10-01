# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _

class AccountMove(models.Model):
    _inherit = "account.move"

    firma_gface = fields.Char('Firma GFACE', copy=False)
    pdf_gface = fields.Binary('PDF GFACE', copy=False, attachment=False)
