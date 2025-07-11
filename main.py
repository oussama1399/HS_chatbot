from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

# Import utility classes
from utils.data_loader import DataLoader
from utils.session_manager import SessionManager
from utils.vector_db import VectorDatabase
from utils.prompt_engineer import PromptEngineer

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
vector_db = None
prompt_engineer = None

def initialize_components():
    """Initialize all components."""
    global data_loader, session_manager, vector_db, prompt_engineer
    
    try:
        logger.info("Initializing components...")
        
        # Initialize data loader
        data_loader = DataLoader()
        products_df = data_loader.load_products()
        services_df = data_loader.load_services()
        
        # Initialize session manager
        session_manager = SessionManager()
        
        # Initialize vector database
        vector_db = VectorDatabase()
        vector_db.initialize_database(products_df, services_df)
        
        # Initialize prompt engineer
        prompt_engineer = PromptEngineer()
        
        logger.info("All components initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing components: {str(e)}")
        raise

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
            'session_manager': session_manager is not None,
            'vector_db': vector_db is not None,
            'prompt_engineer': prompt_engineer is not None
        }
    })

@app.route('/api/stats')
def get_stats():
    """Get application statistics."""
    try:
        stats = {
            'products': data_loader.get_product_statistics(),
            'sessions': session_manager.get_session_stats(),
            'vector_db': vector_db.get_collection_stats()
        }
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({'error': 'Unable to get statistics'}), 500

@app.route('/api/products')
def get_products():
    """Get available products."""
    try:
        products = data_loader.get_available_products()
        return jsonify(products)
    except Exception as e:
        logger.error(f"Error getting products: {str(e)}")
        return jsonify({'error': 'Unable to get products'}), 500

@app.route('/api/services')
def get_services():
    """Get available services."""
    try:
        services = data_loader.get_all_services()
        return jsonify(services)
    except Exception as e:
        logger.error(f"Error getting services: {str(e)}")
        return jsonify({'error': 'Unable to get services'}), 500

@app.route('/api/search')
def search():
    """Search products and services."""
    try:
        query = request.args.get('q', '')
        search_type = request.args.get('type', 'all')  # all, products, services
        
        if not query:
            return jsonify({'error': 'Query parameter is required'}), 400
        
        results = {}
        
        if search_type in ['all', 'products']:
            results['products'] = vector_db.search_products(query, n_results=5)
        
        if search_type in ['all', 'services']:
            results['services'] = vector_db.search_services(query, n_results=3)
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Error in search: {str(e)}")
        return jsonify({'error': 'Search failed'}), 500

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    try:
        # Create or get session
        session_id = request.sid
        session_manager.create_session(session_id)
        
        # Join room
        join_room(session_id)
        
        # Send greeting
        greeting = prompt_engineer.get_greeting_message()
        emit('message', {
            'type': 'text',
            'content': greeting,
            'sender': 'assistant',
            'timestamp': datetime.now().isoformat()
        })
        
        logger.info(f"Client connected: {session_id}")
        
    except Exception as e:
        logger.error(f"Error handling connect: {str(e)}")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    try:
        session_id = request.sid
        leave_room(session_id)
        logger.info(f"Client disconnected: {session_id}")
        
    except Exception as e:
        logger.error(f"Error handling disconnect: {str(e)}")

@socketio.on('message')
def handle_message(data):
    """Handle incoming messages."""
    try:
        session_id = request.sid
        user_message = data.get('content', '')
        
        if not user_message:
            emit('error', {'message': 'Message content is required'})
            return
        
        # Generate response
        response = prompt_engineer.generate_response(user_message, session_id)
        
        # Send response
        emit('message', {
            'type': 'text',
            'content': response,
            'sender': 'assistant',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error handling message: {str(e)}")
        emit('error', {'message': 'Unable to process message'})

@socketio.on('get_suggestions')
def handle_get_suggestions(data):
    """Handle product suggestions request."""
    try:
        session_id = request.sid
        preferences = data.get('preferences', {})
        
        suggestions = prompt_engineer.suggest_products(preferences, session_id)
        
        emit('suggestions', {
            'products': suggestions,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting suggestions: {str(e)}")
        emit('error', {'message': 'Unable to get suggestions'})

@socketio.on('typing')
def handle_typing(data):
    """Handle typing indicator."""
    try:
        session_id = request.sid
        is_typing = data.get('typing', False)
        
        # Broadcast typing status to the room (if needed for multi-user)
        emit('typing_status', {
            'session_id': session_id,
            'typing': is_typing
        }, room=session_id, include_self=False)
        
    except Exception as e:
        logger.error(f"Error handling typing: {str(e)}")

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
        
        logger.info(f"Starting HS Chatbot on port {port}")
        socketio.run(app, host='0.0.0.0', port=port, debug=debug)
        
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        raise
