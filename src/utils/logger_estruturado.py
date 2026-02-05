"""
Logger Estruturado para MegaCLI

Sistema de logging em JSON para rastreabilidade completa.
- Logs estruturados em formato JSON
- Níveis: DEBUG, INFO, WARNING, ERROR
- Rotação automática (últimos 30 dias)
- Queries facilitadas
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import re


class LoggerEstruturado:
    """Logger que salva eventos estruturados em JSON"""
    
    def __init__(self, nome_modulo: str, diretorio_logs: str = "logs"):
        self.nome_modulo = nome_modulo
        self.diretorio_logs = Path(diretorio_logs)
        self.diretorio_logs.mkdir(exist_ok=True)
        
        # Arquivo do dia atual
        self.arquivo_atual = self._get_arquivo_dia()
        
        # Limpar logs antigos
        self._limpar_logs_antigos()
    
    def _get_arquivo_dia(self) -> Path:
        """Retorna arquivo de log do dia atual"""
        data_hoje = datetime.now().strftime("%Y-%m-%d")
        return self.diretorio_logs / f"execucao_{data_hoje}.jsonl"
    
    def _limpar_logs_antigos(self, dias_manter: int = 30):
        """Remove logs mais antigos que N dias"""
        data_limite = datetime.now() - timedelta(days=dias_manter)
        
        for arquivo in self.diretorio_logs.glob("execucao_*.jsonl"):
            # Extrair data do nome do arquivo
            match = re.search(r'execucao_(\d{4}-\d{2}-\d{2})\.jsonl', arquivo.name)
            if match:
                try:
                    data_arquivo = datetime.strptime(match.group(1), "%Y-%m-%d")
                    if data_arquivo < data_limite:
                        arquivo.unlink()
                        print(f"Log removido: {arquivo.name}")
                except:
                    pass
    
    def _log(self, nivel: str, evento: str, dados: Optional[Dict[str, Any]] = None):
        """Registra evento no log"""
        # Atualizar arquivo se mudou o dia
        arquivo_dia = self._get_arquivo_dia()
        if arquivo_dia != self.arquivo_atual:
            self.arquivo_atual = arquivo_dia
        
        # Criar entrada de log
        entrada = {
            "timestamp": datetime.now().isoformat(),
            "nivel": nivel,
            "modulo": self.nome_modulo,
            "evento": evento
        }
        
        if dados:
            entrada["dados"] = dados
        
        # Salvar em arquivo (JSONL - uma linha por evento)
        with open(self.arquivo_atual, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entrada, ensure_ascii=False) + '\n')
    
    def debug(self, evento: str, dados: Optional[Dict] = None):
        """Log nível DEBUG"""
        self._log("DEBUG", evento, dados)
    
    def info(self, evento: str, dados: Optional[Dict] = None):
        """Log nível INFO"""
        self._log("INFO", evento, dados)
    
    def warning(self, evento: str, dados: Optional[Dict] = None):
        """Log nível WARNING"""
        self._log("WARNING", evento, dados)
    
    def error(self, evento: str, dados: Optional[Dict] = None):
        """Log nível ERROR"""
        self._log("ERROR", evento, dados)
    
    def registrar_execucao(self, 
                          inicio: datetime,
                          fim: datetime,
                          sorteios_analisados: int,
                          jogos_gerados: int,
                          indicadores_ativos: int,
                          custo_api: float = 0.0):
        """Registra execução completa do sistema"""
        tempo_total = (fim - inicio).total_seconds()
        
        self.info("execucao_concluida", {
            "inicio": inicio.isoformat(),
            "fim": fim.isoformat(),
            "tempo_segundos": round(tempo_total, 2),
            "sorteios_analisados": sorteios_analisados,
            "jogos_gerados": jogos_gerados,
            "indicadores_ativos": indicadores_ativos,
            "custo_api_usd": custo_api,
            "sucesso": True
        })
    
    def registrar_metricas(self, metricas: Dict[str, Any]):
        """Registra métricas de performance"""
        self.info("metricas_performance", metricas)
    
    def registrar_erro_execucao(self, erro: str, detalhes: Optional[Dict] = None):
        """Registra erro durante execução"""
        dados_erro = {"mensagem": erro}
        if detalhes:
            dados_erro.update(detalhes)
        
        self.error("execucao_falhou", dados_erro)


# ============================================================================
# ANALISADOR DE LOGS
# ============================================================================

class AnalisadorLogs:
    """Analisa logs estruturados para gerar insights"""
    
    def __init__(self, diretorio_logs: str = "logs"):
        self.diretorio_logs = Path(diretorio_logs)
    
    def carregar_logs(self, data_inicio: Optional[datetime] = None, 
                      data_fim: Optional[datetime] = None) -> list:
        """Carrega logs de um período"""
        logs = []
        
        for arquivo in sorted(self.diretorio_logs.glob("execucao_*.jsonl")):
            # Filtrar por data se necessário
            if data_inicio or data_fim:
                match = re.search(r'execucao_(\d{4}-\d{2}-\d{2})\.jsonl', arquivo.name)
                if match:
                    data_arquivo = datetime.strptime(match.group(1), "%Y-%m-%d")
                    if data_inicio and data_arquivo < data_inicio:
                        continue
                    if data_fim and data_arquivo > data_fim:
                        continue
            
            # Ler arquivo
            with open(arquivo, 'r', encoding='utf-8') as f:
                for linha in f:
                    try:
                        logs.append(json.loads(linha))
                    except:
                        pass
        
        return logs
    
    def gerar_resumo(self, ultimos_dias: int = 7) -> Dict[str, Any]:
        """Gera resumo dos últimos N dias"""
        data_inicio = datetime.now() - timedelta(days=ultimos_dias)
        logs = self.carregar_logs(data_inicio=data_inicio)
        
        # Contar eventos por tipo
        eventos = {}
        erros = 0
        execucoes_sucesso = 0
        tempo_total = 0
        custo_total = 0
        
        for log in logs:
            evento = log.get("evento", "desconhecido")
            eventos[evento] = eventos.get(evento, 0) + 1
            
            if log.get("nivel") == "ERROR":
                erros += 1
            
            if evento == "execucao_concluida":
                dados = log.get("dados", {})
                if dados.get("sucesso"):
                    execucoes_sucesso += 1
                    tempo_total += dados.get("tempo_segundos", 0)
                    custo_total += dados.get("custo_api_usd", 0)
        
        return {
            "periodo": f"Últimos {ultimos_dias} dias",
            "total_eventos": len(logs),
            "eventos_por_tipo": eventos,
            "execucoes_sucesso": execucoes_sucesso,
            "execucoes_erro": erros,
            "tempo_medio_segundos": round(tempo_total / max(execucoes_sucesso, 1), 2),
            "custo_total_usd": round(custo_total, 2)
        }
    
    def exportar_metricas(self, output_file: str = "logs/metricas_resumo.json"):
        """Exporta resumo de métricas"""
        resumo = self.gerar_resumo(30)  # Últimos 30 dias
        
        output_path = Path(output_file)
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(resumo, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Métricas exportadas: {output_path}")


# ============================================================================
# EXEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    # Criar logger
    logger = LoggerEstruturado("gerar_analise_completa")
    
    # Simular execução
    inicio = datetime.now()
    
    logger.info("analise_iniciada", {
        "sorteios_total": 2954,
        "indicadores": 21
    })
    
    logger.debug("carregando_historico", {"arquivo": "MEGA_SENA.xlsx"})
    logger.info("historico_carregado", {"linhas": 2954})
    
    logger.info("consultando_ia", {"modelo": "gemini-1.5-flash"})
    logger.info("ia_respondeu", {"tokens_usados": 450, "custo_usd": 0.05})
    
    # Registrar execução completa
    fim = datetime.now()
    logger.registrar_execucao(
        inicio=inicio,
        fim=fim,
        sorteios_analisados=2954,
        jogos_gerados=84,
        indicadores_ativos=21,
        custo_api=0.05
    )
    
    # Analisar logs
    print("\n" + "="*70)
    print("ANÁLISE DE LOGS")
    print("="*70)
    
    analisador = AnalisadorLogs()
    resumo = analisador.gerar_resumo(7)
    
    print(f"\n{resumo['periodo']}:")
    print(f"  Total eventos: {resumo['total_eventos']}")
    print(f"  Execuções sucesso: {resumo['execucoes_sucesso']}")
    print(f"  Tempo médio: {resumo['tempo_medio_segundos']}s")
    print(f"  Custo total: ${resumo['custo_total_usd']}")
    
    # Exportar
    analisador.exportar_metricas()
