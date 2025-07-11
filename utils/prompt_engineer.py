import google.generativeai as genai
import os
import json
import logging
from typing import Dict, List, Any, Optional
from utils.data_loader import DataLoader
from utils.vector_db import VectorDatabase
from utils.session_manager import SessionManager

class PromptEngineer:
    """Handles prompt engineering and AI response generation."""
    
    def __init__(self, config_path: str = "config.json"):
        self.logger = logging.getLogger(__name__)
        self.config = self.load_config(config_path)
        self.setup_gemini()
        
        # Initialize components
        self.data_loader = DataLoader()
        self.vector_db = VectorDatabase()
        self.session_manager = SessionManager()
        
        # Load prompt templates
        self.load_prompt_templates()
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading config: {str(e)}")
            return {}
    
    def setup_gemini(self):
        """Setup Google Gemini AI."""
        try:
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not found in environment variables")
            
            genai.configure(api_key=api_key)
            
            # Initialize model
            model_config = self.config.get('model_config', {})
            self.model = genai.GenerativeModel(
                model_config.get('gemini_model', 'gemini-1.5-flash')
            )
            
            # Configure generation settings
            self.generation_config = genai.types.GenerationConfig(
                temperature=model_config.get('temperature', 0.7),
                max_output_tokens=300,  # Reduced for faster responses
                top_p=model_config.get('top_p', 0.9),
                candidate_count=1
            )
            
            self.logger.info("Gemini AI initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error setting up Gemini: {str(e)}")
            raise
    
    def load_prompt_templates(self):
        """Load prompt templates."""
        self.system_prompt = """Tu es l'assistant IA d'HS Traiteur. 

INSTRUCTIONS:
- Réponds en français, sois professionnel et chaleureux
- Utilise les infos produits/services fournis
- Propose des suggestions basées sur les besoins
- Aide à qualifier les commandes
- Sois concis et direct

HS Traiteur: service traiteur professionnel, cuisine marocaine & internationale.
Services: mariages, soutenances, anniversaires, buffets.
Nous offrons un service complet avec décoration et matériel."""
        
        self.response_templates = self.config.get('response_templates', {})
    
    def get_context_from_query(self, query: str, session_id: str) -> Dict[str, Any]:
        """Get relevant context from vector database and session history."""
        context = {
            'relevant_products': [],
            'relevant_services': [],
            'conversation_history': [],
            'user_context': {}
        }
        
        try:
            # Get relevant products and services from vector database
            context['relevant_products'] = self.vector_db.search_products(query, n_results=3)
            context['relevant_services'] = self.vector_db.search_services(query, n_results=2)
            
            # Get conversation history
            context['conversation_history'] = self.session_manager.get_conversation_history(session_id, limit=5)
            
            # Get user context
            context['user_context'] = self.session_manager.get_user_context(session_id)
            
        except Exception as e:
            self.logger.error(f"Error getting context: {str(e)}")
        
        return context
    
    def build_prompt(self, user_query: str, context: Dict[str, Any]) -> str:
        """Build the complete prompt with context."""
        prompt_parts = [self.system_prompt]
        
        # Add relevant products
        if context['relevant_products']:
            prompt_parts.append("\nPRODUITS PERTINENTS:")
            for product in context['relevant_products']:
                prompt_parts.append(f"- {product['document']}")
        
        # Add relevant services
        if context['relevant_services']:
            prompt_parts.append("\nSERVICES PERTINENTS:")
            for service in context['relevant_services']:
                prompt_parts.append(f"- {service['document']}")
        
        # Add conversation history
        if context['conversation_history']:
            prompt_parts.append("\nHISTORIQUE DE CONVERSATION:")
            for msg in context['conversation_history'][-3:]:  # Last 3 messages
                sender = "Client" if msg['sender'] == 'user' else "Assistant"
                prompt_parts.append(f"{sender}: {msg['content']}")
        
        # Add user context
        if context['user_context']:
            user_prefs = context['user_context'].get('preferences', {})
            if user_prefs:
                prompt_parts.append(f"\nPRÉFÉRENCES CLIENT: {user_prefs}")
        
        # Add current query
        prompt_parts.append(f"\nQUESTION ACTUELLE: {user_query}")
        prompt_parts.append("\nRÉPONSE:")
        
        return "\n".join(prompt_parts)
    
    def generate_response(self, user_query: str, session_id: str) -> str:
        """Generate AI response using Gemini."""
        try:
            # Get context
            context = self.get_context_from_query(user_query, session_id)
            
            # Build prompt
            prompt = self.build_prompt(user_query, context)
            
            # Generate response
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            # Extract response text
            response_text = response.text if response.text else self.response_templates.get('error', 'Désolé, je ne peux pas répondre pour le moment.')
            
            # Save to session
            self.session_manager.add_message(session_id, {
                'type': 'text',
                'content': user_query,
                'sender': 'user'
            })
            
            self.session_manager.add_message(session_id, {
                'type': 'text',
                'content': response_text,
                'sender': 'assistant',
                'metadata': {
                    'context_used': {
                        'products_count': len(context['relevant_products']),
                        'services_count': len(context['relevant_services'])
                    }
                }
            })
            
            return response_text
            
        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            return self.response_templates.get('error', 'Désolé, je rencontre une difficulté technique.')
    
    def suggest_products(self, preferences: Dict[str, Any], session_id: str) -> List[Dict[str, Any]]:
        """Suggest products based on user preferences."""
        try:
            # Build query from preferences
            query_parts = []
            if preferences.get('category'):
                query_parts.append(preferences['category'])
            if preferences.get('price_range'):
                query_parts.append(f"prix {preferences['price_range']}")
            if preferences.get('event_type'):
                query_parts.append(preferences['event_type'])
            
            query = " ".join(query_parts)
            
            # Get suggestions from vector database
            suggestions = self.vector_db.search_products(query, n_results=5)
            
            # Update user context
            self.session_manager.update_user_context(session_id, {'preferences': preferences})
            
            return suggestions
            
        except Exception as e:
            self.logger.error(f"Error suggesting products: {str(e)}")
            return []
    
    def extract_intent(self, user_query: str) -> Dict[str, Any]:
        """Extract intent from user query."""
        intent_prompt = f"""Analyse cette question d'un client de traiteur et extrait l'intention:
        
        Question: "{user_query}"
        
        Réponds uniquement avec un JSON valide contenant:
        {{
            "intent": "information|commande|suggestion|prix|disponibilité|autre",
            "entities": {{
                "produit": "nom du produit si mentionné",
                "service": "type de service si mentionné",
                "evenement": "type d'événement si mentionné",
                "budget": "budget approximatif si mentionné",
                "nombre_personnes": "nombre de personnes si mentionné"
            }},
            "urgence": "faible|moyenne|élevée"
        }}"""
        
        try:
            response = self.model.generate_content(intent_prompt)
            intent_data = json.loads(response.text)
            return intent_data
        except Exception as e:
            self.logger.error(f"Error extracting intent: {str(e)}")
            return {"intent": "autre", "entities": {}, "urgence": "faible"}
    
    def get_greeting_message(self) -> str:
        """Get greeting message."""
        return self.response_templates.get('greeting', 'Bonjour! Comment puis-je vous aider?')
