import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import uuid
import logging

class SessionManager:
    """Manages user sessions and conversation history."""
    
    def __init__(self, sessions_file: str = "data/sessions.json", timeout: int = 1800):
        self.sessions_file = sessions_file
        self.timeout = timeout  # Session timeout in seconds
        self.sessions = {}
        self.logger = logging.getLogger(__name__)
        self.load_sessions()
    
    def load_sessions(self):
        """Load sessions from file."""
        try:
            if os.path.exists(self.sessions_file):
                with open(self.sessions_file, 'r', encoding='utf-8') as f:
                    self.sessions = json.load(f)
                self.logger.info(f"Loaded {len(self.sessions)} sessions")
        except Exception as e:
            self.logger.error(f"Error loading sessions: {str(e)}")
            self.sessions = {}
    
    def save_sessions(self):
        """Save sessions to file."""
        try:
            os.makedirs(os.path.dirname(self.sessions_file), exist_ok=True)
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump(self.sessions, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Error saving sessions: {str(e)}")
    
    def create_session(self, user_id: str = None) -> str:
        """Create a new session."""
        session_id = user_id or str(uuid.uuid4())
        self.sessions[session_id] = {
            'session_id': session_id,
            'created_at': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat(),
            'messages': [],
            'user_context': {
                'preferences': {},
                'current_inquiry': None,
                'order_in_progress': False
            }
        }
        self.save_sessions()
        self.logger.info(f"Created new session: {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID."""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        # Check if session is expired
        last_activity = datetime.fromisoformat(session['last_activity'])
        if datetime.now() - last_activity > timedelta(seconds=self.timeout):
            self.delete_session(session_id)
            return None
        
        return session
    
    def update_session_activity(self, session_id: str):
        """Update session last activity timestamp."""
        if session_id in self.sessions:
            self.sessions[session_id]['last_activity'] = datetime.now().isoformat()
            self.save_sessions()
    
    def add_message(self, session_id: str, message: Dict[str, Any]):
        """Add a message to session history."""
        if session_id not in self.sessions:
            self.create_session(session_id)
        
        self.sessions[session_id]['messages'].append({
            'timestamp': datetime.now().isoformat(),
            'type': message.get('type', 'text'),
            'content': message.get('content', ''),
            'sender': message.get('sender', 'user'),
            'metadata': message.get('metadata', {})
        })
        
        self.update_session_activity(session_id)
        self.save_sessions()
    
    def get_conversation_history(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get conversation history for a session."""
        session = self.get_session(session_id)
        if not session:
            return []
        
        messages = session.get('messages', [])
        return messages[-limit:] if limit > 0 else messages
    
    def update_user_context(self, session_id: str, context_update: Dict[str, Any]):
        """Update user context in session."""
        if session_id not in self.sessions:
            self.create_session(session_id)
        
        self.sessions[session_id]['user_context'].update(context_update)
        self.update_session_activity(session_id)
        self.save_sessions()
    
    def get_user_context(self, session_id: str) -> Dict[str, Any]:
        """Get user context from session."""
        session = self.get_session(session_id)
        if not session:
            return {}
        
        return session.get('user_context', {})
    
    def delete_session(self, session_id: str):
        """Delete a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            self.save_sessions()
            self.logger.info(f"Deleted session: {session_id}")
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions."""
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            last_activity = datetime.fromisoformat(session['last_activity'])
            if current_time - last_activity > timedelta(seconds=self.timeout):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.delete_session(session_id)
        
        if expired_sessions:
            self.logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    
    def get_active_sessions_count(self) -> int:
        """Get count of active sessions."""
        self.cleanup_expired_sessions()
        return len(self.sessions)
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        self.cleanup_expired_sessions()
        
        total_messages = sum(len(session.get('messages', [])) for session in self.sessions.values())
        
        return {
            'active_sessions': len(self.sessions),
            'total_messages': total_messages,
            'avg_messages_per_session': total_messages / len(self.sessions) if self.sessions else 0
        }
