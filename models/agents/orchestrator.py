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

    def route_query(self, query: str) -> str:
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
            else:
                return self.whatsapp_agent.run(query)
                
        except Exception as e:
            logger.error(f"Error routing query: {e}")
            return f"I apologize, but I encountered an error processing your request. Please try again or contact support."

    def _detect_intent(self, query: str) -> str:
        """Detect the intent of the user query using simple keyword matching."""
        query_lower = query.lower()
        
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
