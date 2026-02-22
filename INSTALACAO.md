# 🚀 Guia de Instalação - Quant Invest Dashboard

## 📋 Pré-requisitos

Antes de começar, você precisa ter instalado no seu computador:

### 1. **Python 3.8 ou superior**
- **Windows**: Baixe em [python.org/downloads](https://www.python.org/downloads/)
  - ⚠️ **IMPORTANTE**: Durante a instalação, marque a opção "Add Python to PATH"
- **Mac**: `brew install python3`
- **Linux**: `sudo apt-get install python3 python3-pip`

Para verificar se está instalado:
```bash
python --version
```

### 2. **Git**
- **Windows**: Baixe em [git-scm.com](https://git-scm.com/download/win)
- **Mac**: `brew install git`
- **Linux**: `sudo apt-get install git`

### 3. **Chaves de API** (gratuitas)

#### FRED API (dados econômicos dos EUA)
1. Acesse: https://fred.stlouisfed.org/
2. Clique em "My Account" → "API Keys"
3. Crie uma conta gratuita
4. Gere sua API Key
5. Copie a chave (formato: `abc123def456...`)

#### BCB API (Banco Central do Brasil)
✅ **Não precisa de chave** - API pública e aberta

---

## 📥 Passo 1: Baixar o Projeto

Abra o Terminal (Mac/Linux) ou Prompt de Comando (Windows) e execute:

```bash
# Clone o repositório
git clone https://github.com/noxted/quant-invest-algo.git

# Entre na pasta do projeto
cd quant-invest-algo
```

---

## ⚙️ Passo 2: Instalar Dependências

### Opção A: Instalação Simples (Recomendado)

```bash
# Instale todas as bibliotecas necessárias
pip install -r requirements.txt
```

### Opção B: Usando Ambiente Virtual (Avançado)

```bash
# Crie um ambiente virtual
python -m venv venv

# Ative o ambiente virtual
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt
```

---

## 🔑 Passo 3: Configurar Chaves de API

### Método 1: Arquivo .env (Recomendado)

1. Crie um arquivo chamado `.env` na pasta raiz do projeto
2. Adicione suas chaves:

```env
FRED_API_KEY=sua_chave_fred_aqui
```

### Método 2: Variáveis de Ambiente do Sistema

#### Windows (PowerShell):
```powershell
$env:FRED_API_KEY="sua_chave_aqui"
```

#### Mac/Linux:
```bash
export FRED_API_KEY="sua_chave_aqui"
```

---

## 🎯 Passo 4: Rodar o Dashboard

### 4.1 Inicie o Backend (API)

Em um terminal, execute:

```bash
# Entre na pasta do dashboard
cd dashboard

# Inicie a API
python backend_api.py
```

✅ Você verá a mensagem:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**⚠️ MANTENHA ESTE TERMINAL ABERTO!**

### 4.2 Abra o Dashboard no Navegador

Em um **NOVO** terminal (sem fechar o anterior):

```bash
# Entre na pasta do dashboard
cd dashboard

# Windows - abra o arquivo HTML
start index.html

# Mac
open index.html

# Linux
xdg-open index.html
```

**OU simplesmente**:
- Navegue até a pasta `dashboard`
- Dê duplo-clique no arquivo `index.html`

---

## 🎨 Passo 5: Usar o Dashboard

### 5.1 Tela Inicial

Você verá 3 cards com os perfis de investimento:
- 🛡️ **Conservador** - Foco em renda fixa e segurança
- ⚖️ **Intermediário** - Balanceado entre segurança e crescimento  
- 🚀 **Agressivo** - Foco em crescimento e ações

### 5.2 Fazer um Novo Aporte

1. **Clique no perfil desejado** (ex: Intermediário)
2. **Digite o valor do aporte** (ex: 5000)
3. **Clique em "Gerar Recomendação"**
4. **Aguarde 5-10 segundos** enquanto o algoritmo:
   - Busca dados econômicos em tempo real
   - Analisa indicadores macro (PIB, inflação, juros)
   - Calcula alocação otimizada por setor
   - Gera justificativas baseadas em IA

### 5.3 Ver Resultados

Você verá:
- 📊 **Gráfico de pizza** - Distribuição do aporte por setor
- 📈 **Porcentagens** - Quanto vai para cada área (ex: Tecnologia 25%)
- 💡 **Justificativas** - Por que cada decisão foi tomada
- 🎯 **Indicadores** - Dados econômicos usados na análise

---

## 🔧 Solução de Problemas

### ❌ Erro: "python: command not found"
**Solução**: Python não está instalado ou não está no PATH
- Reinstale o Python marcando "Add to PATH"
- Ou use `python3` ao invés de `python`

### ❌ Erro: "ModuleNotFoundError: No module named..."
**Solução**: Dependências não instaladas
```bash
pip install -r requirements.txt
```

### ❌ Erro: "Connection refused" ou "API não responde"
**Solução**: Backend não está rodando
1. Abra um terminal
2. Execute: `cd dashboard && python backend_api.py`
3. Mantenha o terminal aberto

### ❌ Dashboard mostra erro de API Key
**Solução**: Configure a chave FRED no arquivo `.env`
```env
FRED_API_KEY=sua_chave_aqui
```

### ❌ Gráfico não aparece
**Solução**: 
1. Abra o Console do Navegador (F12)
2. Verifique se há erros JavaScript
3. Certifique-se que o backend está rodando
4. Recarregue a página (Ctrl+R ou Cmd+R)

---

## 📱 Acesso Remoto (Opcional)

Para acessar o dashboard de outros dispositivos na mesma rede:

1. Descubra seu IP local:
```bash
# Windows
ipconfig
# Mac/Linux  
ifconfig
```

2. Inicie o backend com:
```bash
python backend_api.py --host 0.0.0.0
```

3. Acesse de qualquer dispositivo:
```
http://SEU_IP:8000
```

---

## 🐳 Instalação com Docker (Avançado)

Se você preferir usar Docker:

```bash
# Build da imagem
docker build -t quant-invest .

# Rode o container
docker run -p 8000:8000 -e FRED_API_KEY=sua_chave quant-invest
```

---

## 📚 Próximos Passos

Agora que tudo está funcionando:

1. ✅ Teste os 3 perfis de investimento
2. ✅ Experimente diferentes valores de aporte
3. ✅ Compare as recomendações ao longo do tempo
4. ✅ Leia a documentação completa no `README.md`
5. ✅ Explore o código em `algorithms/` para entender a lógica

---

## 🆘 Precisa de Ajuda?

- 📖 Leia a documentação: `README.md`
- 🐛 Reportar bugs: [GitHub Issues](https://github.com/noxted/quant-invest-algo/issues)
- 💬 Dúvidas: Abra uma Discussion no GitHub

---

## ⚡ Comandos Rápidos (Resumo)

```bash
# 1. Clone
git clone https://github.com/noxted/quant-invest-algo.git
cd quant-invest-algo

# 2. Instale
pip install -r requirements.txt

# 3. Configure .env
echo "FRED_API_KEY=sua_chave" > .env

# 4. Rode o backend
cd dashboard && python backend_api.py

# 5. Abra index.html no navegador
```

**Pronto! Agora é só investir com inteligência! 🚀📈**
