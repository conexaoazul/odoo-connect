# -*- coding: utf-8 -*-
import json
import logging
from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class EvolutionWebhookController(http.Controller):

    @http.route('/evolution/webhook', type='json', auth='public', methods=['POST'], csrf=False)
    def receive_webhook(self):
        try:
            payload = request.jsonrequest
            _logger.info(f"Received Evolution Webhook: {json.dumps(payload, indent=4)}")
            
            instance_id = payload.get('instance_id')
            event_type = payload.get('event_type')
            event_data = payload.get('event_data', {})
            
            account = request.env['whatsapp.account'].sudo().search([('evolution_instance_id', '=', instance_id)], limit=1)
            if not account:
                raise ValidationError(f"Instance with ID {instance_id} not found.")

            # Mapeando eventos para ações
            if event_type == 'application.startup':
                # Handle application startup
                account.evolution_instance_status = 'running'
                _logger.info(f"Application startup handled for {instance_id}")

            elif event_type == 'qrcode.updated':
                # Handle QR code update
                account.evolution_qrcode = event_data.get('qrcode')
                _logger.info(f"QR code updated for {instance_id}")

            elif event_type == 'connection.update':
                # Handle connection status update
                account.evolution_instance_status = event_data.get('status')
                _logger.info(f"Connection status updated for {instance_id}")

            elif event_type == 'messages.upsert':
                # Handle new message received
                self._handle_message_upsert(account, event_data)

            elif event_type == 'messages.update':
                # Handle message update
                self._handle_message_update(account, event_data)

            elif event_type == 'messages.delete':
                # Handle message delete
                self._handle_message_delete(account, event_data)

            elif event_type == 'new.jwt':
                # Handle new JWT token
                account.evolution_jwt_token = event_data.get('jwt')
                _logger.info(f"JWT token updated for {instance_id}")

            # Adicione mais eventos conforme necessário
            
            return {'status': 'success', 'message': 'Webhook processed successfully'}

        except ValidationError as e:
            _logger.error(f"ValidationError: {str(e)}")
            return {'status': 'error', 'message': str(e)}
        except Exception as e:
            _logger.error(f"Exception in Evolution Webhook processing: {str(e)}")
            return {'status': 'error', 'message': 'Internal Server Error'}

    def _handle_message_upsert(self, account, event_data):
        # Implement logic to handle new message upsert
        _logger.info(f"Handling message upsert for account {account.id}")

    def _handle_message_update(self, account, event_data):
        # Implement logic to handle message update
        _logger.info(f"Handling message update for account {account.id}")

    def _handle_message_delete(self, account, event_data):
        # Implement logic to handle message deletion
        _logger.info(f"Handling message deletion for account {account.id}")


    @http.route('/evolution/test_connection', type='http', auth='user')
    def test_connection(self):
        """
        A simple route to test the connection and ensure that the server is reachable.
        """
        return "Evolution API Webhook is up and running."


