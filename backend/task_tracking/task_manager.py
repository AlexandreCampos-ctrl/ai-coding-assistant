"""
Gerenciador de Tasks e progresso
"""
from typing import Dict, List, Optional, Literal
from datetime import datetime
from pydantic import BaseModel


TaskMode = Literal["planning", "execution", "verification"]


class Task(BaseModel):
    """Modelo de Task"""
    name: str
    mode: TaskMode
    status: str
    progress: int  # 0-100
    subtasks: List[str] = []
    started_at: str
    updated_at: str


class TaskManager:
    """Gerencia estado de tasks e progresso"""
    
    def __init__(self):
        self.current_task: Optional[Task] = None
        self.task_history: List[Task] = []
    
    def start_task(
        self, 
        name: str, 
        mode: TaskMode,
        status: str = "",
        subtasks: List[str] = []
    ) -> Dict:
        """
        Inicia uma nova task
        
        Args:
            name: Nome da task
            mode: Modo (planning/execution/verification)
            status: Status inicial
            subtasks: Lista de subtasks

        Returns:
            Dict com informações da task
        """
        now = datetime.now().isoformat()
        
        # Se já existe uma task, adiciona ao histórico
        if self.current_task:
            self.task_history.append(self.current_task)
        
        self.current_task = Task(
            name=name,
            mode=mode,
            status=status or f"Iniciando {name}...",
            progress=0,
            subtasks=subtasks,
            started_at=now,
            updated_at=now
        )
        
        return self.current_task.model_dump()
    
    def update_progress(
        self, 
        progress: Optional[int] = None,
        status: Optional[str] = None,
        mode: Optional[TaskMode] = None
    ) -> Dict:
        """
        Atualiza progresso da task atual
        
        Args:
            progress: Novo progresso (0-100)
            status: Novo status
            mode: Novo modo
            
        Returns:
            Dict com task atualizada
        """
        if not self.current_task:
            raise ValueError("Nenhuma task ativa")
        
        if progress is not None:
            self.current_task.progress = max(0, min(100, progress))
        
        if status is not None:
            self.current_task.status = status
        
        if mode is not None:
            self.current_task.mode = mode
        
        self.current_task.updated_at = datetime.now().isoformat()
        
        return self.current_task.model_dump()
    
    def add_subtask(self, subtask: str) -> Dict:
        """Adiciona uma subtask"""
        if not self.current_task:
            raise ValueError("Nenhuma task ativa")
        
        self.current_task.subtasks.append(subtask)
        self.current_task.updated_at = datetime.now().isoformat()
        
        return self.current_task.model_dump()
    
    def complete_task(self) -> Dict:
        """
        Completa a task atual
        
        Returns:
            Dict com task completada
        """
        if not self.current_task:
            raise ValueError("Nenhuma task ativa")
        
        self.current_task.progress = 100
        self.current_task.status = "Concluído"
        self.current_task.updated_at = datetime.now().isoformat()
        
        # Adiciona ao histórico
        completed_task = self.current_task.model_dump()
        self.task_history.append(self.current_task)
        self.current_task = None
        
        return completed_task
    
    def get_current(self) -> Optional[Dict]:
        """Retorna task atual"""
        return self.current_task.model_dump() if self.current_task else None
    
    def get_history(self, limit: int = 10) -> List[Dict]:
        """
        Retorna histórico de tasks
        
        Args:
            limit: Número máximo de tasks
            
        Returns:
            Lista de tasks completadas
        """
        return [t.model_dump() for t in self.task_history[-limit:]]


# Instância global do TaskManager
task_manager = TaskManager()
