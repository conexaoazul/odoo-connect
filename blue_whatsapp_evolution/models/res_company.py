# -*- coding: utf-8 -*-
#############################################################################
#
#    BlueConnect Solutions Ltda.
#
#    Copyright (C) 2023-TODAY BlueConnect Solutions (<https://www.blueconnect.com.br>)
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

from odoo import models, fields, api
import json
import requests
import logging
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)
class ResCompany(models.Model):
    _inherit = 'res.company'

    evolution_api_url = fields.Char(
        string="URL da API Evolution",
        help="URL base da API Evolution usada para integração"
    )
    evolution_global_token = fields.Char(
        string="Token Global da API Evolution",
        help="Token global da API Evolution"
    )
    evolution_api_instance = fields.Char(
        string="Instância da API Evolution",
        help="Instância da API Evolution usada para integração"
    )

    api_response = fields.Text("Resposta da API") 
    
    def action_test_whatsapp_api(self):
        for company in self:
            if not company.evolution_api_url or not company.evolution_global_token or not company.evolution_api_instance:
                _logger.error("Campos necessários não preenchidos")
                return False

            url = f"{company.evolution_api_url}/instance/connectionState/{company.evolution_api_instance}"
            headers = {
                'apikey': company.evolution_global_token
            }

            try:
                response = requests.get(url, headers=headers)
                response_data = response.json()

                connection_state = response_data.get('instance', {}).get('state', 'close')  # Se 'state' não existir, assume 'close'

                if connection_state == 'open':
                    message = "✅ Conexão com a API estabelecida."
                else:
                    message = "❌ A conexão com a API foi recusada."

                # Cria um registro temporário com a mensagem
                response_record = self.env['api.response'].create({
                    'response': message
                })
                # Abre a janela modal com a resposta da API
                return {
                    'name': 'Resposta da API',
                    'type': 'ir.actions.act_window',
                    'res_model': 'api.response',
                    'view_mode': 'form',
                    'view_id': False,
                    'res_id': response_record.id,
                    'target': 'new',
                }

            except requests.RequestException as e:
                error_message = f"Erro ao fazer requisição: {str(e)}"
                
                # Cria um registro temporário com a mensagem de erro
                response_record = self.env['api.response'].create({
                    'response': error_message
                })

                # Abre a janela modal com a mensagem de erro
                return {
                    'name': 'Erro na Requisição',
                    'type': 'ir.actions.act_window',
                    'res_model': 'api.response',
                    'view_mode': 'form',
                    'view_id': False,
                    'res_id': response_record.id,
                    'target': 'new',
                }