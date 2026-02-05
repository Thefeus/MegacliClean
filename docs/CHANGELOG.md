# MegaCLI - Changelog

## [6.3.0] - 04/02/2026

### 🎉 Consolidação e Estabilização
- **Versão Unificada**: Alinhamento de versão em todo o sistema (código e documentação).
- **Refinamento do Modo Conservador**: Otimizações na geração e validação.
- **Documentação Completa**: Guia operacional detalhado no README.

---

## [6.2.0] - 02/02/2026

### 🎉 Melhorias Estatísticas e Anti-Overfitting

### ✨ Adicionado
- **Métricas de Confiança Estatística**
  - Intervalos de confiança (IC 95%) em todas as métricas
  - Cálculo de margem de erro com distribuição t-Student
  - Análise de consistência (coeficiente de variação)
  - Testes de significância estatística (t-test)

- **Validação Train/Test Rigorosa**
  - Split 80/20 para treino e teste
  - Métricas separadas para cada conjunto
  - Cálculo de degradação de performance
  - Detecção de generalização vs overfitting

- **Detector Automático de Overfitting**
  - Análise multi-critério
  - Alertas coloridos por nível de risco (BAIXO/MÉDIO/ALTO)
  - Recomendações automáticas
  - Thresholds configuráveis

- **Modo Conservador (Opção 12)**
  - Usa apenas 5-7 indicadores robustos
  - Universo mínimo de 25 números
  - Validação cruzada obrigatória
  - Gera 100 jogos (menor custo)
  - Relatórios com intervalos de confiança
  - Gera TOP 20, TOP 15, TOP 10 e TOP 9 números 🆕
  - **Geração automática de 84 jogos TOP 9** 🆕
  - **Análise de correlação TOP 9 vs sorteios reais** 🆕
  - **Visualizações gráficas automáticas** 🆕
    - Gráfico TOP 20 com scores
    - Heatmap completo 6x10
    - Histórico de acertos
    - Distribuição TOP 9
  - Calcula score médio para cada nível
  - Export automático de jogos TOP 9 em TXT
  - Dicas de apostas baseadas em probabilidade

- **Módulos novos**:
  - `src/core/metricas_confianca.py`
  - `src/validacao/validador_train_test.py`
  - `src/validacao/detector_overfitting.py`
  - `src/core/modo_conservador.py`

### 🔧 Alterado
- Menu atualizado para v6.2
- Opção 11 agora mostra intervalos de confiança
- Versão atualizada em megacli.py e menu_interativo.py

### 📚 Documentação
- Plano de implementação completo das melhorias
- Guia de interpretação estatística

---

## [6.1.0] - 02/02/2026

### 🎉 Novidades Principais
**Sistema de Auto-Aprendizado Inteligente com IA**

### ✨ Adicionado
- **Opção 11 v2.0**: Sistema completo de validação retroativa e auto-aprendizado
  - Validação multi-nível (TOP 30, 20, 10, 9)
  - Consulta à IA para análise de indicadores
  - Reavaliação probabilística: "E se tivéssemos usado os indicadores da IA?"
  - Análise de grupos de indicadores ótimos
  - Atualização automática do Excel (aba VALIDACAO_RETROATIVA)

- **Módulos novos**:
  - `src/validacao/validador_retroativo_v2_completo.py` - Validador expandido
  - `src/validacao/analisador_grupos_indicadores.py` - Análise combinatória

- **Configuração de IA centralizada**:
  - `config/config.yaml`: Seção `ia` para configurar modelo
  - `src/core/conexao_ia.py`: Sistema inteligente de fallback (app_config.py → config.yaml → gemini-2.5-pro)
  - Suporte para Gemini 2.5 Pro como modelo padrão

### 🔧 Alterado
- Modelo IA padrão atualizado: `gemini-1.5-flash` → `gemini-2.5-pro`
- `src/app_config.py`: Atualizado para Gemini 2.5 Pro
- `src/menu_interativo.py`: Opção 11 expandida com novas funcionalidades
- Configuração do modelo IA agora centralizada (sem hardcode)

### 🐛 Corrigido
- Erro 404 ao usar modelo `gemini-2.0-flash-exp` (não disponível)
- Centralização de configuração do modelo IA em múltiplos arquivos

### 📚 Documentação
- Plano de implementação detalhado da Opção 11 v2.0
- Task.md atualizado com checklist de progresso
- Guia de configuração de modelo IA

---

## [5.1.5] - 22/01/2026
- Versão base estável antes das melhorias

---

## Legenda
- 🎉 Novidades Principais
- ✨ Adicionado
- 🔧 Alterado
- 🐛 Corrigido
- 🗑️ Removido
- 📚 Documentação
- ⚡ Performance
