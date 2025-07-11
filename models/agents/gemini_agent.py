import logging
import google.generativeai as genai
import os

logger = logging.getLogger(__name__)

class GeminiAgent:
    """Agent qui utilise directement l'API Gemini sans RAG."""
    
    def __init__(self):
        """Initialiser l'agent Gemini."""
        try:
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                raise ValueError("GOOGLE_API_KEY n'est pas défini dans les variables d'environnement")
            
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model_name="gemini-1.5-flash")
            
            # Charger le prompt système
            system_prompt_path = os.path.join('data', 'prompt_templates', 'system_prompt.txt')
            try:
                with open(system_prompt_path, 'r', encoding='utf-8') as f:
                    self.system_prompt = f.read().strip()
            except FileNotFoundError:
                self.system_prompt = """Tu es un assistant pour HS Traiteur & Belmokhtar Traiteur, spécialisé 
                dans les services de traiteur pour mariages, événements d'entreprise et particuliers. 
                Fournis des informations précises et utiles sur nos services.
                
                IMPORTANT: Affiche TOUJOURS les prix en dirhams (MAD). Par exemple, si un produit coûte 1500, 
                tu dois écrire "1500 dirhams" ou "1500 MAD". N'utilise JAMAIS une autre devise."""
            
            logger.info("GeminiAgent initialisé avec succès")
        except Exception as e:
            logger.error(f"Échec de l'initialisation de GeminiAgent: {e}")
            raise
    
    def run(self, query: str):
        """Obtenir une réponse directement de Gemini."""
        try:
            chat = self.model.start_chat(history=[])
            response = chat.send_message(
                f"[Instructions système]: {self.system_prompt}\n\n[Question client]: {query}"
            )
            return response.text
        except Exception as e:
            logger.error(f"Erreur lors de la génération de réponse avec Gemini: {e}")
            return "Désolé, je n'ai pas pu traiter votre demande. Veuillez réessayer ou contacter un conseiller."
