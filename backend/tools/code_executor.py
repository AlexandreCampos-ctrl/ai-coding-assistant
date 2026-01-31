"""
Executor de código Python em sandbox
"""

from RestrictedPython import compile_restricted, safe_globals
from RestrictedPython.Guards import guarded_iter_unpack_sequence, safer_getattr
import sys
from io import StringIO
import signal
from contextlib import contextmanager


# Timeout handler
class TimeoutError(Exception):
    pass


def timeout_handler(signum, frame):
    raise TimeoutError("Código excedeu o tempo limite de execução")


@contextmanager
def time_limit(seconds):
    """Context manager para timeout"""
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)


def execute_python(code: str, timeout: int = 30) -> str:
    """
    Executa código Python em um ambiente restrito
    
    Args:
        code: Código Python a executar
        timeout: Timeout em segundos (padrão: 30)
    
    Returns:
        Output do código ou mensagem de erro
    """
    try:
        # Compilar código com restrições
        byte_code = compile_restricted(
            code,
            filename='<inline>',
            mode='exec'
        )
        
        # Verificar erros de compilação
        if byte_code.errors:
            return f"Erro de compilação:\n" + "\n".join(byte_code.errors)
        
        # Preparar ambiente seguro
        safe_locals = {}
        safe_environment = {
            '__builtins__': safe_globals,
            '_iter_unpack_sequence_': guarded_iter_unpack_sequence,
            '_getattr_': safer_getattr,
            # Bibliotecas permitidas
            'math': __import__('math'),
            'random': __import__('random'),
            'datetime': __import__('datetime'),
        }
        
        # Capturar stdout
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        
        try:
            # Executar com timeout (apenas em Unix/Linux)
            try:
                with time_limit(timeout):
                    exec(byte_code.code, safe_environment, safe_locals)
            except:
                # Fallback sem timeout (Windows)
                exec(byte_code.code, safe_environment, safe_locals)
            
            output = mystdout.getvalue()
            return output if output else "Código executado com sucesso (sem output)"
        
        except TimeoutError as e:
            return f"⏱️ Timeout: {str(e)}"
        
        except Exception as e:
            return f"Erro de execução: {type(e).__name__}: {str(e)}"
        
        finally:
            sys.stdout = old_stdout
    
    except Exception as e:
        return f"Erro ao executar código: {str(e)}"


def execute_python_safe(code: str) -> str:
    """
    Versão mais simples sem RestrictedPython (para testes)
    ATENÇÃO: Não usar em produção sem sandbox adequado!
    """
    try:
        # Capturar stdout
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        
        try:
            exec(code)
            output = mystdout.getvalue()
            return output if output else "Código executado com sucesso"
        
        except Exception as e:
            return f"Erro: {type(e).__name__}: {str(e)}"
        
        finally:
            sys.stdout = old_stdout
    
    except Exception as e:
        return f"Erro ao executar: {str(e)}"
