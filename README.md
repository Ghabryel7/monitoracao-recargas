# 📊 Sistema de Monitoramento de Recargas

Sistema automatizado de monitoramento e alarmística para transações de recarga de celular, com detecção inteligente de anomalias e alertas em tempo real.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Selenium](https://img.shields.io/badge/Selenium-4.x-green)](https://www.selenium.dev/)
[![Pandas](https://img.shields.io/badge/Pandas-Latest-orange)](https://pandas.pydata.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 Visão Geral

Sistema desenvolvido para monitorar automaticamente transações de recarga em portais web, analisando dados em janelas de 30 minutos e enviando alertas por email quando detecta anomalias.

### Principais Funcionalidades

- 🤖 **Automação completa** com Selenium WebDriver
- 📈 **Análise inteligente** com thresholds dinâmicos por período do dia
- 📧 **Alertas por email** com relatórios HTML formatados
- 📊 **Geração de relatórios** Excel e gráficos
- ⏰ **Execução agendada** via cron (a cada 30 minutos)
- 🔍 **Detecção de anomalias** em tempo real
- 📝 **Logging detalhado** com rotação automática

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────┐
│           CRON JOB (Execução automática)            │
│         A cada 30 minutos (:00 e :30)               │
└────────────────────┬────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────┐
│      servcel_extractor.py (Orquestrador)            │
│  • Login automático no portal                       │
│  • Filtro de período (últimos 30 min)              │
│  • Download de dados (Excel)                        │
└────────────────────┬────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────┐
│     recarga_analyzer.py (Motor de Análise)          │
│  • Carrega e processa dados                         │
│  • Calcula métricas e percentuais                   │
│  • Aplica thresholds dinâmicos                      │
│  • Determina nível de alarme                        │
└────────────────────┬────────────────────────────────┘
                     ↓
              [Tem alarme?]
                /       \
             NÃO        SIM
              ↓          ↓
         Log Normal   ┌──────────────────────────┐
         e EXIT       │ report_generator.py       │
                      │ • Gera Excel formatado    │
                      │ • Cria gráficos (PNG)     │
                      └────────┬─────────────────┘
                               ↓
                      ┌──────────────────────────┐
                      │ email_sender.py           │
                      │ • Monta HTML formatado    │
                      │ • Anexa relatórios        │
                      │ • Envia via SMTP          │
                      └──────────────────────────┘
```

## 🚀 Tecnologias Utilizadas

### Backend & Automação
- **Python 3.8+** - Linguagem principal
- **Selenium WebDriver** - Automação de navegador web
- **Pandas** - Análise e manipulação de dados
- **Openpyxl** - Leitura e escrita de arquivos Excel

### Comunicação & Relatórios
- **smtplib** - Envio de emails via SMTP
- **Matplotlib** - Geração de gráficos
- **HTML/CSS** - Formatação de emails

### Infraestrutura
- **Cron** - Agendamento de tarefas
- **Logging** - Sistema de logs com rotação
- **Chrome/ChromeDriver** - Navegador headless

## 📋 Pré-requisitos

- Python 3.8 ou superior
- Google Chrome ou Chromium
- ChromeDriver (compatível com a versão do Chrome)
- Acesso SMTP para envio de emails

## 🔧 Instalação

1. **Clone o repositório**
```bash
git clone https://github.com/seu-usuario/monitoracao-recargas.git
cd monitoracao-recargas
```

2. **Crie um ambiente virtual**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Configure as credenciais**
```bash
cp config.example.py config.py
nano config.py  # Edite com suas credenciais
```

5. **Instale o Chrome e ChromeDriver**
```bash
# Ubuntu/Debian
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb

# ChromeDriver será instalado automaticamente via selenium-manager
```

## ⚙️ Configuração

### config.py

Configure os seguintes parâmetros no arquivo `config.py`:

```python
# Credenciais do portal
LOGIN = "seu_usuario"
SENHA = "sua_senha"
URL_BASE = "https://portal-exemplo.com.br"

# Configurações SMTP
EMAIL_SMTP_SERVER = "smtp.gmail.com"
EMAIL_SMTP_PORT = 587
EMAIL_USER = "seu.email@exemplo.com"
EMAIL_PASSWORD = "sua_senha"

# Destinatários
EMAIL_DESTINATARIOS_NOC = [
    "equipe@exemplo.com"
]

# Thresholds dinâmicos por período
THRESHOLDS_POR_PERIODO = {
    "manha": {"threshold_negadas": 12.5, "threshold_n2": 10.0},
    "tarde": {"threshold_negadas": 11.0, "threshold_n2": 10.0},
    "noite": {"threshold_negadas": 13.0, "threshold_n2": 10.0},
    "madrugada": {"threshold_negadas": 17.7, "threshold_n2": 10.0}
}
```

## 🎮 Uso

### Execução Manual

```bash
# Executar uma vez
python3 servcel_extractor.py
```

### Execução Automática (Cron)

Adicione ao crontab:

```bash
crontab -e

# Executar a cada 30 minutos
0,30 * * * * /caminho/completo/run_alarmistica.sh
```

### Testar Conexão SMTP

```python
from email_sender import EmailSender

sender = EmailSender('smtp.gmail.com', 587, 'seu@email.com', 'senha')
sender.testar_conexao()
```

## 📊 Níveis de Alarme

O sistema possui 3 níveis de alarme:

### 🟢 Normal
- **Condição:** Percentual de negadas < threshold E percentual N2 < 10%
- **Ação:** Log apenas, sem envio de email

### 🟡 Alerta
- **Condição:** Percentual de negadas ≥ threshold do período
- **Ação:** Email de alerta com análise completa
- **Exemplo:** 12% de recargas negadas no período da manhã

### 🔴 Crítico
- **Condição:** Percentual de erros N2 ≥ 10%
- **Prioridade:** MÁXIMA (problema no servidor)
- **Ação:** Email crítico com análise completa

## 📈 Thresholds Dinâmicos

O sistema ajusta automaticamente os thresholds baseado no período do dia:

| Período | Horário | Threshold | Justificativa |
|---------|---------|-----------|---------------|
| Manhã | 06:00 - 11:59 | 12.5% | Horário comercial, alta sensibilidade |
| Tarde | 12:00 - 17:59 | 11.0% | Horário pico, máxima sensibilidade |
| Noite | 18:00 - 23:59 | 13.0% | Volume moderado |
| Madrugada | 00:00 - 05:59 | 17.7% | Volume baixo, maior tolerância |

**Threshold N2 (Crítico):** Fixo em 10% para todos os períodos

## 📁 Estrutura do Projeto

```
monitoracao-recargas/
├── servcel_extractor.py      # Script principal (orquestração)
├── recarga_analyzer.py        # Análise de dados e alarmes
├── email_sender.py            # Envio de emails formatados
├── report_generator.py        # Geração de relatórios e gráficos
├── config.py                  # Configurações (não versionado)
├── config.example.py          # Template de configuração
├── run_alarmistica.sh         # Script de execução do cron
├── requirements.txt           # Dependências Python
├── README.md                  # Esta documentação
└── .gitignore                 # Arquivos ignorados pelo Git
```

## 🔍 Funcionalidades Detalhadas

### 1. Web Scraping Inteligente

- **Login automático** com tratamento de erros
- **Preenchimento de formulários** com campos JavaScript complexos
- **ActionChains** para interação com elementos dinâmicos
- **Scrolling automático** para garantir visibilidade dos elementos
- **Download automático** com verificação de conclusão

### 2. Análise de Dados

- **Cálculo de métricas**:
  - Total de transações
  - Percentual de recargas efetuadas/negadas
  - Percentual de erros N2 (servidor)
  - Distribuição de códigos de resposta

- **Rankings**:
  - Top 10 origens com mais negações
  - Top 10 origens com mais erros N2

- **Detecção de anomalias**:
  - Comparação com thresholds dinâmicos
  - Identificação de padrões anormais

### 3. Relatórios e Visualizações

- **Excel formatado** com múltiplas abas:
  - Resumo geral
  - Ranking de negadas
  - Ranking de N2
  - Distribuição de códigos
  - Lista completa de negadas

- **Gráficos PNG**:
  - Gráficos de barras horizontais
  - Top 10 origens problemáticas

### 4. Sistema de Alertas

- **Email HTML formatado** com:
  - Saudação personalizada
  - Tabelas formatadas com CSS
  - Período de análise dinâmico
  - Anexos (Excel)
  - Rodapé com informações técnicas

- **Níveis de prioridade**:
  - Assunto diferenciado (Alerta! / Crítico!)
  - Cores distintas (amarelo/vermelho)

## 🛠️ Desenvolvimento

### Desafios Técnicos Resolvidos

1. **Campos com máscara JavaScript**
   - Problema: `send_keys()` não funcionava em campos de hora
   - Solução: `ActionChains` + `scrollIntoView` + digitação sequencial

2. **Gráficos corrompidos em emails**
   - Problema: Imagens inline não renderizavam no Outlook
   - Solução: Remover gráficos inline, manter apenas anexos

3. **Janela de tempo precisa**
   - Problema: Sistema retornava dados do dia inteiro
   - Solução: Filtro por hora e minuto no formulário web

4. **Thresholds fixos geravam falsos positivos**
   - Problema: Mesmo threshold para todos os períodos
   - Solução: Thresholds dinâmicos baseados em análise histórica

### Boas Práticas Implementadas

- ✅ Logging detalhado com rotação automática
- ✅ Tratamento de exceções em todas as etapas
- ✅ Código modular e reutilizável
- ✅ Configurações externalizadas (config.py)
- ✅ Documentação inline e comentários
- ✅ Type hints para melhor legibilidade
- ✅ Validação de dados em cada etapa

## 📝 Logs

Os logs são salvos em `Logs/alarmistica_YYYYMMDD.log` com:

- Rotação automática (10MB por arquivo)
- 30 backups mantidos
- Formato: timestamp - nível - mensagem

Exemplo:
```
2025-11-11 10:00:02,624 - INFO - Período: 11/11/2025 09:30 até 11/11/2025 10:00
2025-11-11 10:00:09,187 - INFO - Total de transações: 650
2025-11-11 10:00:09,187 - INFO - Recargas negadas: 44 (6.77%)
2025-11-11 10:00:09,187 - INFO - Nível de alarme: Normal
```

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👤 Autor

**Ghabryel Carvalho**

- GitHub: [@seu-usuario](https://github.com/seu-usuario)
- LinkedIn: [Seu Nome](https://linkedin.com/in/seu-perfil)
- Email: seu.email@exemplo.com

## 🙏 Agradecimentos

- Equipe NOC pela colaboração e feedback
- Comunidade Python pela excelente documentação
- Mantenedores do Selenium WebDriver

---

⭐ Se este projeto foi útil para você, considere dar uma estrela!
