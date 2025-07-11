import logging
from .whatsapp_router import WhatsAppRouterAgent
from .gemini_agent import GeminiAgent

logger = logging.getLogger(__name__)

class Orchestrator:
    def __init__(self, llm=None):
        """Initialize the orchestrator with the Gemini agent."""
        try:
            # Nous ignorons le paramètre llm car nous utilisons directement l'API Gemini
            self.gemini_agent = GeminiAgent()
            self.whatsapp_agent = WhatsAppRouterAgent()
            
            logger.info("Orchestrator initialized successfully with Gemini only")
        except Exception as e:
            logger.error(f"Failed to initialize orchestrator: {e}")
            raise

    def route_query(self, query: str):
        """Route the query to the appropriate agent based on intent detection."""
        try:
            # Vérifier si l'utilisateur veut contacter un humain
            if self._wants_human_contact(query):
                return self.whatsapp_agent.run(query)
            
            # Utiliser directement Gemini pour toutes les autres requêtes
            response = self.gemini_agent.run(query)
            
            # Si la réponse semble indiquer qu'une assistance humaine serait utile
            if self._should_offer_human_contact(response, query):
                human_contact = self.whatsapp_agent.get_human_contact_message(query)
                return {
                    "message": response,
                    "offer_human_contact": True,
                    "whatsapp_link": human_contact["whatsapp_link"],
                    "phone_number": human_contact["phone_number"]
                }
            
            return response
            
        except Exception as e:
            logger.error(f"Error routing query: {e}")
            return f"Je m'excuse, mais j'ai rencontré une erreur lors du traitement de votre demande. Veuillez réessayer ou contacter notre support."

    def _wants_human_contact(self, query: str) -> bool:
        """Détecte si l'utilisateur veut parler à un humain."""
        human_contact_keywords = ["parler à un humain", "agent humain", "personne réelle", 
                              "conseiller", "représentant", "parler à quelqu'un", 
                              "whatsapp", "téléphone", "contact direct", "vraie personne", 
                              "chat humain", "assistant humain", "humain"]
        
        query_lower = query.lower()
        for keyword in human_contact_keywords:
            if keyword in query_lower:
                logger.info(f"Detected human contact request with keyword: '{keyword}' in query: '{query}'")
                return True
        
        return False
    
    def _should_offer_human_contact(self, response: str, query: str) -> bool:
        """Détermine si on devrait proposer un contact humain basé sur la réponse et la requête."""
        # Si la requête est complexe (plus de 150 caractères)
        if len(query) > 150:
            logger.info(f"Query is complex (length > 150), suggesting human contact")
            return True
            
        # Si la réponse contient des phrases qui indiquent une incertitude
        uncertainty_phrases = [
            "je ne suis pas sûr", 
            "je n'ai pas cette information",
            "je ne peux pas", 
            "désolé", 
            "navré",
            "contacter un conseiller",
            "contacter directement"
        ]
        
        if any(phrase in response.lower() for phrase in uncertainty_phrases):
            logger.info(f"Response indicates uncertainty, suggesting human contact")
            return True
            
        return False
