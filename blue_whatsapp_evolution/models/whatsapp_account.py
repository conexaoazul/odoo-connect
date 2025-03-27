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

import logging
import mimetypes
import secrets
import string
from datetime import timedelta
import requests
import json
#from markupsafe import Markup

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
# from odoo.addons.whatsapp.tools.whatsapp_api import WhatsAppApi
# from odoo.addons.whatsapp.tools.whatsapp_exception import WhatsAppError
from odoo.tools import plaintext2html

_logger = logging.getLogger(__name__)


class WhatsAppAccount(models.Model):
    _name = 'blue.whatsapp.account'
    _description = 'WhatsApp Evolution Instancia'

    name = fields.Char(string="Name", tracking=1)
    active = fields.Boolean(default=True, tracking=6)
    allowed_company_ids = fields.Many2many(
        comodel_name='res.company', string="Allowed Company",
        default=lambda self: self.env.company)
    company_id = fields.Many2one('res.company', string="Empresa", default=lambda self: self.env.company)
    evolution_api_url = fields.Char(
        string="URL da API Evolution",
    #    related='company_id.evolution_api_url',
        readonly=True,
        help="URL base da API Evolution para integração, herdada da empresa."
    )
    evolution_global_token = fields.Char(
        string="Token Global da API Evolution",
    #    related='company_id.evolution_global_token',
        readonly=True,
        help="Token global da API Evolution, herdado da empresa."
    )
    evolution_instance_id = fields.Char(
        string="ID da Instância Evolution", 
        readonly=True, 
        copy=False, 
        help="Identificador único da instância criada na API Evolution."
    )
    evolution_instance_status = fields.Selection([
        ('stopped', 'Parada'),
        ('running', 'Em Execução'),
        ('restarting', 'Reiniciando'),
        ('error', 'Erro'),
    ], 
        string="Status da Instância", 
        readonly=True, 
        copy=False, 
        default='stopped',
        help="Estado atual da instância na API Evolution."
    )
    evolution_last_connection = fields.Datetime(
        string="Última Conexão", 
        readonly=True, 
        copy=False,
        help="Data e hora da última conexão bem-sucedida com a instância da API Evolution."
    )
    evolution_restart_count = fields.Integer(
        string="Contador de Mensagens Enviadas", 
        readonly=True, 
        default=0,
        help="Número de vezes que foi enviado mensagem por essa instância."
    )

    # Para centralizar as requisições à API:
    def _evolution_api_request(self, endpoint, params):
        base_url = self.company_id.evolution_api_url  # Acessando diretamente o campo da empresa
        headers = {
            'Authorization': f'Bearer {self.company_id.evolution_global_token}',  # Usando o token da empresa
            'Content-Type': 'application/json',
        }
        url = f"{base_url}{endpoint}"
        try:
            response = requests.post(url, json=params, headers=headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            _logger.error("HTTPError: %s", e)
            self.evolution_error_count += 1
            raise UserError(_("Falha na comunicação com a Evolution API"))
        return response.json()


    # Deletar Instância (Delete Instance)
    def delete_evolution_instance(self):
        self.ensure_one()
        if not self.evolution_instance_id:
            raise UserError(_("Nenhuma instância Evolution associada a esta conta"))
        response = self._evolution_api_request('delete_instance', {
            'instance_id': self.evolution_instance_id,
        })
        if response.get('status') == 'deleted':
            self.evolution_instance_id = False
            self.evolution_instance_status = 'stopped'
        else:
            self.evolution_error_count += 1
            raise UserError(_("Falha ao deletar a instância Evolution"))
        
    #Logout Instância (Logout Instance)
    def logout_evolution_instance(self):
        self.ensure_one()
        if not self.evolution_instance_id:
            raise UserError(_("Nenhuma instância Evolution associada a esta conta"))
        response = self._evolution_api_request('logout_instance', {
            'instance_id': self.evolution_instance_id,
        })
        if response.get('status') == 'logged_out':
            self.evolution_instance_status = 'stopped'
        else:
            self.evolution_error_count += 1
            raise UserError(_("Falha ao desconectar da instância Evolution"))
        
    # Deletar Instância (Delete Instance)
    def delete_evolution_instance(self):
        self.ensure_one()
        if not self.evolution_instance_id:
            raise UserError(_("Nenhuma instância Evolution associada a esta conta"))
        response = self._evolution_api_request('delete_instance', {
            'instance_id': self.evolution_instance_id,
        })
        if response.get('status') == 'deleted':
            self.evolution_instance_id = False
            self.evolution_instance_status = 'stopped'
        else:
            self.evolution_error_count += 1
            raise UserError(_("Falha ao deletar a instância Evolution"))
        
    # Logout Instância (Logout Instance)
    def logout_evolution_instance(self):
        self.ensure_one()
        if not self.evolution_instance_id:
            raise UserError(_("Nenhuma instância Evolution associada a esta conta"))
        response = self._evolution_api_request('logout_instance', {
            'instance_id': self.evolution_instance_id,
        })
        if response.get('status') == 'logged_out':
            self.evolution_instance_status = 'stopped'
        else:
            self.evolution_error_count += 1
            raise UserError(_("Falha ao desconectar da instância Evolution"))
        
    # Status da Conexão (Connection Status)
    def get_evolution_connection_status(self):
        self.ensure_one()
        if not self.evolution_instance_id:
            raise UserError(_("Nenhuma instância Evolution associada a esta conta"))
        response = self._evolution_api_request('connection_status', {
            'instance_id': self.evolution_instance_id,
        })
        status = response.get('status')
        if status:
            self.evolution_instance_status = status
        else:
            self.evolution_error_count += 1
            raise UserError(_("Falha ao obter o status da conexão da instância Evolution"))
        
    #Reiniciar Instância (Restart Instance)
    def restart_evolution_instance(self):
        self.ensure_one()
        if not self.evolution_instance_id:
            raise UserError(_("Nenhuma instância Evolution associada a esta conta"))
        response = self._evolution_api_request('restart_instance', {
            'instance_id': self.evolution_instance_id,
        })
        if response.get('status') == 'restarting':
            self.evolution_instance_status = 'restarting'
            self.evolution_restart_count += 1
        else:
            self.evolution_error_count += 1
            raise UserError(_("Falha ao reiniciar a instância Evolution"))
        
    # Status da Conexão (Connection Status)
    def get_evolution_connection_status(self):
        self.ensure_one()
        if not self.evolution_instance_id:
            raise UserError(_("Nenhuma instância Evolution associada a esta conta"))
        response = self._evolution_api_request('connection_status', {
            'instance_id': self.evolution_instance_id,
        })
        status = response.get('status')
        if status:
            self.evolution_instance_status = status
        else:
            self.evolution_error_count += 1
            raise UserError(_("Falha ao obter o status da conexão da instância Evolution"))
        
    # Logout Instância (Logout Instance)
    def logout_evolution_instance(self):
        self.ensure_one()
        if not self.evolution_instance_id:
            raise UserError(_("Nenhuma instância Evolution associada a esta conta"))
        response = self._evolution_api_request('logout_instance', {
            'instance_id': self.evolution_instance_id,
        })
        if response.get('status') == 'logged_out':
            self.evolution_instance_status = 'stopped'
        else:
            self.evolution_error_count += 1
            raise UserError(_("Falha ao desconectar da instância Evolution"))
        
        
    # Buscar Instâncias (Fetch Instances)
    def fetch_evolution_instances(self):
        response = self._evolution_api_request('fetch_instances', {
            'app_uid': self.app_uid,
            'app_secret': self.app_secret,
            'account_uid': self.account_uid,
        })
        # Processar a resposta para atualizar registros locais ou executar ações necessárias
        # Exemplo: Atualizar a lista de instâncias ou registrar novas instâncias no Odoo
        
    #Conectar Instância (Instance Connect)
    def connect_evolution_instance(self):
        self.ensure_one()
        if not self.evolution_instance_id:
            raise UserError(_("Nenhuma instância Evolution associada a esta conta"))
        response = self._evolution_api_request('connect_instance', {
            'instance_id': self.evolution_instance_id,
        })
        if response.get('status') == 'connected':
            self.evolution_last_connection = fields.Datetime.now()
        else:
            raise UserError(_("Falha ao conectar à instância Evolution"))
        
    #Criar Instância (Create Instance)
    def create_evolution_instance(self):
        self.ensure_one()
        response = self._evolution_api_request('create_instance', {
            'app_uid': self.app_uid,
            'app_secret': self.app_secret,
            'account_uid': self.account_uid,
        })
        if response.get('instance_id'):
            self.evolution_instance_id = response['instance_id']
            self.evolution_instance_status = 'running'
            self.evolution_last_connection = fields.Datetime.now()
            self.evolution_restart_count = 0
            self.evolution_error_count = 0
        else:
            raise UserError(_("Falha ao criar instância no Evolution API"))