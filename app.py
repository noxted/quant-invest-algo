#!/usr/bin/env python3
"""
app.py - Quant Invest Algo: Launcher Unificado

Este arquivo e o entry point do executavel .exe gerado pelo PyInstaller.
Ao ser executado (duplo-clique no .exe), ele:
  1. Sobe o backend FastAPI em background (porta 8000)
  2. Aguarda o servidor ficar pronto
  3. Abre o dashboard no navegador padrao
  4. Fica rodando ate o usuario fechar a janela do terminal
"""

import os
import sys
import time
import socket
import threading
import webbrowser
import subprocess
import logging
from pathlib import Path

# ---------------------------------------------------------------------------
# Logging basico - vai para arquivo na pasta do exe
# ---------------------------------------------------------------------------
BASE_DIR = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / 'app.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger('Quant-Invest-App')

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
HOST = '127.0.0.1'
PORT = 8000
URL  = f'http://{HOST}:{PORT}'


def _port_in_use(port: int) -> bool:
    """Verifica se ja tem algo rodando na porta."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((HOST, port)) == 0


def _wait_for_server(timeout: int = 30) -> bool:
    """Aguarda o servidor FastAPI subir. Retorna True se OK."""
    start = time.time()
    while time.time() - start < timeout:
        if _port_in_use(PORT):
            return True
        time.sleep(0.5)
    return False


def _resolve_backend_path() -> Path:
    """
    Resolve o caminho do backend_api.py tanto no modo
    desenvolvimento (rodando com 'python app.py') quanto
    no modo frozen (executavel PyInstaller).
    """
    if getattr(sys, 'frozen', False):
        # PyInstaller extrai os arquivos para sys._MEIPASS
        base = Path(sys._MEIPASS)  # type: ignore[attr-defined]
    else:
        base = BASE_DIR
    return base / 'dashboard' / 'backend_api.py'


# ---------------------------------------------------------------------------
# Thread do backend
# ---------------------------------------------------------------------------
_backend_process: subprocess.Popen | None = None


def _start_backend():
    """Inicia o uvicorn/FastAPI em processo separado."""
    global _backend_process

    backend_path = _resolve_backend_path()

    if not backend_path.exists():
        logger.error(f'backend_api.py nao encontrado em: {backend_path}')
        return

    if _port_in_use(PORT):
        logger.info(f'Porta {PORT} ja em uso - reaproveitando servidor existente.')
        return

    # Determina o interpretador Python a usar
    python_exec = sys.executable if not getattr(sys, 'frozen', False) else 'python'

    logger.info(f'Iniciando backend: {backend_path}')

    # Muda o diretorio de trabalho para a raiz do projeto
    # para que os imports do orchestrator funcionem
    project_root = str(backend_path.parent.parent)

    _backend_process = subprocess.Popen(
        [python_exec, str(backend_path)],
        cwd=project_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding='utf-8',
        errors='replace',
    )

    # Faz o log do output do backend em tempo real
    def _log_output():
        for line in _backend_process.stdout:
            logger.info(f'[backend] {line.rstrip()}')

    threading.Thread(target=_log_output, daemon=True).start()


def _stop_backend():
    """Termina o processo do backend ao sair."""
    global _backend_process
    if _backend_process and _backend_process.poll() is None:
        logger.info('Encerrando backend...')
        _backend_process.terminate()
        try:
            _backend_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            _backend_process.kill()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    logger.info('=' * 60)
    logger.info('  Quant Invest Algo - Iniciando...')
    logger.info('=' * 60)

    # 1. Sobe o backend em background
    backend_thread = threading.Thread(target=_start_backend, daemon=True)
    backend_thread.start()
    backend_thread.join()  # aguarda o Popen iniciar (nao o servidor)

    # 2. Aguarda o servidor ficar pronto (max 30s)
    logger.info(f'Aguardando servidor em {URL} ...')
    if not _wait_for_server(timeout=30):
        logger.error('Servidor nao respondeu em 30s. Verifique logs/app.log.')
        input('Pressione ENTER para sair...')
        sys.exit(1)

    logger.info(f'Servidor pronto! Abrindo dashboard em {URL}')

    # 3. Abre o browser
    webbrowser.open(URL)

    # 4. Mantém vivo ate Ctrl+C ou fechar o terminal
    logger.info('App rodando. Pressione Ctrl+C para encerrar.')
    try:
        while True:
            time.sleep(1)
            # Se o backend morreu inesperadamente, avisa
            if _backend_process and _backend_process.poll() is not None:
                logger.error('Backend encerrou inesperadamente!')
                input('Pressione ENTER para sair...')
                sys.exit(1)
    except KeyboardInterrupt:
        logger.info('Encerrando por solicitacao do usuario...')
    finally:
        _stop_backend()
        logger.info('App encerrado.')


if __name__ == '__main__':
    main()
