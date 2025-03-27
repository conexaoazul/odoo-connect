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
import json
import logging
import re
import requests
import base64
from odoo import models, fields
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)
class WhatsappSendMessage(models.TransientModel):
    """This model is used for sending WhatsApp messages through Odoo."""
    _name = 'whatsapp.send.message'
    _description = "Enviar Whatsapp Mensagem"


    user_id = fields.Many2one('res.partner', string="Contato")
    mobile = fields.Char(related='user_id.mobile', required=True, string="Número do WhatsApp")
    message = fields.Text(string="Mensagem", required=True)
    attachment_ids = fields.Many2many('ir.attachment', string="Anexar Arquivo")

    def check_whatsapp_account(self):
        pass



    def prepare_media(self, attachment, message_text):
        """Prepara arquivos e texto para API do WhatsApp de acordo com a especificação oficial"""
        try:
            # 1. Coletar metadados básicos
            mime_type = attachment.mimetype
            file_name = attachment.name
            media_type = 'document'
            
            # 2. Determinar tipo de mídia correto
            type_mapping = {
                'image': ['image/jpeg', 'image/png', 'image/webp'],
                'video': ['video/mp4', 'video/3gp'],
                'document': ['application/pdf', 'text/plain']
            }
            for key, types in type_mapping.items():
                if mime_type in types:
                    media_type = key
                    break

            # 3. Preparar conteúdo da mídia
            if attachment.url:
                media_content = attachment.url
                _logger.info(f"Usando URL: {media_content[:50]}...")
            else:
                # Dados em base64 SEM prefixo data URI
                media_content = attachment.datas.decode('utf-8')
                _logger.debug(f"Base64 gerado: {media_content[:30]}...")

            # 4. Validar formato final
            if not (media_content.startswith('http') or len(media_content) > 256):
                raise ValueError("Formato de mídia inválido")

            # Retornar a mídia e o texto (mensagem)
            return {
                "media": media_content,  # Apenas base64 ou URL
                "mediatype": media_type,
                "mimetype": mime_type,
                "fileName": file_name,
                "caption": message_text  # Colocando o texto da mensagem no caption
            }

        except Exception as e:
            _logger.error(f"Falha na preparação: {str(e)}")
            return None



    def action_send_message(self): 
        company = self.env.user.company_id
        if company:
            evolution_api_url = company.evolution_api_url
            evolution_global_token = company.evolution_global_token
            evolution_api_instance = company.evolution_api_instance
        else:
            _logger.error("Empresa não encontrada")
            return

        # Definindo o URL para envio da mensagem (texto ou mídia)
        if self.attachment_ids:
            url = f"{evolution_api_url}/message/sendMedia/{evolution_api_instance}"
        else:
            url = f"{evolution_api_url}/message/sendText/{evolution_api_instance}"
        
        # Preparando o payload
        payload = {
            "number": re.sub(r'[^0-9]', '', self.user_id.mobile),
            "text": self.message,
            "linkPreview": False,
            "mentionsEveryOne": False,
        }

        headers = {
            "Content-Type": "application/json",
            'apikey': evolution_global_token
        }

        media_urls = []
        if self.attachment_ids:
            for attachment in self.attachment_ids:
                media_data = self.prepare_media(attachment, self.message)
                if media_data:
                    media_urls.append(media_data)

        if media_urls:
            payload["media"] = media_urls[0]["media"]
            payload["mediatype"] = media_urls[0]["mediatype"]
            payload["mimetype"] = media_urls[0]["mimetype"]
            payload["fileName"] = media_urls[0]["fileName"]
            payload["caption"] = media_urls[0]["caption"]

        try:
            response = requests.post(url, data=json.dumps(payload), headers=headers)
            response_data = response.json()
            
            # Log the entire response for debugging
            _logger.debug(f"Response from API: {response_data}")
            
            if response.status_code == 201:
                status = 'sent'
                body = f"Mensagem enviada com sucesso para {self.user_id.mobile}: {self.message}"
            else:
                status = 'failed'
                body = f"Falha ao enviar. Status: {response.status_code}, {response_data.get('error', 'Unknown error')}"
        except Exception as e:
            status = 'failed'
            body = f"Erro inesperado na requisição: {str(e)}"

        # Garantir que partner_id seja preenchido corretamente
        partner_id = None
        if hasattr(self.user_id, 'partner_id') and self.user_id.partner_id:
            partner_id = self.user_id.partner_id.id  # Para res.partner
        elif hasattr(self.user_id, 'partner_id') and self.user_id.partner_id is None and hasattr(self.user_id, 'id'):
            partner_id = self.user_id.id  # Para crm.lead

        if partner_id:
            self.env['blue.whatsapp.message'].create({
                'partner_id': partner_id,
                'lead_id': self.user_id.id if hasattr(self.user_id, 'id') else False,
                'message': self.message,
                'status': status,
            })
        else:
            _logger.error(f"Erro: Nenhum parceiro associado ao registro. user_id: {self.user_id}.")

        post_values = {
            'body': body,
            'message_type': 'comment',  
            'subtype_id': self.env.ref('mail.mt_note').id  
        }

        try:
            partner_id = self.user_id.partner_id if hasattr(self.user_id, 'partner_id') else None
            message = self.env['mail.message'].create({
                'body': body,
                'message_type': 'comment', 
                'model': self._name,
                'res_id': self.id,
                'partner_ids': partner_id.ids if partner_id else [],
                'subtype_id': self.env.ref('mail.mt_note').id,
            })
        except Exception as e:
            _logger.error(f"Erro ao registrar a mensagem no Odoo: {str(e)}")

