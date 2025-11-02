"""Conversation context management for multi-turn dialogue"""

import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from threading import Lock
import json

from ..models.core import Entity, Intent, CartSummary, EntityType, IntentType


@dataclass
class CommandRecord:
    """Record of a single command in conversation history"""
    timestamp: datetime
    original_text: str
    normalized_text: str
    intent: Intent
    entities: List[Entity]
    success: bool
    response: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert command record to dictionary"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "original_text": self.original_text,
            "normalized_text": self.normalized_text,
            "intent": self.intent.to_dict(),
            "entities": [e.to_dict() for e in self.entities],
            "success": self.success,
            "response": self.response
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CommandRecord':
        """Create command record from dictionary"""
        # Reconstruct entities
        entities = []
        for e_data in data.get("entities", []):
            entity = Entity(
                type=EntityType(e_data["type"]),
                value=e_data["value"],
                confidence=e_data["confidence"],
                span=tuple(e_data["span"])
            )
            entities.append(entity)
        
        # Reconstruct intent
        intent_data = data["intent"]
        intent = Intent(
            type=IntentType(intent_data["type"]),
            confidence=intent_data["confidence"],
            entities=entities
        )
        
        return cls(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            original_text=data["original_text"],
            normalized_text=data["normalized_text"],
            intent=intent,
            entities=entities,
            success=data["success"],
            response=data["response"]
        )


@dataclass
class ConversationContext:
    """Enhanced conversation context for multi-turn dialogue"""
    session_id: str
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    command_history: List[CommandRecord] = field(default_factory=list)
    cart_state: Optional[CartSummary] = None
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    disambiguation_context: Dict[str, Any] = field(default_factory=dict)
    
    # Session configuration
    max_history_size: int = 20
    session_timeout_minutes: int = 30
    
    def update_activity(self) -> None:
        """Update last activity timestamp"""
        self.last_activity = datetime.now()
    
    def add_command(self, original_text: str, normalized_text: str, intent: Intent, 
                   entities: List[Entity], success: bool, response: str) -> None:
        """Add command to conversation history"""
        self.update_activity()
        
        command_record = CommandRecord(
            timestamp=datetime.now(),
            original_text=original_text,
            normalized_text=normalized_text,
            intent=intent,
            entities=entities,
            success=success,
            response=response
        )
        
        self.command_history.append(command_record)
        
        # Maintain history size limit
        if len(self.command_history) > self.max_history_size:
            self.command_history = self.command_history[-self.max_history_size:]
    
    def update_cart_state(self, cart_summary: CartSummary) -> None:
        """Update current cart state"""
        self.update_activity()
        self.cart_state = cart_summary
    
    def is_expired(self) -> bool:
        """Check if session has expired based on timeout"""
        timeout_threshold = datetime.now() - timedelta(minutes=self.session_timeout_minutes)
        return self.last_activity < timeout_threshold
    
    def get_recent_commands(self, count: int = 5) -> List[CommandRecord]:
        """Get recent commands from history"""
        return self.command_history[-count:] if self.command_history else []
    
    def get_recent_entities(self, entity_type: Optional[EntityType] = None, 
                          count: int = 10) -> List[Entity]:
        """Get recent entities from command history"""
        entities = []
        for command in reversed(self.command_history):
            for entity in command.entities:
                if entity_type is None or entity.type == entity_type:
                    entities.append(entity)
                    if len(entities) >= count:
                        return entities
        return entities
    
    def get_last_successful_command(self) -> Optional[CommandRecord]:
        """Get the last successful command"""
        for command in reversed(self.command_history):
            if command.success:
                return command
        return None
    
    def get_commands_by_intent(self, intent_type: IntentType, count: int = 5) -> List[CommandRecord]:
        """Get recent commands of specific intent type"""
        matching_commands = []
        for command in reversed(self.command_history):
            if command.intent.type == intent_type:
                matching_commands.append(command)
                if len(matching_commands) >= count:
                    break
        return matching_commands
    
    def has_recent_product_mentions(self, product_name: str, minutes: int = 5) -> bool:
        """Check if product was mentioned recently"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        for command in reversed(self.command_history):
            if command.timestamp < cutoff_time:
                break
            
            # Check in original text
            if product_name.lower() in command.original_text.lower():
                return True
            
            # Check in entities
            for entity in command.entities:
                if (entity.type == EntityType.PRODUCT and 
                    product_name.lower() in entity.value.lower()):
                    return True
        
        return False
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """Get session statistics"""
        if not self.command_history:
            return {
                "total_commands": 0,
                "successful_commands": 0,
                "success_rate": 0.0,
                "session_duration_minutes": 0,
                "most_common_intent": None
            }
        
        total_commands = len(self.command_history)
        successful_commands = sum(1 for cmd in self.command_history if cmd.success)
        success_rate = successful_commands / total_commands if total_commands > 0 else 0.0
        
        # Calculate session duration
        session_duration = (self.last_activity - self.created_at).total_seconds() / 60
        
        # Find most common intent
        intent_counts = {}
        for command in self.command_history:
            intent_type = command.intent.type.value
            intent_counts[intent_type] = intent_counts.get(intent_type, 0) + 1
        
        most_common_intent = max(intent_counts.items(), key=lambda x: x[1])[0] if intent_counts else None
        
        return {
            "total_commands": total_commands,
            "successful_commands": successful_commands,
            "success_rate": success_rate,
            "session_duration_minutes": round(session_duration, 2),
            "most_common_intent": most_common_intent,
            "intent_distribution": intent_counts
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for serialization"""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "command_history": [cmd.to_dict() for cmd in self.command_history],
            "cart_state": self.cart_state.to_dict() if self.cart_state else None,
            "user_preferences": self.user_preferences,
            "disambiguation_context": self.disambiguation_context,
            "max_history_size": self.max_history_size,
            "session_timeout_minutes": self.session_timeout_minutes,
            "is_expired": self.is_expired(),
            "statistics": self.get_session_statistics()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationContext':
        """Create context from dictionary"""
        # Reconstruct command history
        command_history = []
        for cmd_data in data.get("command_history", []):
            command_history.append(CommandRecord.from_dict(cmd_data))
        
        # Reconstruct cart state if present
        cart_state = None
        if data.get("cart_state"):
            # This would need CartSummary.from_dict method
            pass  # For now, leave as None
        
        context = cls(
            session_id=data["session_id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            last_activity=datetime.fromisoformat(data["last_activity"]),
            command_history=command_history,
            cart_state=cart_state,
            user_preferences=data.get("user_preferences", {}),
            disambiguation_context=data.get("disambiguation_context", {}),
            max_history_size=data.get("max_history_size", 20),
            session_timeout_minutes=data.get("session_timeout_minutes", 30)
        )
        
        return context


class ConversationContextManager:
    """Manager for conversation contexts with session tracking and cleanup"""
    
    def __init__(self, cleanup_interval_minutes: int = 60):
        self._contexts: Dict[str, ConversationContext] = {}
        self._lock = Lock()
        self.cleanup_interval_minutes = cleanup_interval_minutes
        self._last_cleanup = datetime.now()
    
    def get_context(self, session_id: str) -> ConversationContext:
        """Get or create conversation context for session"""
        with self._lock:
            self._cleanup_expired_sessions()
            
            if session_id not in self._contexts:
                self._contexts[session_id] = ConversationContext(session_id=session_id)
            
            context = self._contexts[session_id]
            context.update_activity()
            return context
    
    def update_context(self, session_id: str, context: ConversationContext) -> None:
        """Update conversation context"""
        with self._lock:
            self._contexts[session_id] = context
    
    def remove_context(self, session_id: str) -> bool:
        """Remove conversation context"""
        with self._lock:
            if session_id in self._contexts:
                del self._contexts[session_id]
                return True
            return False
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs"""
        with self._lock:
            self._cleanup_expired_sessions()
            return list(self._contexts.keys())
    
    def get_session_count(self) -> int:
        """Get number of active sessions"""
        with self._lock:
            self._cleanup_expired_sessions()
            return len(self._contexts)
    
    def _cleanup_expired_sessions(self) -> None:
        """Clean up expired sessions"""
        now = datetime.now()
        
        # Only run cleanup if enough time has passed
        if (now - self._last_cleanup).total_seconds() < self.cleanup_interval_minutes * 60:
            return
        
        expired_sessions = []
        for session_id, context in self._contexts.items():
            if context.is_expired():
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self._contexts[session_id]
        
        self._last_cleanup = now
    
    def force_cleanup(self) -> int:
        """Force cleanup of expired sessions and return count removed"""
        with self._lock:
            expired_sessions = []
            for session_id, context in self._contexts.items():
                if context.is_expired():
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                del self._contexts[session_id]
            
            self._last_cleanup = datetime.now()
            return len(expired_sessions)
    
    def get_manager_statistics(self) -> Dict[str, Any]:
        """Get manager statistics"""
        with self._lock:
            self._cleanup_expired_sessions()
            
            total_sessions = len(self._contexts)
            total_commands = sum(len(ctx.command_history) for ctx in self._contexts.values())
            
            if self._contexts:
                avg_session_duration = sum(
                    (ctx.last_activity - ctx.created_at).total_seconds() / 60 
                    for ctx in self._contexts.values()
                ) / len(self._contexts)
                
                avg_commands_per_session = total_commands / len(self._contexts)
            else:
                avg_session_duration = 0
                avg_commands_per_session = 0
            
            return {
                "active_sessions": total_sessions,
                "total_commands": total_commands,
                "avg_session_duration_minutes": round(avg_session_duration, 2),
                "avg_commands_per_session": round(avg_commands_per_session, 2),
                "last_cleanup": self._last_cleanup.isoformat()
            }
    
    def export_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Export session data for persistence"""
        with self._lock:
            if session_id in self._contexts:
                return self._contexts[session_id].to_dict()
            return None
    
    def import_session_data(self, session_data: Dict[str, Any]) -> bool:
        """Import session data from persistence"""
        try:
            context = ConversationContext.from_dict(session_data)
            with self._lock:
                self._contexts[context.session_id] = context
            return True
        except Exception:
            return False


# Global context manager instance
_context_manager = ConversationContextManager()


def get_context_manager() -> ConversationContextManager:
    """Get the global conversation context manager"""
    return _context_manager


def get_conversation_context(session_id: str) -> ConversationContext:
    """Get conversation context for a session (convenience function)"""
    return _context_manager.get_context(session_id)


def update_conversation_context(session_id: str, context: ConversationContext) -> None:
    """Update conversation context (convenience function)"""
    _context_manager.update_context(session_id, context)