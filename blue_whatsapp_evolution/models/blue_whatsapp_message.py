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
from odoo import models, fields

class BlueWhatsappMessage(models.Model):
    _name = 'blue.whatsapp.message'
    _description = 'WhatsApp Message Log'

    partner_id = fields.Many2one('res.partner', string="Parceiro", help="Parceiro que recebeu a mensagem", required=True)
    lead_id = fields.Many2one('crm.lead', string="Lead", help="Lead que recebeu a mensagem")
    message = fields.Text(string="Mensagem", required=True, help="Conteúdo da mensagem enviada")
    status = fields.Selection([
        ('sent', 'Enviada'),
        ('failed', 'Falhada')
    ], string="Status", required=True, default='sent', help="Status da mensagem")
    sent_date = fields.Datetime(string="Data de Envio", default=fields.Datetime.now, help="Data e hora em que a mensagem foi enviada")

    def create_log_entry(self, partner, message, status):
        """Método para criar um log de mensagem WhatsApp"""
        lead = partner and partner.parent_id or False
        self.create({
            'partner_id': partner.id,
            'lead_id': lead.id if lead else False,
            'message': message,
            'status': status,
        })
