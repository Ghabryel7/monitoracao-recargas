#!/bin/bash

echo "==========================================="
echo "  Setup - Sistema de Monitoramento"
echo "==========================================="
echo ""

# Verificar Python
echo "[1/6] Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instale Python 3.8 ou superior."
    exit 1
fi
echo "✅ Python encontrado: $(python3 --version)"

# Criar ambiente virtual
echo ""
echo "[2/6] Criando ambiente virtual..."
python3 -m venv venv
echo "✅ Ambiente virtual criado"

# Ativar ambiente virtual
echo ""
echo "[3/6] Ativando ambiente virtual..."
source venv/bin/activate
echo "✅ Ambiente virtual ativado"

# Instalar dependências
echo ""
echo "[4/6] Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependências instaladas"

# Criar diretórios
echo ""
echo "[5/6] Criando diretórios..."
mkdir -p Recargas
mkdir -p output
mkdir -p Logs
mkdir -p Screenshots
echo "✅ Diretórios criados"

# Copiar config.example.py para config.py (se não existir)
echo ""
echo "[6/6] Configurando arquivo de configuração..."
if [ ! -f config.py ]; then
    cp config.example.py config.py
    echo "✅ Arquivo config.py criado"
    echo "⚠️  IMPORTANTE: Edite o arquivo config.py com suas credenciais!"
    echo "   Execute: nano config.py"
else
    echo "✅ Arquivo config.py já existe"
fi

echo ""
echo "==========================================="
echo "  Setup concluído com sucesso!"
echo "==========================================="
echo ""
echo "Próximos passos:"
echo "1. Edite o arquivo config.py com suas credenciais"
echo "   $ nano config.py"
echo ""
echo "2. Teste a execução:"
echo "   $ python3 servcel_extractor.py"
echo ""
echo "3. Configure o cron (opcional):"
echo "   $ crontab -e"
echo "   Adicione: 0,30 * * * * $(pwd)/run_alarmistica.sh"
echo ""
