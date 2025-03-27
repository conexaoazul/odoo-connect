# -*- coding: utf-8 -*-
#############################################################################
#
#    BlueConnect Solutions Ltda.
#
#    Copyright (C) 2024-TODAY BlueConnect Solutions (<https://www.conexaoazul.com>)
#    Author: Diego Santos (diego.blueconenct@gmail.com)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
{
    'name': 'Integration WhatsApp Evolution API - Base',
    'version': '17.0.1.0.0',
    'category': 'Extra Tools',
    'summary': 'WhatsApp Web, Odoo-WhatsApp Integration, Evolution API, WhatsApp Connector for Odoo, WhatsApp Messaging, Odoo WhatsApp, WhatsApp Integration, Odoo 17.0, Odoo WhatsApp API Connector',
    'description': '''
        This module integrates Odoo 17.0 with the Evolution API to enable the sending of WhatsApp messages directly from the Odoo platform. 
        By utilizing the WhatsApp Web API provided by Evolution, businesses can send messages to their contacts using the official WhatsApp Web interface.
        
        Key Features:
        - Seamless WhatsApp messaging integration using Evolution API.
        - Send messages to contacts directly from Odoo.
        - Automatically register and configure your Evolution API instance in Odoo using the `res.company` model.
        - Easily manage and configure the connection to the Evolution API from the company settings.
        - A user-friendly interface for sending messages from Odoo without leaving the platform.

        This module provides businesses with a low-cost, highly effective solution to engage with customers and clients through WhatsApp, improving customer communication and support.
    ''',
    'author': 'Diego Santos <diego.blueconnect@gmail.com>',
    'maintainer': 'Conexão Azul Digital Ltda',
    'company': 'Conexão Azul Digital Ltda',
    'website': 'https://www.conexaoazul.com',
    'depends': ['base', 'contacts', 'crm'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'views/view_blue_whatsapp_account.xml',
        'views/company_whatsapp_integration_views.xml',
        'wizard/whatsapp_send_message_views.xml',
        'views/crm_lead_views.xml',
        'views/view_api_response_form.xml',
    ],
    'images': ['static/description/banner.jpg'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
    #'price': 90.00,
    'currency': 'USD'
}