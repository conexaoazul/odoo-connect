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
from odoo import models, _
import json
import requests
import logging

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    """Extends the res_partner model to add a new action for sending WhatsApp
    messages."""
    _inherit = 'res.partner'

    def action_send_msg(self):
        """This function is called when the user clicks the
         'Send WhatsApp Message' button on a partner's form view. It opens a
          new wizard to compose and send a WhatsApp message."""
        return {'type': 'ir.actions.act_window',
                'name': _('Whatsapp Message'),
                'res_model': 'whatsapp.send.message',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {'default_user_id': self.id}, }


    def send_whatsapp_message(self, phone, text, url, headers):
        """Envia uma mensagem para o WhatsApp via API e loga erros."""
        payload = json.dumps({
            "number": phone,
            "text": text
        })
        try:
            response = requests.post(url, headers=headers, data=payload)
            if response.status_code != 201:
                error_message = f"Falha ao enviar mensagem para o WhatsApp: {response.text}"
                _logger.error(error_message)
                return False, error_message
            return True, response.text
        except Exception as e:
            error_message = f"Erro ao enviar mensagem para o WhatsApp: {str(e)}"
            _logger.error(error_message)
            return False, error_message

