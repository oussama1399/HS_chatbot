import os
import logging
import urllib.parse
try:
    from dotenv import load_dotenv
    
except ImportError:
    def load_dotenv():
        logging.warning("dotenv package not installed, environment variables may not be loaded")

class WhatsAppRouterAgent:
    def __init__(self):
        self.whatsapp_link = "https://api.whatsapp.com/message/ZREQ73H3OQTRJ1?autoload=1&app_absent=0"
        load_dotenv()
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.api_enabled = bool(self.account_sid and self.auth_token)
        self.phone_number = os.getenv('CONTACT_PHONE', "+212671506013")  # Numéro de téléphone par défaut
        logging.info("WhatsApp router agent initialized with direct contact link")
        
    def _generate_whatsapp_link(self, query: str) -> str:
        base_link = self.whatsapp_link
        separator = "&" if "?" in base_link else "?"
        encoded_message = urllib.parse.quote(f"Bonjour, j'ai une question concernant: {query}")
        return f"{base_link}{separator}text={encoded_message}"
        
    def run(self, query: str) -> str:
        whatsapp_link = self._generate_whatsapp_link(query)
        response = {
            "type": "whatsapp_redirect",
            "message": "Il semble que votre demande nécessite l'attention d'un conseiller. Souhaitez-vous discuter directement avec un membre de notre équipe ?",
            "whatsapp_link": whatsapp_link,
            "phone_number": self.phone_number
        }
        return response
        
    def get_human_contact_message(self, query: str) -> dict:
        """Generate a response with WhatsApp contact option."""
        whatsapp_link = self._generate_whatsapp_link(query)
        return {
            "message": "Je peux vous mettre en contact avec un conseiller pour une assistance plus personnalisée.",
            "whatsapp_link": whatsapp_link,
            "phone_number": self.phone_number
        }
