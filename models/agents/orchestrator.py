import logging
from .lead_qualifier import LeadQualifierAgent
from .rag_agent import RAGAgent
from .faq_agent import FAQAgent
from .whatsapp_router import WhatsAppRouterAgent

logger = logging.getLogger(__name__)

class Orchestrator:
    def __init__(self, llm):
        """Initialize the orchestrator with all agents and the LLM model."""
        try:
            self.llm = llm
            
            # Initialize agents (pass llm to each agent)
            self.lead_agent = LeadQualifierAgent(llm)
            self.rag_agent = RAGAgent(llm)
            self.faq_agent = FAQAgent(llm)
            self.whatsapp_agent = WhatsAppRouterAgent()
            
            logger.info("Orchestrator initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize orchestrator: {e}")
            raise

    def route_query(self, query: str):
        """Route the query to the appropriate agent based on intent detection."""
        try:
            intent = self._detect_intent(query)
            logger.info(f"Detected intent: {intent} for query: {query[:50]}...")
            
            if intent == "lead":
                return self.lead_agent.run(query)
            elif intent == "faq":
                return self.faq_agent.run(query)
            elif intent == "rag":
                return self.rag_agent.run(query)
            elif intent == "contact_human":
                return self.whatsapp_agent.run(query)
            else:
                # Pour les requêtes normales, inclure une option de contact humain
                response = self.rag_agent.run(query)
                # Ajouter l'option de contact humain dans la réponse
                if isinstance(response, str) and ("Je ne suis pas sûr" in response or 
                                                "Je n'ai pas" in response or
                                                "désolé" in response.lower() or 
                                                len(query) > 150):  # Questions complexes
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

    def _detect_intent(self, query: str) -> str:
        """Detect the intent of the user query using simple keyword matching."""
        query_lower = query.lower()
        
        # Contact human keywords
        if any(word in query_lower for word in ["parler à un humain", "agent humain", "personne réelle", 
                                              "conseiller", "représentant", "parler à quelqu'un", 
                                              "whatsapp", "téléphone", "contact direct", "vraie personne", 
                                              "chat humain", "assistant humain"]):
            return "contact_human"
        
        # Lead qualification keywords
        if any(word in query_lower for word in ["lead", "budget", "event", "plan", "organize", "book", "wedding", "party"]):
            return "lead"
        # FAQ keywords  
        elif any(word in query_lower for word in ["faq", "question", "how", "what", "when", "where", "why", "policy", "cancel"]):
            return "faq"
        # RAG keywords
        elif any(word in query_lower for word in ["technical", "product", "service", "supply", "rental", "equipment", "catalog"]):
            return "rag"
        else:
            return "whatsapp"
