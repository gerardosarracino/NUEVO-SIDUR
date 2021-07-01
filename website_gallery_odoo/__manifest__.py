# -*- coding: utf-8 -*-
{
    'name': "Website Gallery",
    'summary': """
        Used to view Image Gallery in website/Kanban""",
    'description': """
        Used to store, manage and view Images in Website Gallery view and Kanban view.
    """,
    'author': "Tintumon.M",
    'website': "www.tintumon.co.in",
    'category': 'Website',
    'version': '0.1',
    'depends': [
        'website',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/website_menu_data.xml',
        'views/website_gallery_views.xml',
        'views/website_gallery_templates.xml',
    ],
    'application': True,
}
