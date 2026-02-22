@echo off
chcp 65001 >nul
title Quant Invest Algo - Instalador

echo ============================================================
echo   Quant Invest Algo - Instalacao Automatica
echo ============================================================
echo.

:: ------------------------------------------------------------
:: 1. Verifica se Python esta instalado
:: ------------------------------------------------------------
echo [1/5] Verificando Python...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    python3 --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo.
        echo  ERRO: Python nao encontrado!
        echo.
        echo  Instale o Python em: https://python.org/downloads
        echo  IMPORTANTE: Marque a opcao "Add Python to PATH" durante a instalacao!
        echo.
        pause
        exit /b 1
    )
    set PYTHON=python3
) else (
    set PYTHON=python
)

echo  OK - Python encontrado: 
for /f "tokens=*" %%i in ('%PYTHON% --version') do echo     %%i
echo.

:: ------------------------------------------------------------
:: 2. Corrige o pip (resolve o problema "pip nao funciona")
:: ------------------------------------------------------------
echo [2/5] Corrigindo/atualizando pip...

%PYTHON% -m ensurepip --upgrade >nul 2>&1
%PYTHON% -m pip install --upgrade pip --quiet

if %errorlevel% neq 0 (
    echo  AVISO: Nao foi possivel atualizar o pip. Tentando continuar...
) else (
    echo  OK - pip atualizado.
)
echo.

:: ------------------------------------------------------------
:: 3. Cria o arquivo .env com a chave FRED
:: ------------------------------------------------------------
echo [3/5] Configurando chave de API...

if not exist .env (
    copy .env.example .env >nul
    echo  OK - Arquivo .env criado com a chave FRED configurada.
) else (
    echo  OK - Arquivo .env ja existe, mantendo configuracoes atuais.
)
echo.

:: ------------------------------------------------------------
:: 4. Instala as dependencias
:: ------------------------------------------------------------
echo [4/5] Instalando dependencias (pode demorar alguns minutos)...
echo       Nao feche esta janela!
echo.

%PYTHON% -m pip install -r requirements.txt --quiet

if %errorlevel% neq 0 (
    echo.
    echo  ERRO na instalacao das dependencias!
    echo  Tente rodar como Administrador (clique direito no .bat -> Executar como administrador)
    echo.
    pause
    exit /b 1
)

echo  OK - Todas as dependencias instaladas.
echo.

:: ------------------------------------------------------------
:: 5. Gera o executavel .exe
:: ------------------------------------------------------------
echo [5/5] Gerando executavel .exe (pode demorar 3-10 minutos)...
echo       Aguarde, nao feche esta janela!
echo.

%PYTHON% -m pip install pyinstaller --quiet
%PYTHON% -m PyInstaller build_exe.spec --noconfirm

if %errorlevel% neq 0 (
    echo.
    echo  ERRO ao gerar o executavel!
    echo  Verifique se o arquivo build_exe.spec esta na pasta correta.
    echo.
    pause
    exit /b 1
)

:: ------------------------------------------------------------
:: Concluido
:: ------------------------------------------------------------
echo.
echo ============================================================
echo   PRONTO! Executavel gerado com sucesso!
echo ============================================================
echo.
echo  Localizacao: dist\QuantInvestAlgo.exe
echo.
echo  Para usar:
echo    1. Va ate a pasta dist\
echo    2. Copie o QuantInvestAlgo.exe para onde quiser
echo    3. Coloque o arquivo .env na mesma pasta
echo    4. Duplo-clique no QuantInvestAlgo.exe
echo.
echo  Ou para rodar direto (sem .exe):
echo    python app.py
echo.
pause
