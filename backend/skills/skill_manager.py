import os
from pathlib import Path
from typing import Dict, List, Optional
import yaml


class SkillManager:
    """Gerencia as Skills do assistente (instruções especializadas)"""

    def __init__(self, skills_dir: str = "skills"):
        self.skills_dir = Path(skills_dir)
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        self.skills: Dict[str, Dict] = {}
        self.load_skills()

    def load_skills(self):
        """Carrega todas as skills do diretório"""
        if not self.skills_dir.exists():
            return

        for skill_path in self.skills_dir.iterdir():
            if skill_path.is_dir():
                skill_file = skill_path / "SKILL.md"
                if skill_file.exists():
                    self.skills[skill_path.name] = self._parse_skill(skill_file)

    def _parse_skill(self, file_path: Path) -> Dict:
        """Lê o arquivo SKILL.md e extrai metadados e conteúdo"""
        content = file_path.read_text(encoding='utf-8')
        
        # Simples parsing de metadados se houver (opcional)
        return {
            "name": file_path.parent.name,
            "instructions": content,
            "path": str(file_path.absolute())
        }

    def get_skill_prompts(self) -> str:
        """Retorna todas as instruções de skills formatadas para o prompt"""
        if not self.skills:
            return ""

        prompt = "\n\n### 🎓 Skills Disponíveis\n"
        for name, data in self.skills.items():
            prompt += f"\n#### Skill: {name}\n{data['instructions']}\n"
        
        return prompt

    def list_skills(self) -> List[str]:
        """Lista nomes das skills carregadas"""
        return list(self.skills.keys())
