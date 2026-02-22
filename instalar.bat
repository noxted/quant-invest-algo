@echo off
chcp 65001 >nul
title Quant Invest Algo - Instalador

:: Garante que o script rode a partir da pasta onde o .bat esta
cd /d "%~dp0"

echo ============================================================
echo  Quant Invest Algo - Instalacao Automatica
echo ============================================================
echo.
echo Pasta do projeto: %~dp0
echo.

:: ------------------------------------------------------------
:: Verificar se esta na pasta correta
:: ------------------------------------------------------------
if not exist requirements.txt (
    echo.
    echo ERRO: Arquivo requirements.txt nao encontrado!
    echo.
    echo Certifique-se de que voce clonou o repositorio corretamente:
    echo   git clone https://github.com/noxted/quant-invest-algo.git
    echo   cd quant-invest-algo
    echo.
    echo E depois execute o instalar.bat de dentro da pasta quant-invest-algo
    echo.
    pause
    exit /b 1
)

:: ------------------------------------------------------------
:: 1. Verifica se Python esta instalado
:: ------------------------------------------------------------
echo [1/5] Verificando Python...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    python3 --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo.
        echo ERRO: Python nao encontrado!
        echo.
        echo Instale o Python em: https://python.org/downloads
        echo IMPORTANTE: Marque a opcao "Add Python to PATH" durante a instalacao!
        echo.
        pause
        exit /b 1
    )
    set PYTHON=python3
) else (
    set PYTHON=python
)

echo OK - Python encontrado:
for /f "tokens=*" %%i in ('%PYTHON% --version') do echo     %%i
echo.

:: ------------------------------------------------------------
:: 2. Corrige o pip
:: ------------------------------------------------------------
echo [2/5] Corrigindo/atualizando pip...

%PYTHON% -m ensurepip --upgrade >nul 2>&1
%PYTHON% -m pip install --upgrade pip --quiet

if %errorlevel% neq 0 (
    echo AVISO: Nao foi possivel atualizar o pip. Tentando continuar...
) else (
    echo OK - pip atualizado.
)
echo.

:: ------------------------------------------------------------
:: 3. Cria o arquivo .env
:: ------------------------------------------------------------
echo [3/5] Configurando chave de API...

if not exist .env (
    copy .env.example .env >nul
    echo OK - Arquivo .env criado. Edite-o para adicionar sua FRED_API_KEY.
) else (
    echo OK - Arquivo .env ja existe, mantendo configuracoes atuais.
)
echo.

:: ------------------------------------------------------------
:: 4. Instala as dependencias
:: ------------------------------------------------------------
echo [4/5] Instalando dependencias (pode demorar alguns minutos)...
echo Nao feche esta janela!
echo.

%PYTHON% -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo ERRO na instalacao das dependencias!
    echo Tente rodar como Administrador: clique direito no .bat e escolha "Executar como administrador"
    echo.
    pause
    exit /b 1
)

echo.
echo OK - Todas as dependencias instaladas.
echo.

:: ------------------------------------------------------------
:: 5. Gera o executavel .exe (opcional)
:: ------------------------------------------------------------
echo [5/5] Gerando executavel .exe (pode demorar 3-10 minutos)...
echo Aguarde, nao feche esta janela!
echo.

%PYTHON% -m pip install pyinstaller --quiet
%PYTHON% -m PyInstaller build_exe.spec --noconfirm

if %errorlevel% neq 0 (
    echo.
    echo AVISO: Nao foi possivel gerar o .exe (build_exe.spec nao encontrado ou erro).
    echo O projeto ainda funciona normalmente via: python app.py
    echo.
) else (
    echo OK - Executavel gerado em: dist\QuantInvestAlgo.exe
)

:: ------------------------------------------------------------
:: Concluido
:: ------------------------------------------------------------
echo.
echo ============================================================
echo  INSTALACAO CONCLUIDA!
echo ============================================================
echo.
echo Para iniciar o dashboard:
echo   python app.py
echo.
echo Para rodar o agente autonomo (24h sem intervencao):
echo   python main.py --profile intermediate --auto --aporte 5000
echo.
echo Lembre-se de editar o arquivo .env com sua FRED_API_KEY!
echo.
pause
