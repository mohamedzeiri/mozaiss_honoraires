from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BaremeHonoraireWizard(models.TransientModel):
    _name = 'bareme.honoraire.wizard'
    _description = 'Barème Honoraire CAC - Calcul automatique'

    move_id = fields.Many2one('account.move', string='Facture', required=True, ondelete='cascade')

    # ── Critère Bilan ─────────────────────────────────────────────────────────
    total_bilan      = fields.Float(string='Total Net Bilan (MDT)',    digits=(16, 3), default=0.0)
    amortissements   = fields.Float(string='+ Amortissements (MDT)',   digits=(16, 3), default=0.0)
    provisions       = fields.Float(string='+ Provisions (MDT)',       digits=(16, 3), default=0.0)
    total_brut_bilan = fields.Float(string='Total Brut Bilan (MDT)',   digits=(16, 3),
                                    compute='_compute_bilan', store=False)
    plafond_bilan    = fields.Float(string='Plafond (DT)',  digits=(16, 3), readonly=True)
    honor_bilan      = fields.Float(string='Honoraire (DT)',digits=(16, 3), readonly=True)

    # ── Critère Produits TTC ──────────────────────────────────────────────────
    total_produit    = fields.Float(string='Total Produit TTC (MDT)', digits=(16, 3), default=0.0)
    plafond_produit  = fields.Float(string='Plafond (DT)',  digits=(16, 3), readonly=True)
    honor_produit    = fields.Float(string='Honoraire (DT)',digits=(16, 3), readonly=True)

    # ── Critère Effectif Moyen ────────────────────────────────────────────────
    total_effectif   = fields.Float(string='Total Effectif Moyen', digits=(16, 0), default=0.0)
    plafond_effectif = fields.Float(string='Plafond (DT)',  digits=(16, 3), readonly=True)
    honor_effectif   = fields.Float(string='Honoraire (DT)',digits=(16, 3), readonly=True)

    # ── Calculs automatiques ──────────────────────────────────────────────────

    @api.depends('total_bilan', 'amortissements', 'provisions')
    def _compute_bilan(self):
        for wiz in self:
            wiz.total_brut_bilan = round(wiz.total_bilan + wiz.amortissements + wiz.provisions, 3)

    @api.onchange('total_bilan', 'amortissements', 'provisions')
    def _onchange_bilan(self):
        brut = round(self.total_bilan + self.amortissements + self.provisions, 3)
        plafond, honor, _ = self._calcul_bareme_brut(brut)
        self.plafond_bilan = plafond
        self.honor_bilan   = honor

    @api.onchange('total_produit')
    def _onchange_produit(self):
        plafond, honor, _ = self._calcul_bareme_produit(self.total_produit)
        self.plafond_produit = plafond
        self.honor_produit   = honor

    @api.onchange('total_effectif')
    def _onchange_effectif(self):
        plafond, honor, _ = self._calcul_bareme_effectif(self.total_effectif)
        self.plafond_effectif = plafond
        self.honor_effectif   = honor

    # ── Fonctions de barème ───────────────────────────────────────────────────

    @staticmethod
    def _calcul_bareme_brut(mt):
        som = plafond = honor = 0.0
        if 0 < mt < 300:
            plafond = 0; honor = 700; som = 700
        elif 300 <= mt < 1000:
            plafond = 700; honor = (mt - 300) * 1.15456; som = plafond + honor
        elif 1000 <= mt < 3000:
            plafond = 700 + 1081.92; honor = (mt - 1000) * 0.7728; som = plafond + honor
        elif 3000 <= mt < 7000:
            plafond = 700 + 1081.92 + 1545.6; honor = (mt - 3000) * 0.3864; som = plafond + honor
        elif 7000 <= mt < 15000:
            plafond = 700 + 1081.92 + 1545.6 + 1545.6; honor = (mt - 7000) * 0.1546; som = plafond + honor
        elif 15000 <= mt < 35000:
            plafond = 700 + 1081.92 + 1545.6 + 1545.6 + 1236.48; honor = (mt - 15000) * 0.1160; som = plafond + honor
        elif 35000 <= mt < 80000:
            plafond = 700 + 1081.92 + 1545.6 + 1545.6 + 1236.48 + 2320.8; honor = (mt - 35000) * 0.0773; som = plafond + honor
        elif 80000 <= mt < 200000:
            plafond = 700 + 1081.92 + 1545.6 + 1545.6 + 1236.48 + 2320.8 + 3477.6; honor = (mt - 80000) * 0.0388; som = plafond + honor
        elif 200000 <= mt < 500000:
            plafond = 700 + 1081.92 + 1545.6 + 1545.6 + 1236.48 + 2320.8 + 3477.6 + 4651.2; honor = (mt - 200000) * 0.0155; som = plafond + honor
        elif 500000 <= mt < 1000000:
            plafond = 700 + 1081.92 + 1545.6 + 1545.6 + 1236.48 + 2320.8 + 3477.6 + 4651.2 + 4644; honor = (mt - 500000) * 0.0116; som = plafond + honor
        elif mt >= 1000000:
            plafond = 700 + 1081.92 + 1545.6 + 1545.6 + 1236.48 + 2320.8 + 3477.6 + 4651.2 + 4644 + 5820; honor = (mt - 1000000) * 0.0078; som = plafond + honor
        return (round(max(plafond, 0), 3), round(max(honor, 0), 3), round(max(som, 0), 3))

    @staticmethod
    def _calcul_bareme_produit(mt):
        som = plafond = honor = 0.0
        if 0 < mt < 100:
            plafond = 0; honor = 500; som = 500
        elif 100 <= mt < 300:
            plafond = 500; honor = (mt - 100) * 3.4776; som = plafond + honor
        elif 300 <= mt < 700:
            plafond = 500 + 695.52; honor = (mt - 300) * 2.3184; som = plafond + honor
        elif 700 <= mt < 1500:
            plafond = 500 + 695.52 + 927.36; honor = (mt - 700) * 1.5456; som = plafond + honor
        elif 1500 <= mt < 3000:
            plafond = 500 + 695.52 + 927.36 + 1236.48; honor = (mt - 1500) * 0.7728; som = plafond + honor
        elif 3000 <= mt < 7500:
            plafond = 500 + 695.52 + 927.36 + 1236.48 + 1159.2; honor = (mt - 3000) * 0.3864; som = plafond + honor
        elif 7500 <= mt < 20000:
            plafond = 500 + 695.52 + 927.36 + 1236.48 + 1159.2 + 1738.8; honor = (mt - 7500) * 0.1933; som = plafond + honor
        elif 20000 <= mt < 50000:
            plafond = 500 + 695.52 + 927.36 + 1236.48 + 1159.2 + 1738.8 + 2416.5; honor = (mt - 20000) * 0.1546; som = plafond + honor
        elif 50000 <= mt < 120000:
            plafond = 500 + 695.52 + 927.36 + 1236.48 + 1159.2 + 1738.8 + 2416.5 + 4636.8; honor = (mt - 50000) * 0.0773; som = plafond + honor
        elif 120000 <= mt < 350000:
            plafond = 500 + 695.52 + 927.36 + 1236.48 + 1159.2 + 1738.8 + 2416.5 + 4636.8 + 5409.6; honor = (mt - 120000) * 0.0388; som = plafond + honor
        elif mt >= 350000:
            plafond = 500 + 695.52 + 927.36 + 1236.48 + 1159.2 + 1738.8 + 2416.5 + 4636.8 + 5409.6 + 8914.8; honor = (mt - 350000) * 0.0193; som = plafond + honor
        return (round(max(plafond, 0), 3), round(max(honor, 0), 3), round(max(som, 0), 3))

    @staticmethod
    def _calcul_bareme_effectif(mt):
        som = plafond = honor = 0.0
        if 0 < mt < 50:
            plafond = 0; honor = 800; som = 800
        elif 50 <= mt < 150:
            plafond = 800; honor = (mt - 50) * 13.1376; som = plafond + honor
        elif 150 <= mt < 500:
            plafond = 800 + 1313.76; honor = (mt - 150) * 7.7280; som = plafond + honor
        elif 500 <= mt < 1200:
            plafond = 800 + 1313.76 + 2704.8; honor = (mt - 500) * 3.8640; som = plafond + honor
        elif 1200 <= mt < 3000:
            plafond = 800 + 1313.76 + 2704.8 + 2704.8; honor = (mt - 1200) * 1.9320; som = plafond + honor
        elif 3000 <= mt < 7000:
            plafond = 800 + 1313.76 + 2704.8 + 2704.8 + 3477.6; honor = (mt - 3000) * 1.5456; som = plafond + honor
        elif mt >= 7000:
            plafond = 800 + 1313.76 + 2704.8 + 2704.8 + 3477.6 + 6182.4; honor = (mt - 7000) * 1.1592; som = plafond + honor
        return (round(max(plafond, 0), 3), round(max(honor, 0), 3), round(max(som, 0), 3))

    # ── Action principale ─────────────────────────────────────────────────────

    def action_validate(self):
        self.ensure_one()
        move = self.move_id

        if move.state != 'draft':
            raise UserError(
                _("Impossible de modifier une facture confirmée. "
                  "Remettez-la en brouillon d'abord.")
            )

        # Recalcul forcé
        brut = round(self.total_bilan + self.amortissements + self.provisions, 3)
        plafond_bilan,    honor_bilan,    _ = self._calcul_bareme_brut(brut)
        plafond_produit,  honor_produit,  _ = self._calcul_bareme_produit(self.total_produit)
        plafond_effectif, honor_effectif, _ = self._calcul_bareme_effectif(self.total_effectif)

        if honor_bilan == 0 and honor_produit == 0 and honor_effectif == 0:
            raise UserError(
                _("Aucun montant d'honoraire à transférer. "
                  "Veuillez saisir des montants valides.")
            )

        # Sauvegarde sur la facture
        move.write({
            'bareme_total_bilan':      self.total_bilan,
            'bareme_amortissements':   self.amortissements,
            'bareme_provisions':       self.provisions,
            'bareme_total_produit':    self.total_produit,
            'bareme_total_effectif':   self.total_effectif,
            'bareme_plafond_bilan':    plafond_bilan,
            'bareme_honor_bilan':      honor_bilan,
            'bareme_plafond_produit':  plafond_produit,
            'bareme_honor_produit':    honor_produit,
            'bareme_plafond_effectif': plafond_effectif,
            'bareme_honor_effectif':   honor_effectif,
            'bareme_applied':          True,
        })

        # Produits
        product_bilan    = self._get_or_create_product('Honoraires Bilan CAC')
        product_produit  = self._get_or_create_product('Honoraires Produits CAC')
        product_effectif = self._get_or_create_product('Honoraires Effectif Moyen CAC')

        # Supprime les anciennes lignes CAC
        old_lines = move.invoice_line_ids.filtered(
            lambda l: l.product_id and 'CAC' in (l.product_id.name or '')
        )
        old_lines.unlink()

        lines_vals = []
        if honor_bilan > 0:
            lines_vals.append({
                'move_id':    move.id,
                'product_id': product_bilan.id,
                'name':       f'Honoraires Bilan CAC - Total Brut {brut:.3f} MDT',
                'quantity':   1.0,
                'price_unit': honor_bilan,
                'account_id': self._get_account(product_bilan, move),
            })
        if honor_produit > 0:
            lines_vals.append({
                'move_id':    move.id,
                'product_id': product_produit.id,
                'name':       f'Honoraires Produits TTC CAC - Total {self.total_produit:.3f} MDT',
                'quantity':   1.0,
                'price_unit': honor_produit,
                'account_id': self._get_account(product_produit, move),
            })
        if honor_effectif > 0:
            lines_vals.append({
                'move_id':    move.id,
                'product_id': product_effectif.id,
                'name':       f'Honoraires Effectif Moyen CAC - Effectif {int(self.total_effectif)}',
                'quantity':   1.0,
                'price_unit': honor_effectif,
                'account_id': self._get_account(product_effectif, move),
            })

        # Récupère la taxe 19%
        tax_19 = self._get_tax_19()
        tax_ids = [(6, 0, [tax_19.id])] if tax_19 else []

        # Ajoute la taxe sur chaque ligne
        for line in lines_vals:
            line['tax_ids'] = tax_ids

        self.env['account.move.line'].create(lines_vals)
        return {'type': 'ir.actions.act_window_close'}

    def _get_tax_19(self):
        tax = self.env['account.tax'].search([
            ('amount', '=', 19),
            ('type_tax_use', '=', 'sale'),
            ('active', '=', True),
        ], limit=1)
        if not tax:
            tax = self.env['account.tax'].create({
                'name': 'TVA 19%',
                'amount': 19,
                'amount_type': 'percent',
                'type_tax_use': 'sale',
            })
        return tax

    def _get_or_create_product(self, name):
        product = self.env['product.product'].search(
            [('name', '=', name), ('type', '=', 'service')], limit=1
        )
        if not product:
            product = self.env['product.product'].create({'name': name, 'type': 'service'})
        return product

    def _get_account(self, product, move):
        accounts = product.product_tmpl_id.get_product_accounts()
        account = accounts.get('income')
        if not account:
            account = self.env['account.account'].search([
                ('account_type', '=', 'income'),
                ('company_id', '=', move.company_id.id),
            ], limit=1)
        return account.id if account else False
