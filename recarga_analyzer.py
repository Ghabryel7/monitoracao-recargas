"""
Módulo de Análise de Recargas e Alarmística
Processa arquivos Excel de transações e detecta anomalias
"""

import os
import logging
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)


class RecargaAnalyzer:
    """
    Analisa relatórios de recargas e detecta situações de alarme

    Níveis de Alarme:
    - Alerta: ≥10% de recargas negadas (qualquer tipo)
    - Crítico: ≥10% de recargas com código N2 (erro no servidor)

    Análise feita em janelas de 30 minutos
    """

    def __init__(self, threshold_negadas: float = 10.0, threshold_n2: float = 10.0, periodo_texto: str = None):
        """
        Inicializa o analisador

        Args:
            threshold_negadas: Percentual mínimo de negadas para Alerta (padrão: 10%)
            threshold_n2: Percentual mínimo de N2 para Crítico (padrão: 10%)
            periodo_texto: Texto descritivo do período analisado
        """
        self.threshold_negadas = threshold_negadas
        self.threshold_n2 = threshold_n2
        self.periodo_texto = periodo_texto or "Período não especificado"
        self.df = None
        self.resultado_analise = {}

    def carregar_arquivo(self, caminho_arquivo: str) -> bool:
        """
        Carrega arquivo Excel de transações

        Args:
            caminho_arquivo: Caminho completo do arquivo

        Returns:
            True se carregou com sucesso, False caso contrário
        """
        try:
            if not os.path.exists(caminho_arquivo):
                logger.error(f"Arquivo não encontrado: {caminho_arquivo}")
                return False

            # Ler Excel com header na linha 2 (índice 2)
            self.df = pd.read_excel(caminho_arquivo, header=2)

            # Validar colunas necessárias
            colunas_necessarias = ['Estado Transação', 'Cod Resp', 'Origem', 'Telefone', 'Valor']
            for coluna in colunas_necessarias:
                if coluna not in self.df.columns:
                    logger.error(f"Coluna necessária não encontrada: {coluna}")
                    return False

            # Converter Data/Hora Origem para datetime
            if 'Data/Hora Origem' in self.df.columns:
                self.df['Data/Hora Origem'] = pd.to_datetime(
                    self.df['Data/Hora Origem'],
                    format="%d/%m/%Y %H:%M:%S",
                    errors='coerce'
                )

            logger.info(f"Arquivo carregado: {len(self.df)} transações")
            return True

        except Exception as e:
            logger.error(f"Erro ao carregar arquivo: {e}")
            return False

    def analisar(self) -> Dict:
        """
        Realiza análise completa das transações

        Returns:
            Dicionário com resultados da análise
        """
        if self.df is None or len(self.df) == 0:
            logger.error("Nenhum dado carregado para análise")
            return {}

        try:
            total = len(self.df)

            # Análise de recargas negadas (APENAS por Estado Transação para evitar duplicação)
            # Considera qualquer estado que contenha "Negada" (Negada Servidor, Negada Timeout, Negada Terminal, etc.)
            negadas_mask = self.df['Estado Transação'].astype(str).str.contains('Negada', case=False, na=False)
            negadas = self.df[negadas_mask]
            qtd_negadas = len(negadas)
            perc_negadas = (qtd_negadas / total) * 100

            # Análise de código N2 (erro servidor) - Filtrado DIRETAMENTE do DataFrame original
            # N2 geralmente corresponde a "Negada Servidor", mas filtramos pelo código para precisão
            n2_mask = self.df['Cod Resp'].astype(str) == 'N2'
            n2_transacoes = self.df[n2_mask]
            qtd_n2 = len(n2_transacoes)
            perc_n2 = (qtd_n2 / total) * 100

            # Análise de códigos de resposta
            cod_resp_counts = self.df['Cod Resp'].value_counts()

            # Análise de estados
            estado_counts = self.df['Estado Transação'].value_counts()

            # Determinar nível de alarme
            nivel_alarme = self._determinar_nivel_alarme(perc_negadas, perc_n2)

            # Montar resultado
            self.resultado_analise = {
                'total_transacoes': total,
                'transacoes_efetuadas': len(self.df[~negadas_mask]),
                'transacoes_negadas': qtd_negadas,
                'percentual_negadas': round(perc_negadas, 2),
                'transacoes_n2': qtd_n2,
                'percentual_n2': round(perc_n2, 2),
                'nivel_alarme': nivel_alarme,
                'detalhes_codigos': cod_resp_counts.to_dict(),
                'detalhes_estados': estado_counts.to_dict(),
                'timestamp_analise': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'periodo_analise': self.periodo_texto,
                'df_negadas': negadas,
                'df_n2': n2_transacoes
            }

            logger.info(f"Análise concluída: {total} transações, "
                       f"{perc_negadas:.2f}% negadas, "
                       f"{perc_n2:.2f}% N2, "
                       f"Alarme: {nivel_alarme}")

            return self.resultado_analise

        except Exception as e:
            logger.error(f"Erro durante análise: {e}")
            return {}

    def _determinar_nivel_alarme(self, perc_negadas: float, perc_n2: float) -> str:
        """
        Determina o nível de alarme baseado nos percentuais

        Args:
            perc_negadas: Percentual de transações negadas
            perc_n2: Percentual de transações com código N2

        Returns:
            'Crítico', 'Alerta' ou 'Normal'
        """
        # Crítico tem prioridade (problema crítico no servidor)
        if perc_n2 >= self.threshold_n2:
            return 'Crítico'

        # Alerta para percentual alto de negadas em geral
        if perc_negadas >= self.threshold_negadas:
            return 'Alerta'

        return 'Normal'

    def gerar_tabela_resumo(self) -> pd.DataFrame:
        """
        Gera tabela resumo para o e-mail

        Returns:
            DataFrame com resumo das métricas
        """
        if not self.resultado_analise:
            return pd.DataFrame()

        resumo = pd.DataFrame([
            {
                'Métrica': 'Total de Transações',
                'Valor': self.resultado_analise['total_transacoes']
            },
            {
                'Métrica': 'Recargas Efetuadas',
                'Valor': f"{self.resultado_analise['transacoes_efetuadas']} ({100 - self.resultado_analise['percentual_negadas']:.2f}%)"
            },
            {
                'Métrica': 'Recargas Negadas',
                'Valor': f"{self.resultado_analise['transacoes_negadas']} ({self.resultado_analise['percentual_negadas']:.2f}%)"
            },
            {
                'Métrica': 'Recargas com Erro N2 (Servidor)',
                'Valor': f"{self.resultado_analise['transacoes_n2']} ({self.resultado_analise['percentual_n2']:.2f}%)"
            },
            {
                'Métrica': 'Nível de Alarme',
                'Valor': self.resultado_analise['nivel_alarme']
            }
        ])

        return resumo

    def gerar_tabela_codigos(self, top_n: int = 10) -> pd.DataFrame:
        """
        Gera tabela com distribuição de códigos de resposta

        Args:
            top_n: Quantidade de códigos a mostrar

        Returns:
            DataFrame com códigos e suas frequências
        """
        if not self.resultado_analise:
            return pd.DataFrame()

        codigos = self.resultado_analise['detalhes_codigos']
        total = self.resultado_analise['total_transacoes']

        tabela = []
        for codigo, qtd in list(codigos.items())[:top_n]:
            perc = (qtd / total) * 100
            descricao = self._get_descricao_codigo(codigo)
            tabela.append({
                'Código': codigo,
                'Quantidade': qtd,
                'Percentual': f"{perc:.2f}%",
                'Descrição': descricao
            })

        return pd.DataFrame(tabela)

    def gerar_tabela_negadas(self, limit: int = None) -> pd.DataFrame:
        """
        Gera tabela com recargas negadas (TODAS)

        Args:
            limit: Quantidade máxima de linhas (None = sem limite, mostra todas)

        Returns:
            DataFrame com recargas negadas
        """
        if not self.resultado_analise or self.resultado_analise.get('df_negadas') is None:
            return pd.DataFrame()

        df_negadas = self.resultado_analise['df_negadas']

        if len(df_negadas) == 0:
            return pd.DataFrame()

        # Selecionar colunas relevantes
        colunas = ['Origem', 'Telefone', 'Valor', 'Estado Transação', 'Cod Resp', 'Data/Hora Origem']

        # Se limit for None ou não especificado, retorna todas as linhas
        if limit is None:
            df_resultado = df_negadas[colunas].copy()
        else:
            df_resultado = df_negadas[colunas].head(limit).copy()

        return df_resultado

    def gerar_ranking_negadas(self, top_n: int = 10) -> pd.DataFrame:
        """
        Gera ranking de origens com mais RECARGAS NEGADAS (todas)

        Args:
            top_n: Quantidade de origens a mostrar

        Returns:
            DataFrame com ranking de todas as recargas negadas
        """
        if not self.resultado_analise or self.resultado_analise.get('df_negadas') is None:
            return pd.DataFrame()

        df_negadas = self.resultado_analise['df_negadas']

        if len(df_negadas) == 0:
            return pd.DataFrame()

        # Contar total de negadas por origem
        negadas_por_origem = df_negadas['Origem'].value_counts()

        # Criar DataFrame de ranking
        ranking = pd.DataFrame({
            'Origem': negadas_por_origem.index,
            'Total Negadas': negadas_por_origem.values
        })

        # Ordenar por total negadas
        ranking = ranking.sort_values('Total Negadas', ascending=False).head(top_n)

        # Resetar índice
        ranking = ranking.reset_index(drop=True)
        ranking.index = ranking.index + 1  # Começar do 1

        return ranking

    def gerar_ranking_n2(self, top_n: int = 10) -> pd.DataFrame:
        """
        Gera ranking de origens com mais erros N2 (Erro Servidor)
        Filtra DIRETAMENTE do DataFrame original pela coluna 'Cod Resp'

        Args:
            top_n: Quantidade de origens a mostrar

        Returns:
            DataFrame com ranking específico de N2
        """
        if self.df is None or len(self.df) == 0:
            return pd.DataFrame()

        # Filtrar N2 diretamente do DataFrame original (não do df_negadas)
        # Isso evita qualquer possível duplicação ou inconsistência
        df_n2 = self.df[self.df['Cod Resp'].astype(str) == 'N2']

        if len(df_n2) == 0:
            return pd.DataFrame()

        # Contar N2 por origem
        n2_por_origem = df_n2['Origem'].value_counts()

        # Criar DataFrame de ranking
        ranking = pd.DataFrame({
            'Origem': n2_por_origem.index,
            'Total N2': n2_por_origem.values
        })

        # Ordenar por total N2
        ranking = ranking.sort_values('Total N2', ascending=False).head(top_n)

        # Resetar índice
        ranking = ranking.reset_index(drop=True)
        ranking.index = ranking.index + 1  # Começar do 1

        return ranking

    def gerar_tabela_hora_a_hora(self) -> pd.DataFrame:
        """
        Gera tabela com breakdown hora a hora (igual ao projeto_apoio)

        Returns:
            DataFrame com estatísticas por hora
        """
        if self.df is None or len(self.df) == 0:
            return pd.DataFrame()

        try:
            # Criar coluna de hora
            df_copy = self.df.copy()
            df_copy['hora_hh'] = df_copy['Data/Hora Origem'].dt.strftime('%H')

            # Criar pivot table
            tabela_hora = pd.pivot_table(
                df_copy,
                index='hora_hh',
                columns='Estado Transação',
                values='Origem',
                aggfunc='count',
                fill_value=0
            )

            # Adicionar total geral
            tabela_hora['Total Geral'] = tabela_hora.sum(axis=1)

            # Calcular total negadas
            colunas_negadas = [col for col in tabela_hora.columns if 'Negada' in col or col == 'Pendente']
            if colunas_negadas:
                tabela_hora['Total Negadas'] = tabela_hora[colunas_negadas].sum(axis=1)
            else:
                tabela_hora['Total Negadas'] = 0

            # Calcular percentual de negadas
            tabela_hora['% Negadas'] = (tabela_hora['Total Negadas'] / tabela_hora['Total Geral'] * 100).round(2)

            # Adicionar linha de totais
            totais = tabela_hora.sum(numeric_only=True)
            totais['% Negadas'] = (totais['Total Negadas'] / totais['Total Geral'] * 100).round(2)

            # Criar DataFrame de totais
            totais_row = pd.DataFrame([totais], index=['Total Geral'])

            # Resetar índice e concatenar
            tabela_hora.index.name = 'Hora'
            tabela_hora = tabela_hora.reset_index()

            totais_row = totais_row.reset_index()
            totais_row.columns = tabela_hora.columns

            tabela_hora = pd.concat([tabela_hora, totais_row], ignore_index=True)

            return tabela_hora

        except Exception as e:
            logger.error(f"Erro ao gerar tabela hora a hora: {e}")
            return pd.DataFrame()

    def _get_descricao_codigo(self, codigo: str) -> str:
        """
        Retorna descrição do código de resposta

        Args:
            codigo: Código de resposta

        Returns:
            Descrição do código
        """
        descricoes = {
            '00': 'Transação aprovada',
            'N1': 'Negada - Timeout',
            'N2': 'Negada - Erro no servidor',
            '86': 'Negada - Terminal',
            '30': 'Negada - Erro de formato',
            '51': 'Negada - Saldo insuficiente',
            '96': 'Negada - Erro no sistema'
        }

        return descricoes.get(str(codigo), 'Código desconhecido')

    def tem_alarme(self) -> bool:
        """
        Verifica se há situação de alarme

        Returns:
            True se houver Alerta ou Crítico
        """
        if not self.resultado_analise:
            return False

        return self.resultado_analise.get('nivel_alarme', 'Normal') in ['Alerta', 'Crítico']

    def get_mensagem_alarme(self) -> str:
        """
        Retorna mensagem descritiva do alarme

        Returns:
            Mensagem do alarme
        """
        if not self.resultado_analise:
            return "Nenhuma análise realizada"

        nivel = self.resultado_analise.get('nivel_alarme', 'Normal')
        perc_negadas = self.resultado_analise.get('percentual_negadas', 0)
        perc_n2 = self.resultado_analise.get('percentual_n2', 0)

        if nivel == 'Crítico':
            return (f"🚨 CRÍTICO: {perc_n2:.2f}% das recargas estão com erro N2 (Problema no Servidor). "
                   f"Threshold: {self.threshold_n2}%. Ação imediata necessária!")

        elif nivel == 'Alerta':
            return (f"⚠️ ALERTA: {perc_negadas:.2f}% das recargas foram negadas. "
                   f"Threshold: {self.threshold_negadas}%. Necessário entender o problema.")

        else:
            return f"✅ Status Normal: {perc_negadas:.2f}% negadas, {perc_n2:.2f}% N2"


def analisar_arquivo(caminho_arquivo: str,
                     threshold_negadas: float = 10.0,
                     threshold_n2: float = 10.0) -> Tuple[bool, Dict, str]:
    """
    Função auxiliar para análise rápida de um arquivo

    Args:
        caminho_arquivo: Caminho do arquivo Excel
        threshold_negadas: Threshold para Alerta
        threshold_n2: Threshold para Crítico

    Returns:
        Tupla (tem_alarme, resultado_analise, mensagem)
    """
    analyzer = RecargaAnalyzer(threshold_negadas, threshold_n2)

    if not analyzer.carregar_arquivo(caminho_arquivo):
        return False, {}, "Erro ao carregar arquivo"

    resultado = analyzer.analisar()
    tem_alarme = analyzer.tem_alarme()
    mensagem = analyzer.get_mensagem_alarme()

    return tem_alarme, resultado, mensagem
