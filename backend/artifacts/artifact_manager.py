"""
Gerenciador de Artifacts (task.md, implementation_plan.md, walkthrough.md)
"""
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import json


class ArtifactManager:
    """Gerencia artifacts do assistente (task.md, walkthrough.md, etc)"""
    
    VALID_TYPES = ["task", "implementation_plan", "walkthrough", "other"]
    
    def __init__(self, conversation_id: str):
        """
        Inicializa o gerenciador de artifacts para uma conversação
        
        Args:
            conversation_id: ID único da conversação
        """
        self.conversation_id = conversation_id
        self.brain_dir = Path(f".brain/{conversation_id}")
        self.brain_dir.mkdir(parents=True, exist_ok=True)
        
        # Metadata file
        self.metadata_file = self.brain_dir / "artifacts_metadata.json"
        self._load_metadata()
    
    def _load_metadata(self):
        """Carrega metadata dos artifacts"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {}
    
    def _save_metadata(self):
        """Salva metadata dos artifacts"""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
    
    def create_artifact(
        self, 
        name: str, 
        content: str, 
        artifact_type: str = "other",
        summary: str = ""
    ) -> Dict:
        """
        Cria um novo artifact
        
        Args:
            name: Nome do artifact (ex: "task.md")
            content: Conteúdo do artifact
            artifact_type: Tipo do artifact
            summary: Resumo do artifact
            
        Returns:
            Dict com informações do artifact criado
        """
        if artifact_type not in self.VALID_TYPES:
            raise ValueError(f"Tipo inválido. Use: {self.VALID_TYPES}")
        
        # Sanitize filename
        safe_name = Path(name).name
        artifact_path = self.brain_dir / safe_name
        
        # Write content
        with open(artifact_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Update metadata
        self.metadata[safe_name] = {
            "type": artifact_type,
            "summary": summary,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "size": len(content)
        }
        self._save_metadata()
        
        return {
            "name": safe_name,
            "path": str(artifact_path.absolute()),
            "type": artifact_type,
            "summary": summary,
            "created": True
        }
    
    def update_artifact(
        self, 
        name: str, 
        content: str,
        summary: Optional[str] = None
    ) -> Dict:
        """
        Atualiza um artifact existente
        
        Args:
            name: Nome do artifact
            content: Novo conteúdo
            summary: Novo resumo (opcional)
            
        Returns:
            Dict com informações do artifact atualizado
        """
        safe_name = Path(name).name
        artifact_path = self.brain_dir / safe_name
        
        if not artifact_path.exists():
            raise FileNotFoundError(f"Artifact '{safe_name}' não existe")
        
        # Write content
        with open(artifact_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Update metadata
        if safe_name in self.metadata:
            self.metadata[safe_name]["updated_at"] = datetime.now().isoformat()
            self.metadata[safe_name]["size"] = len(content)
            if summary:
                self.metadata[safe_name]["summary"] = summary
        else:
            # Create metadata if doesn't exist
            self.metadata[safe_name] = {
                "type": "other",
                "summary": summary or "",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "size": len(content)
            }
        
        self._save_metadata()
        
        return {
            "name": safe_name,
            "path": str(artifact_path.absolute()),
            "updated": True
        }
    
    def get_artifact(self, name: str) -> Dict:
        """
        Obtém um artifact por nome
        
        Args:
            name: Nome do artifact
            
        Returns:
            Dict com conteúdo e metadata do artifact
        """
        safe_name = Path(name).name
        artifact_path = self.brain_dir / safe_name
        
        if not artifact_path.exists():
            raise FileNotFoundError(f"Artifact '{safe_name}' não existe")
        
        with open(artifact_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        metadata = self.metadata.get(safe_name, {})
        
        return {
            "name": safe_name,
            "content": content,
            "metadata": metadata,
            "path": str(artifact_path.absolute())
        }
    
    def list_artifacts(self) -> List[Dict]:
        """
        Lista todos os artifacts
        
        Returns:
            Lista de dicts com informações dos artifacts
        """
        artifacts = []
        
        for artifact_file in self.brain_dir.glob("*.md"):
            metadata = self.metadata.get(artifact_file.name, {})
            artifacts.append({
                "name": artifact_file.name,
                "type": metadata.get("type", "other"),
                "summary": metadata.get("summary", ""),
                "created_at": metadata.get("created_at", ""),
                "updated_at": metadata.get("updated_at", ""),
                "size": metadata.get("size", 0),
                "path": str(artifact_file.absolute())
            })
        
        return sorted(artifacts, key=lambda x: x["updated_at"], reverse=True)
    
    def delete_artifact(self, name: str) -> Dict:
        """
        Deleta um artifact
        
        Args:
            name: Nome do artifact
            
        Returns:
            Dict confirmando a deleção
        """
        safe_name = Path(name).name
        artifact_path = self.brain_dir / safe_name
        
        if not artifact_path.exists():
            raise FileNotFoundError(f"Artifact '{safe_name}' não existe")
        
        artifact_path.unlink()
        
        if safe_name in self.metadata:
            del self.metadata[safe_name]
            self._save_metadata()
        
        return {
            "name": safe_name,
            "deleted": True
        }
