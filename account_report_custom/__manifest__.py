{
    'name': 'Partner Ledger Report Custom',
    'version': '18.0',
    'author': 'Aswanth krishnan',
    'category': 'accounting',
    'website': '',
    'license': 'LGPL-3',
    'support': '',
    'description': """custom coloumn and filtration In Partner Ledger, Aged Receivable, Aged Payable Report""",
    'depends': ['account_reports'],

    'data': [
        'data/partner_ledger.xml',
        'data/aged_partner_balance.xml'
    ],
    "assets": {
        'web.assets_backend': [
            'account_report_custom/static/src/components/**/*',
        ],
        "web.assets_qweb": [],
    },

    'qweb': [],
    'images': ['static/description/icon.png'],
    'installable': True,
    'auto_install': False,
}

