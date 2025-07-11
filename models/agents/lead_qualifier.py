from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
import logging

logger = logging.getLogger(__name__)

class LeadQualifierAgent:
    def __init__(self, llm):
        """Initialize the lead qualifier agent with the provided LLM."""
        self.llm = llm
        self.collected_info = {}
        
        # Define tools to collect user info
        tools = [
            Tool(
                name="collect_budget",
                func=self._collect_budget,
                description="Collect budget information from the user"
            ),
            Tool(
                name="collect_event_type",
                func=self._collect_event_type,
                description="Collect event type information from the user"
            ),
            Tool(
                name="collect_contact_info",
                func=self._collect_contact_info,
                description="Collect contact information from the user"
            )
        ]
        
        # Initialize agent with the LLM
        self.agent = initialize_agent(
            tools,
            self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True
        )

    def _collect_budget(self, context: str) -> str:
        """Extract budget information from the context or ask for it."""
        # In a real implementation, this would be more sophisticated
        return "Budget information collected. Please provide your budget range for the event."
    
    def _collect_event_type(self, context: str) -> str:
        """Extract event type information from the context or ask for it."""
        return "Event type information collected. Please specify what type of event you're planning."
    
    def _collect_contact_info(self, context: str) -> str:
        """Extract contact information from the context or ask for it."""
        return "Contact information collected. Please provide your contact details for follow-up."

    def run(self, query: str) -> str:
        """Process the lead qualification query."""
        try:
            # Create a structured prompt for lead qualification
            lead_prompt = f"""
            You are a lead qualification assistant. Your goal is to gather important information 
            about the customer's event planning needs. Based on the following query, determine 
            what information you need to collect and provide a helpful response.
            
            Customer Query: {query}
            
            Focus on collecting:
            1. Budget range
            2. Event type and size
            3. Date and location preferences
            4. Contact information
            
            Provide a friendly response that moves the conversation forward:
            """
            
            return self.agent.run(lead_prompt)
        except Exception as e:
            logger.error(f"Error in lead qualification: {e}")
            return "I'd be happy to help you plan your event! Could you tell me more about what type of event you're planning and your budget range?"
