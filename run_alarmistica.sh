#!/bin/bash
#
# Script para executar a alarmística de recargas
# Executa a cada 30 minutos via cron
#

# Diretório do projeto
cd /projetos/alarmistica_recargas

# Executar script Python
/usr/bin/python3 servcel_extractor.py >> /projetos/alarmistica_recargas/Logs/cron.log 2>&1

# Adicionar timestamp ao log
echo "========================================" >> /projetos/alarmistica_recargas/Logs/cron.log
echo "Execução finalizada em: $(date)" >> /projetos/alarmistica_recargas/Logs/cron.log
echo "========================================" >> /projetos/alarmistica_recargas/Logs/cron.log
