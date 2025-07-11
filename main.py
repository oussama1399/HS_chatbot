from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import os
import json
import logging
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Import only essential utility classes
from utils.data_loader import DataLoader
from utils.session_manager import SessionManager

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')

# Initialize extensions
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables for components
data_loader = None
session_manager = None

def initialize_components():
    """Initialize essential components only."""
    global data_loader, session_manager
    
    try:
        logger.info("Initializing components...")
        
        # Initialize data loader
        data_loader = DataLoader()
        products_df = data_loader.load_products()
        services_df = data_loader.load_services()
        
        # Initialize session manager
        session_manager = SessionManager()
        
        logger.info(f"✅ Loaded {len(products_df)} products and {len(services_df)} services")
        
    except Exception as e:
        logger.error(f"❌ Error initializing components: {str(e)}")
        raise

# Initialize components before serving routes
initialize_components()

# Routes
@app.route('/')
def index():
    """Main chat interface."""
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'components': {
            'data_loader': data_loader is not None,
            'session_manager': session_manager is not None
        }
    })

@app.route('/api/products')
def get_products():
    """Get all products."""
    if data_loader:
        try:
            products = data_loader.load_products()
            # Convert DataFrame to a simple list of dictionaries with proper null handling
            products_list = products.replace({pd.NA: None}).to_dict('records')
            return jsonify(products_list)
        except Exception as e:
            logger.error(f"Error serving products API: {str(e)}")
            return jsonify({"error": str(e)}), 500
    return jsonify([])

@app.route('/api/services')
def get_services():
    """Get all services."""
    if data_loader:
        services = data_loader.load_services()
        return jsonify(services.to_dict('records'))
    return jsonify([])

@app.route('/api/stats')
def get_stats():
    """Get application statistics."""
    if data_loader:
        products_df = data_loader.load_products()
        services_df = data_loader.load_services()
        
        return jsonify({
            'products': {
                'total_products': len(products_df),
                'available_products': len(products_df[products_df['is_available'] == True]) if 'is_available' in products_df.columns else len(products_df)
            },
            'services': {
                'total_services': len(services_df)
            },
            'sessions': session_manager.get_session_stats() if session_manager else {'total': 0}
        })
    return jsonify({'error': 'Data not loaded'})

# WebSocket events
@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    logger.info("✅ Client connected")
    emit('message', {
        'type': 'text',
        'content': 'Bonjour! Je suis votre assistant HS Traiteur. Comment puis-je vous aider aujourd\'hui?',
        'sender': 'assistant',
        'timestamp': datetime.now().isoformat()
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    logger.info("❌ Client disconnected")

@socketio.on('message')
def handle_message(data):
    """Handle incoming messages."""
    
    
    try:
        user_message = data.get('content', '')
        if not user_message:
            return
        
        # Import AI components
        import google.generativeai as genai
        from models.agents.orchestrator import Orchestrator
        
        # Configure Gemini (only for API key verification)
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        
        # Utiliser l'orchestrateur directement (sans passer de LLM)
        orchestrator = Orchestrator()
        result = orchestrator.route_query(user_message)
        
        # Vérifier si la réponse suggère un contact humain
        if isinstance(result, dict) and result.get('offer_human_contact'):
            ai_response = result['message']
            
            # Envoyer d'abord la réponse de l'IA
            emit('message', {
                'type': 'text',
                'content': ai_response,
                'sender': 'assistant',
                'timestamp': datetime.now().isoformat()
            })
            
            # Puis proposer le contact humain
            emit('message', {
                'type': 'human_contact_offer',
                'content': "Souhaitez-vous être mis en relation avec un conseiller pour une assistance plus personnalisée?",
                'whatsapp_link': result.get('whatsapp_link', ''),
                'phone_number': result.get('phone_number', ''),
                'sender': 'assistant',
                'timestamp': datetime.now().isoformat()
            })
            return
        elif isinstance(result, dict) and result.get('type') == 'whatsapp_redirect':
            # Redirection directe vers WhatsApp
            emit('message', {
                'type': 'human_contact',
                'content': result.get('message', "Je vous mets en relation avec un conseiller..."),
                'whatsapp_link': result.get('whatsapp_link', ''),
                'phone_number': result.get('phone_number', ''),
                'sender': 'assistant',
                'timestamp': datetime.now().isoformat()
            })
            return
        else:
            # Réponse normale
            ai_response = result if isinstance(result, str) else str(result)
        
        # Send AI response
        emit('message', {
            'type': 'text',
            'content': ai_response,
            'sender': 'assistant',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Error generating AI response: {str(e)}")
        # Fallback response
        emit('message', {
            'type': 'text',
            'content': "Désolé, je rencontre une difficulté technique. Pouvez-vous reformuler votre question?",
            'sender': 'assistant',
            'timestamp': datetime.now().isoformat()
        })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {str(error)}")
    return render_template('500.html'), 500

if __name__ == '__main__':
    try:
        # Initialize components
        initialize_components()
        
        # Run the application
        port = int(os.getenv('PORT', 5000))
        debug = os.getenv('ENVIRONMENT', 'development') == 'development'
        
        logger.info(f"🚀 Starting HS Chatbot on port {port}")
        logger.info(f"🌐 Access the app at: http://localhost:{port}")
        socketio.run(app, host='0.0.0.0', port=port, debug=debug)
        
    except Exception as e:
        logger.error(f"❌ Failed to start application: {str(e)}")
        raise
