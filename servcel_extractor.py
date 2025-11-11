"""
ServCel Report Extractor - Production Version
Extrai relatório de transações do GWCelWeb automaticamente
Compatível com Linux/Windows (headless mode)
"""

import os
import sys
import time
import logging
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options

# ===== CONFIGURAÇÃO DE LOGGING =====
from logging.handlers import RotatingFileHandler

# Criar diretório de logs
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Arquivo de log com data
log_filename = os.path.join(LOG_DIR, f"alarmistica_{datetime.now().strftime('%Y%m%d')}.log")

# Configurar logging com rotação
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(
            log_filename,
            maxBytes=10*1024*1024,  # 10MB por arquivo
            backupCount=30,  # Manter 30 backups (30 dias)
            encoding='utf-8'
        ),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)
logger.info(f"Logs salvos em: {log_filename}")

# ===== IMPORTAR CONFIGURAÇÕES =====
try:
    from config import (
        LOGIN, SENHA, URL_BASE, DOWNLOAD_DIR,
        EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT, EMAIL_USER, EMAIL_PASSWORD,
        EMAIL_DESTINATARIOS_NOC, THRESHOLD_WARNING_NEGADAS, THRESHOLD_ALERT_N2,
        get_thresholds_atuais
    )
    logger.info("Configurações carregadas com sucesso")
except ImportError:
    logger.error("Arquivo config.py não encontrado!")
    logger.error("Crie o arquivo config.py com as credenciais corretas.")
    sys.exit(1)

# ===== IMPORTAR MÓDULOS DE ALARMÍSTICA =====
try:
    from recarga_analyzer import RecargaAnalyzer
    from email_sender import EmailSender
    from report_generator import gerar_relatorio_completo
    logger.info("Módulos de alarmística carregados com sucesso")
except ImportError as e:
    logger.error(f"Erro ao importar módulos de alarmística: {e}")
    logger.error("Certifique-se que recarga_analyzer.py, email_sender.py e report_generator.py estão no diretório")
    sys.exit(1)

# ===== CRIAR DIRETÓRIOS =====
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs("output", exist_ok=True)  # Pasta para gráficos e Excel


def calcular_periodo():
    """
    Calcula o período de busca (JANELA DE 30 MINUTOS)

    Exemplos:
    - Execução às 10:00 → Busca 09:30 até 10:00
    - Execução às 10:30 → Busca 10:00 até 10:30
    - Execução às 14:45 → Busca 14:15 até 14:45
    """
    agora = datetime.now()

    # Calcular momento 30 minutos atrás
    inicio = agora - timedelta(minutes=30)

    # Datas
    data_inicial = inicio.strftime("%d/%m/%Y")
    data_final = agora.strftime("%d/%m/%Y")

    # Horas e minutos
    hora_inicial = inicio.strftime("%H")
    minuto_inicial = inicio.strftime("%M")
    hora_final = agora.strftime("%H")
    minuto_final = agora.strftime("%M")

    return {
        'data_inicial': data_inicial,
        'data_final': data_final,
        'hora_inicial': hora_inicial,
        'hora_final': hora_final,
        'minuto_inicial': minuto_inicial,
        'minuto_final': minuto_final,
        'periodo_completo': f"{data_inicial} - {hora_inicial}h{minuto_inicial} até {hora_final}h{minuto_final}"
    }


def configurar_chrome(headless=True):
    """
    Configura opções do Chrome
    """
    chrome_options = Options()

    # Configurações de download
    prefs = {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option('prefs', prefs)

    # Modo headless (sem interface gráfica)
    if headless:
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')

    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--window-size=1920,1080')

    return chrome_options


def fazer_login(driver):
    """
    Realiza login no GWCelWeb
    """
    logger.info("Iniciando login...")

    try:
        driver.get(URL_BASE)
        time.sleep(3)

        # Preencher credenciais
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        username_field.send_keys(LOGIN)

        driver.find_element(By.ID, "password").send_keys(SENHA)
        driver.find_element(By.ID, "kc-login").click()

        time.sleep(5)

        # Verificar se login foi bem-sucedido
        if "login-actions/authenticate" in driver.current_url:
            logger.error("Falha no login - credenciais inválidas")
            return False

        logger.info("Login realizado com sucesso")
        return True

    except Exception as e:
        logger.error(f"Erro no login: {e}")
        return False


def navegar_transacoes(driver):
    """
    Navega até a página de transações via menu
    """
    logger.info("Navegando para página de transações...")

    try:
        # Hover no menu ServCel
        servcel_link = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'ServCel')]"))
        )

        actions = ActionChains(driver)
        actions.move_to_element(servcel_link).perform()
        time.sleep(2)

        # Clicar em Transações
        transacao_link = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Transações') or contains(text(), 'Transacao')]"))
        )
        transacao_link.click()
        time.sleep(5)

        logger.info("Página de transações acessada")
        return True

    except Exception as e:
        logger.error(f"Erro ao navegar para transações: {e}")
        return False


def preencher_formulario(driver, periodo):
    """
    Preenche o formulário de busca com data/hora
    """
    logger.info("Preenchendo formulário de busca...")

    try:
        time.sleep(3)

        # Aguardar página carregar
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "initialDate"))
        )
        time.sleep(1)

        # Campos de data usando JavaScript (os campos têm máscara/validação)
        # Data inicial
        data_inicial_valor = periodo['data_inicial']
        driver.execute_script(
            "document.getElementById('initialDate').value = arguments[0];"
            "document.getElementById('initialDate').dispatchEvent(new Event('input', { bubbles: true }));"
            "document.getElementById('initialDate').dispatchEvent(new Event('change', { bubbles: true }));",
            data_inicial_valor
        )
        logger.info(f"Data inicial: {data_inicial_valor}")
        time.sleep(1)

        # Data final
        data_final_valor = periodo['data_final']
        driver.execute_script(
            "document.getElementById('finalDate').value = arguments[0];"
            "document.getElementById('finalDate').dispatchEvent(new Event('input', { bubbles: true }));"
            "document.getElementById('finalDate').dispatchEvent(new Event('change', { bubbles: true }));",
            data_final_valor
        )
        logger.info(f"Data final: {data_final_valor}")
        time.sleep(1)

        # Campos de hora - Digitar com os dois pontos (formato HH:MM)
        try:
            # Hora inicial
            logger.info("Preenchendo hora inicial...")
            hora_inicial_input = driver.find_element(By.ID, "initialHour")

            # Scroll até o elemento e garantir que está visível
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", hora_inicial_input)
            time.sleep(0.5)

            # Usar ActionChains para interagir
            actions = ActionChains(driver)
            actions.move_to_element(hora_inicial_input).click().perform()
            time.sleep(0.5)

            # Digitar no formato HH:MM usando ActionChains
            hora_inicial_valor = f"{periodo['hora_inicial']}:{periodo['minuto_inicial']}"
            logger.info(f"Digitando hora inicial: {hora_inicial_valor}")
            actions.send_keys(hora_inicial_valor).perform()

            logger.info(f"✅ Hora inicial preenchida: {hora_inicial_valor}")
            time.sleep(1)
        except Exception as e:
            logger.error(f"❌ ERRO ao preencher hora inicial: {e}")
            raise

        try:
            # Hora final
            logger.info("Preenchendo hora final...")
            hora_final_input = driver.find_element(By.ID, "finalHour")

            # Scroll até o elemento
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", hora_final_input)
            time.sleep(0.5)

            # Usar ActionChains para interagir
            actions = ActionChains(driver)
            actions.move_to_element(hora_final_input).click().perform()
            time.sleep(0.5)

            # Digitar no formato HH:MM usando ActionChains
            hora_final_valor = f"{periodo['hora_final']}:{periodo['minuto_final']}"
            logger.info(f"Digitando hora final: {hora_final_valor}")
            actions.send_keys(hora_final_valor).perform()

            logger.info(f"✅ Hora final preenchida: {hora_final_valor}")
            time.sleep(1)
        except Exception as e:
            logger.error(f"❌ ERRO ao preencher hora final: {e}")
            raise

        logger.info("✅ Formulário preenchido com sucesso")
        return True

    except Exception as e:
        logger.error(f"❌ ERRO ao preencher formulário: {e}")
        import traceback
        traceback.print_exc()
        return False


def executar_pesquisa(driver):
    """
    Clica no botão Pesquisar e aguarda resultados
    """
    logger.info("Executando pesquisa...")

    try:
        # Procurar e clicar no botão Pesquisar
        pesquisar_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Pesquisar')]"))
        )

        pesquisar_button.click()
        logger.info("Pesquisa iniciada")

        # Aguardar resultados
        time.sleep(10)
        logger.info("Resultados carregados")

        return True

    except Exception as e:
        logger.error(f"Erro ao executar pesquisa: {e}")
        return False


def exportar_relatorio(driver):
    """
    Clica no botão Exportar e baixa o arquivo
    """
    logger.info("Procurando botão Exportar...")

    try:
        time.sleep(3)

        # Procurar botão Exportar
        exportar_button = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Exportar') or contains(text(), 'Export')]"))
        )

        logger.info("Botão Exportar encontrado")
        exportar_button.click()
        logger.info("Download iniciado")

        # Aguardar download
        time.sleep(15)

        return True

    except Exception as e:
        logger.error(f"Erro ao exportar: {e}")
        return False


def verificar_download():
    """
    Verifica se o arquivo foi baixado com sucesso
    """
    logger.info("Verificando arquivos baixados...")

    try:
        arquivos = os.listdir(DOWNLOAD_DIR)
        excel_files = [f for f in arquivos if f.endswith(('.xlsx', '.xls')) and 'Transacao' in f]

        if excel_files:
            # Ordenar por data de modificação (mais recente primeiro)
            excel_files.sort(key=lambda x: os.path.getmtime(os.path.join(DOWNLOAD_DIR, x)), reverse=True)
            arquivo_recente = excel_files[0]
            tamanho = os.path.getsize(os.path.join(DOWNLOAD_DIR, arquivo_recente))

            logger.info(f"Arquivo baixado: {arquivo_recente} ({tamanho} bytes)")
            return arquivo_recente
        else:
            logger.warning("Nenhum arquivo Excel encontrado")
            return None

    except Exception as e:
        logger.error(f"Erro ao verificar download: {e}")
        return None


def analisar_e_alertar(arquivo_path: str, periodo: dict) -> bool:
    """
    Analisa o arquivo de recargas e envia alerta se necessário

    Args:
        arquivo_path: Caminho completo do arquivo a analisar
        periodo: Dicionário com informações do período analisado

    Returns:
        True se análise foi bem-sucedida
    """
    logger.info("="*70)
    logger.info("INICIANDO ANÁLISE DE ALARMÍSTICA")
    logger.info("="*70)

    try:
        # Obter thresholds dinâmicos baseados no período do dia atual
        thresholds = get_thresholds_atuais()
        periodo_nome = thresholds['periodo'].capitalize()

        # Obter informação de período (se disponível dos logs)
        periodo_info = "Últimos 30 minutos"

        logger.info(f"=== THRESHOLDS DINÂMICOS ===")
        logger.info(f"Período do dia: {periodo_nome}")
        logger.info(f"Threshold Negadas: {thresholds['threshold_negadas']}%")
        logger.info(f"Threshold N2 (Crítico): {thresholds['threshold_n2']}%")

        # Criar analisador com thresholds dinâmicos
        analyzer = RecargaAnalyzer(
            threshold_negadas=thresholds['threshold_negadas'],
            threshold_n2=thresholds['threshold_n2'],
            periodo_texto=periodo_info
        )

        # Carregar arquivo
        if not analyzer.carregar_arquivo(arquivo_path):
            logger.error("Falha ao carregar arquivo para análise")
            return False

        # Realizar análise
        resultado = analyzer.analisar()

        if not resultado:
            logger.error("Falha na análise dos dados")
            return False

        # Exibir resultado
        logger.info(f"Total de transações: {resultado['total_transacoes']}")
        logger.info(f"Recargas efetuadas: {resultado['transacoes_efetuadas']}")
        logger.info(f"Recargas negadas: {resultado['transacoes_negadas']} ({resultado['percentual_negadas']}%)")
        logger.info(f"Recargas com N2 (Erro Servidor): {resultado['transacoes_n2']} ({resultado['percentual_n2']}%)")
        logger.info(f"Nível de alarme: {resultado['nivel_alarme']}")

        # Verificar se há alarme
        if analyzer.tem_alarme():
            nivel_alarme = resultado['nivel_alarme']
            mensagem = analyzer.get_mensagem_alarme()

            logger.warning("="*70)
            logger.warning(f"ALARME DETECTADO: {nivel_alarme}")
            logger.warning(mensagem)
            logger.warning("="*70)

            # Enviar e-mail
            logger.info("Preparando envio de e-mail de alerta...")

            try:
                # Gerar relatório completo (tabelas, gráficos, excel)
                logger.info("Gerando relatório completo (gráficos e Excel)...")
                relatorio = gerar_relatorio_completo(analyzer, output_dir="output")

                if not relatorio:
                    logger.error("Falha ao gerar relatório completo")
                    return False

                # Gerar tabelas adicionais
                tabela_resumo = analyzer.gerar_tabela_resumo()
                tabela_codigos = analyzer.gerar_tabela_codigos()
                tabela_negadas = analyzer.gerar_tabela_negadas()

                # Criar sender
                sender = EmailSender(
                    smtp_server=EMAIL_SMTP_SERVER,
                    smtp_port=EMAIL_SMTP_PORT,
                    smtp_user=EMAIL_USER,
                    smtp_password=EMAIL_PASSWORD
                )

                # Formatar período para exibição (ex: "14h às 14h30")
                hora_ini = f"{periodo['hora_inicial']}h{periodo['minuto_inicial']}" if periodo['minuto_inicial'] != '00' else f"{periodo['hora_inicial']}h"
                hora_fim = f"{periodo['hora_final']}h{periodo['minuto_final']}" if periodo['minuto_final'] != '00' else f"{periodo['hora_final']}h"
                periodo_texto = f"{hora_ini} às {hora_fim}"

                # Enviar alerta com todos os anexos
                enviado = sender.enviar_alerta(
                    destinatarios=EMAIL_DESTINATARIOS_NOC,
                    resultado_analise=resultado,
                    tabela_resumo=tabela_resumo,
                    tabela_codigos=tabela_codigos,
                    tabela_negadas=tabela_negadas,
                    ranking_negadas=relatorio.get('ranking_negadas'),
                    ranking_n2=relatorio.get('ranking_n2'),
                    nivel_alarme=nivel_alarme,
                    periodo_analise=periodo_texto,
                    excel_path=relatorio.get('excel')
                )

                if enviado:
                    logger.info("✅ E-mail de alerta enviado com sucesso!")
                    logger.info(f"Destinatários: {', '.join(EMAIL_DESTINATARIOS_NOC)}")
                    if relatorio.get('excel'):
                        logger.info(f"Excel anexado: {os.path.basename(relatorio.get('excel'))}")
                else:
                    logger.error("❌ Falha ao enviar e-mail de alerta")
                    return False

            except Exception as e:
                logger.error(f"Erro ao enviar e-mail: {e}")
                import traceback
                logger.error(traceback.format_exc())
                return False

        else:
            logger.info("✅ Status normal - nenhum alarme detectado")
            logger.info(f"Percentual de negadas: {resultado['percentual_negadas']}% (threshold: {thresholds['threshold_negadas']}%)")
            logger.info(f"Percentual de N2: {resultado['percentual_n2']}% (threshold: {thresholds['threshold_n2']}%)")

        logger.info("="*70)
        logger.info("ANÁLISE DE ALARMÍSTICA CONCLUÍDA")
        logger.info("="*70)

        return True

    except Exception as e:
        logger.error(f"Erro durante análise de alarmística: {e}")
        return False


def main():
    """
    Função principal
    """
    logger.info("="*70)
    logger.info("SERVCEL REPORT EXTRACTOR - INICIANDO")
    logger.info("="*70)

    driver = None

    try:
        # Calcular período
        periodo = calcular_periodo()
        logger.info(f"Período: {periodo['data_inicial']} {periodo['hora_inicial']}:{periodo['minuto_inicial']} até {periodo['data_final']} {periodo['hora_final']}:{periodo['minuto_final']}")

        # Configurar Chrome
        chrome_options = configurar_chrome(headless=True)

        # Iniciar driver
        logger.info("Iniciando Chrome WebDriver...")
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(60)
        logger.info("Chrome iniciado com sucesso")

        # Executar fluxo
        if not fazer_login(driver):
            raise Exception("Falha no login")

        if not navegar_transacoes(driver):
            raise Exception("Falha ao navegar para transações")

        if not preencher_formulario(driver, periodo):
            raise Exception("Falha ao preencher formulário")

        if not executar_pesquisa(driver):
            raise Exception("Falha ao executar pesquisa")

        if not exportar_relatorio(driver):
            raise Exception("Falha ao exportar relatório")

        # Verificar arquivo
        arquivo = verificar_download()

        if arquivo:
            logger.info("="*70)
            logger.info("DOWNLOAD CONCLUÍDO COM SUCESSO")
            logger.info(f"Arquivo: {arquivo}")
            logger.info(f"Local: {DOWNLOAD_DIR}")
            logger.info("="*70)

            # Executar análise de alarmística
            arquivo_completo = os.path.join(DOWNLOAD_DIR, arquivo)
            analise_ok = analisar_e_alertar(arquivo_completo, periodo)

            if analise_ok:
                logger.info("="*70)
                logger.info("PROCESSO COMPLETO CONCLUÍDO COM SUCESSO")
                logger.info("="*70)
                return 0
            else:
                logger.warning("Download realizado, mas análise de alarmística falhou")
                return 1
        else:
            logger.error("Processo falhou: arquivo não encontrado")
            return 1

    except Exception as e:
        logger.error(f"Erro crítico: {e}")
        return 1

    finally:
        if driver:
            driver.quit()
            logger.info("Chrome fechado")


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
