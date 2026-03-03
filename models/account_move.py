from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    bareme_total_bilan      = fields.Float(string='Total Net Bilan (MDT)',    digits=(16, 3))
    bareme_amortissements   = fields.Float(string='Amortissements (MDT)',      digits=(16, 3))
    bareme_provisions       = fields.Float(string='Provisions (MDT)',          digits=(16, 3))
    bareme_total_brut       = fields.Float(string='Total Brut Bilan (MDT)',    digits=(16, 3),
                                           compute='_compute_total_brut', store=True)
    bareme_total_produit    = fields.Float(string='Total Produit TTC (MDT)',   digits=(16, 3))
    bareme_total_effectif   = fields.Float(string='Total Effectif Moyen',      digits=(16, 0))

    bareme_plafond_bilan    = fields.Float(string='Plafond Bilan (DT)',        digits=(16, 3))
    bareme_honor_bilan      = fields.Float(string='Honoraire Bilan (DT)',      digits=(16, 3))
    bareme_plafond_produit  = fields.Float(string='Plafond Produit (DT)',      digits=(16, 3))
    bareme_honor_produit    = fields.Float(string='Honoraire Produit (DT)',    digits=(16, 3))
    bareme_plafond_effectif = fields.Float(string='Plafond Effectif (DT)',     digits=(16, 3))
    bareme_honor_effectif   = fields.Float(string='Honoraire Effectif (DT)',   digits=(16, 3))
    bareme_applied          = fields.Boolean(string='Barème CAC Appliqué',     default=False)

    
    timbre_fiscal           = fields.Float(string='Timbre Fiscal (DT)',        digits=(16, 3), default=1.0)

    @api.depends('bareme_total_bilan', 'bareme_amortissements', 'bareme_provisions')
    def _compute_total_brut(self):
        for move in self:
            move.bareme_total_brut = round(
                move.bareme_total_bilan + move.bareme_amortissements + move.bareme_provisions, 3
            )

    def _montant_en_lettres(self, montant):
        try:
            from num2words import num2words
            montant = round(float(montant), 3)
            entier   = int(montant)
            millimes = round((montant - entier) * 1000)
            # Partie dinars
            texte = num2words(entier, lang='fr').upper() + " DINARS"
            # Partie millimes
            if millimes > 0:
                texte += " ET " + num2words(millimes, lang='fr').upper() + " MILLIMES"
            return texte
        except Exception:
            montant  = round(float(montant), 3)
            entier   = int(montant)
            millimes = round((montant - entier) * 1000)
            if millimes:
                return f"{entier} DINARS ET {millimes} MILLIMES"
            return f"{entier} DINARS"

    def action_open_bareme_honoraire(self):
        self.ensure_one()
        return {
            'type':      'ir.actions.act_window',
            'name':      'Barème Honoraire CAC',
            'res_model': 'bareme.honoraire.wizard',
            'view_mode': 'form',
            'target':    'new',
            'context': {
                'default_move_id':           self.id,
                'default_total_bilan':       self.bareme_total_bilan,
                'default_amortissements':    self.bareme_amortissements,
                'default_provisions':        self.bareme_provisions,
                'default_total_produit':     self.bareme_total_produit,
                'default_total_effectif':    self.bareme_total_effectif,
                'default_plafond_bilan':     self.bareme_plafond_bilan,
                'default_honor_bilan':       self.bareme_honor_bilan,
                'default_plafond_produit':   self.bareme_plafond_produit,
                'default_honor_produit':     self.bareme_honor_produit,
                'default_plafond_effectif':  self.bareme_plafond_effectif,
                'default_honor_effectif':    self.bareme_honor_effectif,
            },
        }

    def action_print_note_honoraire(self):
        self.ensure_one()
        return self.env.ref(
            'mozaiss_honoraires.action_report_note_honoraire'
        ).report_action(self)
