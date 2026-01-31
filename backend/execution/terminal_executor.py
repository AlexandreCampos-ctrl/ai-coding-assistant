import asyncio
import subprocess
import shlex
import os
from typing import AsyncGenerator, Dict, List, Optional


class TerminalExecutor:
    """Executa comandos de shell de forma segura e assíncrona"""
    
    # Comandos proibidos por segurança no MVP
    BANNED_COMMANDS = ['rm -rf /', 'format', 'del /s /q', 'rd /s /q']

    def __init__(self, cwd: Optional[str] = None):
        self.cwd = cwd or os.getcwd()

    async def execute(self, command: str) -> AsyncGenerator[Dict, None]:
        """
        Executa um comando e retorna output em tempo real via generator
        """
        # Sanitização básica
        if any(banned in command for banned in self.BANNED_COMMANDS):
            yield {"type": "error", "content": "Comando bloqueado por segurança."}
            return

        try:
            # Iniciar processo
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.cwd
            )

            # Ler stdout e stderr simultaneamente
            async def read_stream(stream, stream_type):
                while True:
                    line = await stream.readline()
                    if line:
                        yield {"type": stream_type, "content": line.decode('utf-8', errors='replace')}
                    else:
                        break

            # Consumir streams
            async for output in self._merge_streams(
                read_stream(process.stdout, "stdout"),
                read_stream(process.stderr, "stderr")
            ):
                yield output

            # Aguardar conclusão
            return_code = await process.wait()
            yield {"type": "exit", "content": f"Processo finalizado com código {return_code}", "code": return_code}

        except Exception as e:
            yield {"type": "error", "content": f"Erro na execução: {str(e)}"}

    async def _merge_streams(self, *iterables):
        """Mescla múltiplos async generators"""
        queue = asyncio.Queue()
        counter = len(iterables)

        async def enqueue(iterable):
            nonlocal counter
            async for item in iterable:
                await queue.put(item)
            counter -= 1

        tasks = [asyncio.create_task(enqueue(it)) for it in iterables]
        
        while counter > 0 or not queue.empty():
            try:
                item = await asyncio.wait_for(queue.get(), timeout=0.1)
                yield item
            except asyncio.TimeoutError:
                continue

        for task in tasks:
            task.cancel()
