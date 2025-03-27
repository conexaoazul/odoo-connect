# -*- coding: utf-8 -*-
import json
import logging
import re
import requests
import base64
from odoo import models, fields
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)
class WhatsappSendMessage(models.TransientModel):
    """Este modelo é usado para enviar mensagens do WhatsApp através do Odoo."""
    _name = 'whatsapp.send.message.crm'
    _description = "Whatsapp Wizard"

    lead_id = fields.Many2one('crm.lead', string="Lead")
    mobile = fields.Char(related='lead_id.mobile', required=True, string="Número do WhatsApp")
    message = fields.Text(string="Mensagem", required=True)
    attachments_ids = fields.Many2many('ir.attachment', string="Anexar Arquivo")

    def check_whatsapp_account(self):
        pass

    def prepare_media(self, attachment, message_text):
        """Prepara arquivos e texto para API do WhatsApp de acordo com a especificação oficial"""
        try:
            mime_type = attachment.mimetype
            file_name = attachment.name
            media_type = 'document'

            # Determinar tipo de mídia
            type_mapping = {
                'image': ['image/jpeg', 'image/png', 'image/webp'],
                'video': ['video/mp4', 'video/3gp'],
                'document': ['application/pdf', 'text/plain']
            }
            for key, types in type_mapping.items():
                if mime_type in types:
                    media_type = key
                    break

            # Preparar conteúdo da mídia
            if attachment.url:
                media_content = attachment.url
            else:
                media_content = attachment.datas.decode('utf-8')

            if not (media_content.startswith('http') or len(media_content) > 256):
                raise ValueError("Formato de mídia inválido")

            return {
                "media": media_content,
                "mediatype": media_type,
                "mimetype": mime_type,
                "fileName": file_name,
                "caption": message_text
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

        # URL para enviar a mensagem
        if self.attachment_ids:
            url = f"{evolution_api_url}/message/sendMedia/{evolution_api_instance}"
        else:
            url = f"{evolution_api_url}/message/sendText/{evolution_api_instance}"
        
        # Preparando o payload
        phone_number = re.sub(r'[^0-9]', '', self.lead_id.partner_id.mobile)  # Acesso ao telefone através do partner_id
        if not phone_number:
            raise UserError(_("Este lead não tem número de telefone associado."))

        payload = {
            "number": phone_number,
            "text": self.message,  # Mensagem de texto
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

            if response.status_code == 200:
                _logger.info("Mensagem enviada com sucesso")
                status = 200
                body = f"Mensagem enviada com sucesso: {self.message}"
            else:
                _logger.error(f"Erro ao enviar mensagem: {response.status_code} - {response.text}")
                status = response.status_code
                body = f"Falha ao enviar. Status: {status}, {response.json().get('error', 'Unknown error')}"
        except Exception as e:
            _logger.error(f"Erro na requisição: {str(e)}")
            status = 500
            body = f"Erro inesperado na requisição: {str(e)}"
        
        # Criar a mensagem no canal de mensagens do Odoo
        post_values = {
            'body': body,
            'message_type': 'whatsapp_message',
            'subtype_id': self.env.ref('mail.mt_note').id  # Isso define o tipo da mensagem como "Nota"
        }

        # Criando a mensagem no Odoo (usando mail.message diretamente)
        try:
            partner_id = self.lead_id.partner_id if self.lead_id and self.lead_id.partner_id else None
            message = self.env['mail.message'].create({
                'body': body,
                'message_type': 'whatsapp_message',
                'model': self._name,
                'res_id': self.id,
                'partner_ids': partner_id.ids if partner_id else [],
                'subtype_id': self.env.ref('mail.mt_note').id,
            })
            _logger.info(f"Mensagem registrada no Odoo: {message.body}")
        except Exception as e:
            _logger.error(f"Erro ao registrar a mensagem no Odoo: {str(e)}")
