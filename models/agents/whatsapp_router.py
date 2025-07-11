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
        logging.info("WhatsApp router agent initialized with direct contact link")
    def _generate_whatsapp_link(self, query: str) -> str:
        base_link = self.whatsapp_link
        separator = "&" if "?" in base_link else "?"
        encoded_message = urllib.parse.quote(f"Customer Query: {query}")
        return f"{base_link}{separator}text={encoded_message}"
    def run(self, query: str) -> str:
        whatsapp_link = self._generate_whatsapp_link(query)
        return f"Your request needs more specialized attention.\n\nYou can contact our team directly via WhatsApp: {self.whatsapp_link}\n\nWe've prepared a message with your query for quick assistance."
