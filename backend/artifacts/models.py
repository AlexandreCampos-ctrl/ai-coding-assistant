"""
Modelos de dados para artifacts
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal


class ArtifactCreate(BaseModel):
    """Modelo para criar artifact"""
    name: str = Field(..., description="Nome do artifact (ex: task.md)")
    content: str = Field(..., description="Conteúdo do artifact")
    artifact_type: Literal["task", "implementation_plan", "walkthrough", "other"] = "other"
    summary: str = Field("", description="Resumo do artifact")


class ArtifactUpdate(BaseModel):
    """Modelo para atualizar artifact"""
    content: str = Field(..., description="Novo conteúdo")
    summary: Optional[str] = Field(None, description="Novo resumo")


class ArtifactResponse(BaseModel):
    """Modelo de resposta de artifact"""
    name: str
    path: str
    type: str
    summary: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    size: int = 0
    content: Optional[str] = None
