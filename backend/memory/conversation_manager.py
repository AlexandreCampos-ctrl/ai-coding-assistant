"""
Gerenciador de conversas e memória
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Optional
import json
import uuid
from datetime import datetime


class ConversationManager:
    """Gerencia histórico de conversas com SQLite"""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            data_dir = Path(__file__).parent.parent.parent / "data"
            data_dir.mkdir(exist_ok=True)
            db_path = str(data_dir / "conversations.db")
        
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Inicializa o banco de dados"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT,
                    role TEXT,
                    content TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
                )
            """)
            
            conn.commit()
    
    def create_conversation(self, title: str = "Nova Conversa") -> str:
        """Cria uma nova conversa"""
        conversation_id = str(uuid.uuid4())
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO conversations (id, title) VALUES (?, ?)",
                (conversation_id, title)
            )
            conn.commit()
        
        return conversation_id
    
    def add_message(self, conversation_id: str, role: str, content: str):
        """Adiciona uma mensagem à conversa"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
                (conversation_id, role, content)
            )
            
            # Atualizar timestamp da conversa
            conn.execute(
                "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (conversation_id,)
            )
            
            conn.commit()
    
    def get_messages(self, conversation_id: str, limit: Optional[int] = None) -> List[Dict]:
        """Obtém mensagens de uma conversa"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            query = """
                SELECT role, content, timestamp 
                FROM messages 
                WHERE conversation_id = ? 
                ORDER BY timestamp ASC
            """
            
            if limit:
                query += f" LIMIT {limit}"
            
            cursor = conn.execute(query, (conversation_id,))
            messages = [
                {
                    "role": row['role'],
                    "content": row['content'],
                    "timestamp": row['timestamp']
                }
                for row in cursor.fetchall()
            ]
            
            return messages
    
    def list_conversations(self) -> List[Dict]:
        """Lista todas as conversas"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            cursor = conn.execute("""
                SELECT id, title, created_at, updated_at 
                FROM conversations 
                ORDER BY updated_at DESC
            """)
            
            conversations = [
                {
                    "id": row['id'],
                    "title": row['title'],
                    "created_at": row['created_at'],
                    "updated_at": row['updated_at']
                }
                for row in cursor.fetchall()
            ]
            
            return conversations
    
    def delete_conversation(self, conversation_id: str):
        """Deleta uma conversa e todas as suas mensagens"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
            conn.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
            conn.commit()
    
    def update_conversation_title(self, conversation_id: str, title: str):
        """Atualiza o título de uma conversa"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE conversations SET title = ? WHERE id = ?",
                (title, conversation_id)
            )
            conn.commit()
    
    def get_context_window(self, conversation_id: str, max_tokens: int = 8000) -> List[Dict]:
        """
        Obtém mensagens dentro da janela de contexto
        Aproximação simples: ~4 caracteres por token
        """
        messages = self.get_messages(conversation_id)
        
        # Começar do final e adicionar mensagens até atingir o limite
        context_messages = []
        current_tokens = 0
        
        for message in reversed(messages):
            message_tokens = len(message['content']) // 4
            
            if current_tokens + message_tokens > max_tokens:
                break
            
            context_messages.insert(0, message)
            current_tokens += message_tokens
        
        return context_messages
