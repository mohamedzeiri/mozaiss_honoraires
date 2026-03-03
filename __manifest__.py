{
    'name': 'Bareme Honoraires CAC (Mozaiss vers Odoo)',
    'version': '19.0.1.1.0',
    'category': 'Accounting/Accounting',
    'summary': 'Calcul automatique des honoraires CAC selon barème commissariat',
    'description': """
        Migration de la fonctionnalité du barème de la note d'honoraire de Mozaiss vers Odoo.
        
        Fonctionnalités :
        - Bouton « Barème Honoraire CAC » sur les factures de vente
        - Calcul automatique des honoraires selon 3 critères :
          * Bilan (Total Net Bilan + Amortissements + Provisions)
          * Produits TTC
          * Effectif Moyen
        - Ajout automatique des lignes correspondantes dans la facture
        - Rapport Note d'Honoraire personnalisé
    """,
    'author': 'Migration Mozaiss',
    'depends': ['account', 'sale_management', 'purchase'],
    'data': [
        'data/product_data.xml',
        'views/account_move_views.xml',
        'wizard/bareme_honoraire_wizard_views.xml',
        'report/note_honoraire_report.xml',
        'report/note_honoraire_template.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
