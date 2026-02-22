# build_exe.spec
# Configuracao do PyInstaller para gerar o executavel .exe do Quant Invest Algo
#
# Como usar:
#   pip install pyinstaller
#   pyinstaller build_exe.spec
#
# O executavel sera gerado em: dist/QuantInvestAlgo.exe  (Windows)
#                              dist/QuantInvestAlgo      (Linux/Mac)

import sys
from pathlib import Path

ROOT = Path(SPECPATH)  # diretorio raiz do projeto

# ------------------------------------------------------------
# Arquivos de dados que precisam ser empacotados junto ao .exe
# Formato: (origem, destino_dentro_do_exe)
# ------------------------------------------------------------
datas = [
    # Dashboard: HTML + JS + CSS
    (str(ROOT / 'dashboard' / 'index.html'),       'dashboard'),
    (str(ROOT / 'dashboard' / 'backend_api.py'),   'dashboard'),

    # Modulos Python do projeto (nao sao importados diretamente,
    # mas o backend_api.py precisa deles no sys.path)
    (str(ROOT / 'algorithms'),   'algorithms'),
    (str(ROOT / 'config'),       'config'),
    (str(ROOT / 'data'),         'data'),
    (str(ROOT / 'environment'),  'environment'),
    (str(ROOT / 'risk'),         'risk'),

    # Arquivo de orquestrador na raiz
    (str(ROOT / 'orchestrator.py'), '.'),

    # Exemplo de .env (o usuario vai preencher)
    (str(ROOT / '.env.example'), '.'),
]

# Inclui o arquivo .env se existir
env_file = ROOT / '.env'
if env_file.exists():
    datas.append((str(env_file), '.'))

# ------------------------------------------------------------
# Modulos ocultos que o PyInstaller nao detecta automaticamente
# (imports dinamicos usados pelo FastAPI/uvicorn/starlette)
# ------------------------------------------------------------
hiddenimports = [
    # FastAPI / Uvicorn
    'uvicorn',
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'fastapi',
    'fastapi.middleware.cors',
    'starlette',
    'starlette.middleware',
    'starlette.middleware.cors',
    'anyio',
    'anyio._backends._asyncio',
    # Data
    'pandas',
    'numpy',
    'yfinance',
    'requests',
    'python_dotenv',
    # ML/RL (importados pelo orchestrator)
    'torch',
    'sklearn',
    'scipy',
]

a = Analysis(
    ['app.py'],                # entry point
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',           # pesado, nao usado no dashboard
        'IPython',
        'jupyter',
        'notebook',
        'test',
        'tests',
        '_pytest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='QuantInvestAlgo',     # nome do executavel gerado
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,                   # comprime o executavel (precisa do UPX instalado, opcional)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,               # True = mostra janela de terminal com os logs
                                # Mude para False se quiser rodar silenciosamente
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='dashboard/icon.ico',  # descomente e adicione um icone .ico se quiser
)

# coll nao e necessario no modo --onefile, mas deixado comentado para referencia
# coll = COLLECT(exe, ...)
