#!/bin/bash
# instalar.sh - Instalador automatico para Linux/Mac
# Quant Invest Algo

set -e

echo "============================================================"
echo "  Quant Invest Algo - Instalacao Automatica (Linux/Mac)"
echo "============================================================"
echo

# ------------------------------------------------------------
# 1. Verifica Python
# ------------------------------------------------------------
echo "[1/5] Verificando Python..."

if command -v python3 &>/dev/null; then
    PYTHON=python3
elif command -v python &>/dev/null; then
    PYTHON=python
else
    echo
    echo " ERRO: Python nao encontrado!"
    echo " Instale com:"
    echo "   Ubuntu/Debian: sudo apt-get install python3 python3-pip"
    echo "   Mac:           brew install python3"
    echo
    exit 1
fi

echo " OK - $($PYTHON --version)"
echo

# ------------------------------------------------------------
# 2. Corrige/atualiza pip
# ------------------------------------------------------------
echo "[2/5] Corrigindo/atualizando pip..."

$PYTHON -m ensurepip --upgrade 2>/dev/null || true
$PYTHON -m pip install --upgrade pip --quiet 2>/dev/null || \
    $PYTHON -m pip install --upgrade pip --quiet --user 2>/dev/null || true

echo " OK - pip pronto."
echo

# ------------------------------------------------------------
# 3. Cria .env com a chave FRED
# ------------------------------------------------------------
echo "[3/5] Configurando chave de API..."

if [ ! -f .env ]; then
    cp .env.example .env
    echo " OK - Arquivo .env criado com a chave FRED configurada."
else
    echo " OK - Arquivo .env ja existe, mantendo configuracoes atuais."
fi
echo

# ------------------------------------------------------------
# 4. Instala dependencias
# ------------------------------------------------------------
echo "[4/5] Instalando dependencias (pode demorar alguns minutos)..."
echo "      Nao feche este terminal!"
echo

$PYTHON -m pip install -r requirements.txt --quiet || \
    $PYTHON -m pip install -r requirements.txt --quiet --user

echo " OK - Dependencias instaladas."
echo

# ------------------------------------------------------------
# 5. Gera executavel
# ------------------------------------------------------------
echo "[5/5] Gerando executavel (pode demorar 3-10 minutos)..."
echo

$PYTHON -m pip install pyinstaller --quiet || \
    $PYTHON -m pip install pyinstaller --quiet --user

$PYTHON -m PyInstaller build_exe.spec --noconfirm

# ------------------------------------------------------------
# Concluido
# ------------------------------------------------------------
echo
echo "============================================================"
echo "  PRONTO! Executavel gerado com sucesso!"
echo "============================================================"
echo
echo " Localizacao: dist/QuantInvestAlgo"
echo
echo " Para usar:"
echo "   chmod +x dist/QuantInvestAlgo"
echo "   ./dist/QuantInvestAlgo"
echo
echo " Ou para rodar direto (sem compilar):"
echo "   $PYTHON app.py"
echo
