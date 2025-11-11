"""
Módulo de Envio de E-mails
Envia alertas de recargas com formatação HTML
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders
from typing import List, Dict, Optional
import pandas as pd
from datetime import datetime

logger = logging.getLogger(__name__)


class EmailSender:
    """
    Envia e-mails formatados com alertas de recargas
    """

    def __init__(self, smtp_server: str, smtp_port: int, smtp_user: str, smtp_password: str):
        """
        Inicializa o sender de e-mail

        Args:
            smtp_server: Servidor SMTP
            smtp_port: Porta SMTP (587 para TLS, 465 para SSL)
            smtp_user: Usuário de autenticação
            smtp_password: Senha de autenticação
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password

    def enviar_alerta(self,
                     destinatarios: List[str],
                     resultado_analise: Dict,
                     tabela_resumo: pd.DataFrame,
                     tabela_codigos: pd.DataFrame,
                     tabela_negadas: pd.DataFrame,
                     ranking_negadas: pd.DataFrame,
                     ranking_n2: pd.DataFrame,
                     nivel_alarme: str,
                     periodo_analise: str,
                     excel_path: Optional[str] = None) -> bool:
        """
        Envia e-mail de alerta com tabelas formatadas e anexos

        Args:
            destinatarios: Lista de e-mails destino
            resultado_analise: Resultado da análise
            tabela_resumo: DataFrame com resumo
            tabela_codigos: DataFrame com códigos de resposta
            tabela_negadas: DataFrame com transações negadas
            ranking_negadas: DataFrame com ranking de todas negadas
            ranking_n2: DataFrame com ranking específico de N2
            nivel_alarme: 'Crítico' ou 'Alerta'
            periodo_analise: Período analisado (ex: "14h às 14h30")
            excel_path: Caminho do arquivo Excel

        Returns:
            True se enviou com sucesso
        """
        try:
            # Definir assunto baseado no nível
            if nivel_alarme == 'Crítico':
                assunto = "Crítico! - Recargas Negadas Servidor!"
                cor_titulo = "#dc3545"  # Vermelho
            else:
                assunto = "Alerta! - Recargas Negadas Geral!"
                cor_titulo = "#ffc107"  # Amarelo

            # Criar mensagem
            msg = MIMEMultipart('alternative')
            msg['Subject'] = assunto
            msg['From'] = self.smtp_user
            msg['To'] = ', '.join(destinatarios)

            # Gerar corpo HTML
            html_body = self._gerar_html(
                resultado_analise,
                tabela_resumo,
                tabela_codigos,
                tabela_negadas,
                ranking_negadas,
                ranking_n2,
                nivel_alarme,
                cor_titulo,
                periodo_analise
            )

            # Anexar HTML
            msg.attach(MIMEText(html_body, 'html'))

            # Gráficos removidos a pedido do usuário (apareciam corrompidos)

            # Anexar Excel
            if excel_path and os.path.exists(excel_path):
                try:
                    with open(excel_path, 'rb') as f:
                        attachment = MIMEBase('application', 'vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                        attachment.set_payload(f.read())
                        encoders.encode_base64(attachment)
                        attachment.add_header('Content-Disposition', f'attachment; filename={os.path.basename(excel_path)}')
                        msg.attach(attachment)

                    logger.info(f"Excel anexado: {os.path.basename(excel_path)}")
                except Exception as e:
                    logger.error(f"Erro ao anexar Excel: {e}")

            # Enviar e-mail
            logger.info(f"Conectando ao servidor SMTP: {self.smtp_server}:{self.smtp_port}")

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info(f"E-mail enviado com sucesso para {len(destinatarios)} destinatário(s)")
            return True

        except smtplib.SMTPAuthenticationError:
            logger.error("Erro de autenticação SMTP - verifique usuário e senha")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"Erro SMTP ao enviar e-mail: {e}")
            return False
        except Exception as e:
            logger.error(f"Erro ao enviar e-mail: {e}")
            return False

    def _gerar_html(self,
                    resultado: Dict,
                    tabela_resumo: pd.DataFrame,
                    tabela_codigos: pd.DataFrame,
                    tabela_negadas: pd.DataFrame,
                    ranking_negadas: pd.DataFrame,
                    ranking_n2: pd.DataFrame,
                    nivel_alarme: str,
                    cor_titulo: str,
                    periodo_analise: str) -> str:
        """
        Gera HTML formatado para o e-mail

        Args:
            resultado: Resultado da análise
            tabela_resumo: DataFrame resumo
            tabela_codigos: DataFrame códigos
            tabela_negadas: DataFrame negadas
            ranking_negadas: DataFrame ranking de todas negadas
            ranking_n2: DataFrame ranking de N2
            nivel_alarme: Nível do alarme
            cor_titulo: Cor do título
            periodo_analise: Período analisado (ex: "14h às 14h30")

        Returns:
            HTML formatado
        """
        # Saudação e texto inicial
        saudacao = f"""
        <div style="margin-bottom: 20px;">
            <p style="font-size: 14px; color: #333;">Caros, boa tarde.</p>
            <p style="font-size: 14px; color: #333;">Segue o report de recargas negadas.</p>
            <p style="font-size: 13px; color: #666; font-style: italic;"><strong>Período analisado:</strong> {periodo_analise}</p>
        </div>
        """

        # Converter tabelas para HTML
        html_resumo = self._tabela_para_html(tabela_resumo, "Resumo Geral")
        html_ranking_negadas = self._tabela_para_html(ranking_negadas, "Ranking de Origens - Todas as Recargas Negadas")
        html_ranking_n2 = self._tabela_para_html(ranking_n2, "Ranking de Origens - Erros N2 (Servidor)")
        html_codigos = self._tabela_para_html(tabela_codigos, "Distribuição de Códigos de Resposta")
        html_negadas = self._tabela_para_html(tabela_negadas, "Recargas Negadas (Amostra)", max_rows=50)

        # Gráficos REMOVIDOS do inline - serão apenas anexos
        # Os gráficos continuam sendo enviados como anexos no e-mail

        # HTML completo
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin-bottom: 30px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                th {{
                    background-color: #4a5568;
                    color: white;
                    padding: 12px;
                    text-align: left;
                    font-weight: bold;
                }}
                td {{
                    padding: 10px 12px;
                    border-bottom: 1px solid #e2e8f0;
                }}
                tr:nth-child(even) {{
                    background-color: #f7fafc;
                }}
                tr:hover {{
                    background-color: #edf2f7;
                }}
                .secao {{
                    margin-bottom: 40px;
                }}
                .titulo-secao {{
                    color: #2d3748;
                    border-bottom: 2px solid #4a5568;
                    padding-bottom: 10px;
                    margin-bottom: 15px;
                }}
                .footer {{
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #e2e8f0;
                    font-size: 12px;
                    color: #718096;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <h1 style="color: {cor_titulo}; text-align: center; margin-bottom: 30px;">
                Alarmística de Recargas - NOC
            </h1>

            {saudacao}

            <div class="secao">
                {html_resumo}
            </div>

            <div class="secao">
                {html_ranking_negadas}
            </div>

            <div class="secao">
                {html_ranking_n2}
            </div>

            <div class="secao">
                {html_codigos}
            </div>

            <div class="secao">
                {html_negadas}
            </div>

            <div class="footer">
                <p>
                    <strong>Análise realizada em:</strong> {resultado['timestamp_analise']}<br>
                    <strong>Período analisado:</strong> {periodo_analise}<br>
                    <strong>Total de transações analisadas:</strong> {resultado['total_transacoes']}<br>
                    Sistema de Alarmística Automática - Equipe de Monitoramento (Janelas de 30 minutos)
                </p>
            </div>
        </body>
        </html>
        """

        return html

    def _tabela_para_html(self, df: pd.DataFrame, titulo: str, max_rows: int = None) -> str:
        """
        Converte DataFrame para HTML formatado

        Args:
            df: DataFrame a converter
            titulo: Título da tabela
            max_rows: Máximo de linhas a exibir

        Returns:
            HTML da tabela
        """
        if df is None or len(df) == 0:
            return f"""
            <h3 class="titulo-secao">{titulo}</h3>
            <p style="color: #718096;">Nenhum dado disponível</p>
            """

        # Limitar linhas se necessário
        if max_rows and len(df) > max_rows:
            df_display = df.head(max_rows)
            nota = f"<p style='color: #718096; font-size: 12px;'>* Exibindo {max_rows} de {len(df)} registros</p>"
        else:
            df_display = df
            nota = ""

        # Converter para HTML
        html_table = df_display.to_html(index=False, border=0, classes='tabela')

        return f"""
        <h3 class="titulo-secao">{titulo}</h3>
        {html_table}
        {nota}
        """

    def testar_conexao(self) -> bool:
        """
        Testa conexão SMTP

        Returns:
            True se conectou com sucesso
        """
        try:
            logger.info(f"Testando conexão SMTP: {self.smtp_server}:{self.smtp_port}")

            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)

            logger.info("Conexão SMTP testada com sucesso!")
            return True

        except smtplib.SMTPAuthenticationError:
            logger.error("Erro de autenticação - usuário ou senha incorretos")
            return False
        except Exception as e:
            logger.error(f"Erro ao testar conexão: {e}")
            return False


def enviar_alerta_simples(destinatarios: List[str],
                          resultado_analise: Dict,
                          analyzer,
                          smtp_config: Dict) -> bool:
    """
    Função auxiliar para envio rápido de alerta

    Args:
        destinatarios: Lista de e-mails
        resultado_analise: Resultado da análise
        analyzer: Instância de RecargaAnalyzer
        smtp_config: Dict com config SMTP (server, port, user, password)

    Returns:
        True se enviou com sucesso
    """
    try:
        # Criar sender
        sender = EmailSender(
            smtp_server=smtp_config['server'],
            smtp_port=smtp_config['port'],
            smtp_user=smtp_config['user'],
            smtp_password=smtp_config['password']
        )

        # Gerar tabelas
        tabela_resumo = analyzer.gerar_tabela_resumo()
        tabela_codigos = analyzer.gerar_tabela_codigos()
        tabela_negadas = analyzer.gerar_tabela_negadas()
        ranking_negadas = analyzer.gerar_ranking_negadas()
        ranking_n2 = analyzer.gerar_ranking_n2()

        nivel_alarme = resultado_analise.get('nivel_alarme', 'Alerta')

        # Enviar
        return sender.enviar_alerta(
            destinatarios=destinatarios,
            resultado_analise=resultado_analise,
            tabela_resumo=tabela_resumo,
            tabela_codigos=tabela_codigos,
            tabela_negadas=tabela_negadas,
            ranking_negadas=ranking_negadas,
            ranking_n2=ranking_n2,
            nivel_alarme=nivel_alarme
        )

    except Exception as e:
        logger.error(f"Erro ao enviar alerta: {e}")
        return False
