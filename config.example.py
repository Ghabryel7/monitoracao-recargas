"""
Arquivo de Configuração - Sistema de Monitoramento de Recargas
IMPORTANTE: Renomeie para config.py e preencha com suas credenciais reais
"""

# ===== CREDENCIAIS DE ACESSO =====
# Credenciais do portal web de transações
LOGIN = "seu_usuario"
SENHA = "sua_senha"

# ===== URLs DO SISTEMA =====
URL_BASE = "https://portal-exemplo.com.br"

# ===== DIRETÓRIOS =====
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(BASE_DIR, "Recargas")
SCREENSHOT_DIR = os.path.join(BASE_DIR, "Screenshots")
LOG_DIR = os.path.join(BASE_DIR, "Logs")

# ===== BANCO DE DADOS (OPCIONAL) =====
DB_HOST = "seu-db-host.exemplo.com"
DB_USER = "seu_usuario_db"
DB_PASSWORD = "sua_senha_db"
DB_NAME = "nome_database"

# ===== TELEGRAM (OPCIONAL) =====
TELEGRAM_TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
TELEGRAM_CHAT_ID = "-123456789"

# ===== CONFIGURAÇÕES DE E-MAIL =====
# Configurações SMTP para envio de alertas
EMAIL_SMTP_SERVER = "smtp.gmail.com"  # ou smtp.office365.com para Outlook
EMAIL_SMTP_PORT = 587  # Porta TLS padrão
EMAIL_USER = "seu.email@exemplo.com"  # E-mail que enviará os alertas
EMAIL_PASSWORD = "sua_senha_email"  # Senha do e-mail ou app password

# Destinatários dos alertas
EMAIL_DESTINATARIOS_NOC = [
    "equipe1@exemplo.com",
    "equipe2@exemplo.com",
    "noc@exemplo.com",
]

# ===== THRESHOLDS DE ALARMÍSTICA =====
# IMPORTANTE: Thresholds baseados em análise histórica
# Ajuste conforme o comportamento do seu sistema

# Percentual mínimo de código N2 (erro servidor) para emitir Crítico
# CRÍTICO: Mantido em 10% para TODOS os períodos (problema grave no servidor)
THRESHOLD_ALERT_N2 = 10.0  # 10% de erros N2 (servidor) - TODOS OS PERÍODOS

# Thresholds de NEGADAS por período do dia (baseado em dados históricos)
# Objetivo: Alertar antes de atingir limite crítico
THRESHOLDS_POR_PERIODO = {
    "manha": {  # 06:00 - 11:59
        "threshold_negadas": 12.5,  # Percentual para alertar
        "threshold_n2": 10.0,       # Crítico mantido em 10%
    },
    "tarde": {  # 12:00 - 17:59
        "threshold_negadas": 11.0,
        "threshold_n2": 10.0,
    },
    "noite": {  # 18:00 - 23:59
        "threshold_negadas": 13.0,
        "threshold_n2": 10.0,
    },
    "madrugada": {  # 00:00 - 05:59
        "threshold_negadas": 17.7,  # Maior tolerância (volume menor)
        "threshold_n2": 10.0,
    }
}

# Fallback: Se não conseguir determinar o período, usar valores padrão
THRESHOLD_WARNING_NEGADAS = 10.0  # 10% de recargas negadas (padrão)

# ===== FUNÇÕES HELPER =====
def get_periodo_do_dia():
    """
    Determina o período do dia baseado na hora atual
    Returns: 'manha', 'tarde', 'noite' ou 'madrugada'
    """
    from datetime import datetime
    hora_atual = datetime.now().hour

    if 6 <= hora_atual < 12:
        return "manha"
    elif 12 <= hora_atual < 18:
        return "tarde"
    elif 18 <= hora_atual < 24:
        return "noite"
    else:
        return "madrugada"

def get_thresholds_atuais():
    """
    Retorna os thresholds apropriados baseados no período do dia atual
    Returns: dict com 'threshold_negadas' e 'threshold_n2'
    """
    periodo = get_periodo_do_dia()
    thresholds = THRESHOLDS_POR_PERIODO.get(periodo, {
        "threshold_negadas": THRESHOLD_WARNING_NEGADAS,
        "threshold_n2": THRESHOLD_ALERT_N2
    })
    return {
        "periodo": periodo,
        "threshold_negadas": thresholds["threshold_negadas"],
        "threshold_n2": thresholds["threshold_n2"]
    }
