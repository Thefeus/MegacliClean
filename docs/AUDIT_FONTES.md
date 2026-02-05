# Auditoria de Fontes do Projeto MegaCLI

**Data:** 04/02/2026
**Objetivo:** Conferência entre estrutura física e Mapa de Fontes (`config/fontes.py`).

---

## 📂 1. Estrutura Física vs. Mapa de Fontes

Legenda:
- ✅ : Registrado em `config/fontes.py`
- ❌ : **NÃO** Registrado (Candidato a inclusão)

### Diretorios Principais

#### `src/`
- [x] `megacli.py` (Entry point, usa fontes)
- [✅] `src/menu_interativo.py`

#### `src/core/`
- [✅] `analisador_9_numeros.py`
- [✅] `analisador_universo_reduzido.py`
- [✅] `analise_params.py`
- [✅] `ciclo_refinamento_ia.py`
- [✅] `conexao_ia.py`
- [✅] `config.py`
- [❌] `filtros_avancados.py`
- [✅] `gerador_jogos_top10.py`
- [✅] `metricas_confianca.py`
- [✅] `modo_conservador.py`
- [✅] `paths.py`
- [✅] `previsao_30n.py`
- [❌] `seletor_universo_inteligente.py`
- [❌] `sistema_refinamento.py`
- [❌] `sistema_voto.py`
- [✅] `visualizacao_graficos.py`

#### `src/validacao/`
- [✅] `analisador_historico.py`
- [✅] `analise_correlacao.py`
- [✅] `detector_overfitting.py`
- [✅] `ranking_indicadores.py`
- [✅] `validador_1000_jogos.py`
- [✅] `validador_train_test.py`
- [❌] `backtest_comparativo.py`
- [❌] `validacao_continua.py`
- [❌] `validador_ciclo.py`
- [❌] `validador_retroativo.py`
- [❌] `validador_retroativo_v2.py`
- [❌] `validador_retroativo_v2_completo.py`
- [❌] `estrategias_previsao.py`

#### `src/utils/`
- [✅] `export_jogos_top9.py`
- [✅] `indicador_otimizado_10n.py`
- [✅] `sistema_exportacao.py`
- [❌] `advanced_ml.py`
- [❌] `consultar_ia_refinamento.py`
- [❌] `debug_api_key.py`
- [❌] `descricoes_indicadores.py`
- [❌] `detector_colunas.py`
- [❌] `exportador_excel.py`
- [❌] `feature_engineer.py`
- [❌] `finalizar_projeto.py`
- [❌] `frequencia_minima.py`
- [❌] `funcoes_principais.py`
- [❌] `gerador_otimizado_v2.py`
- [❌] `indicador_base.py`
- [❌] `indicador_ciclos.py`
- [❌] `indicador_otimizado_20n.py`
- [❌] `indicador_otimizado_9n.py`
- [❌] `indicador_padrao_delta.py`
- [❌] `indicadores_avancados.py`
- [❌] `indicadores_basicos.py`
- [❌] `indicadores_extras.py`
- [❌] `indicadores_frequencia.py`
- [❌] `indicadores_geometricos.py`
- [❌] `indicadores_ia.py`
- [❌] `indicadores_ml.py`
- [❌] `indicadores_numerologicos.py`
- [❌] `indicadores_temporais.py`
- [❌] `limpar_documentos.py`
- [❌] `logger_estruturado.py`
- [❌] `mapear_e_limpar_python.py`
- [❌] `otimizador_parametros.py`
- [❌] `padroes_emergentes.py`
- [❌] `preprocessamento.py`
- [❌] `project_structure.py`
- [❌] `relatorio_tecnico.py`
- [❌] `testar_importacao.py`
- [❌] `utils.py`

---

## 🔍 2. Análise Detalhada de Imports (Amostra)

### `src/utils/sistema_exportacao.py`
**Imports:**
```python
import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Font, Alignment
from openpyxl.utils.dataframe import dataframe_to_rows
from datetime import datetime
```

### `src/validacao/estrategias_previsao.py`
**Imports:**
```python
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from collections import Counter
import time
import os
from dotenv import load_dotenv
```

### `src/validacao/validador_ciclo.py`
**Imports:**
```python
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, Optional
import json
from datetime import datetime
```

### `src/utils/debug_api_key.py`
**Imports:**
```python
import unittest
import os
import dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
```

---

## 🚀 3. Plano de Ação

Para garantir que "todos os fontes" estejam no arquivo `fontes.py`, é necessário adicionar os arquivos marcados com ❌.

**Arquivos a Adicionar em `config/fontes.py`:**

1.  **Core Extras:**
    - `filtros_avancados`
    - `seletor_universo_inteligente`
    - `sistema_refinamento`
    - `sistema_voto`

2.  **Validação Extras:**
    - `backtest_comparativo`
    - `validacao_continua`
    - `validador_ciclo`
    - `validador_retroativo_v2_completo` (Versão mais completa)
    - `estrategias_previsao`

3.  **Utils Extras:**
    - `exportador_excel`
    - `limpar_documentos`
    - `utils` (Genérico)
    - `indicadores_*` (Agrupamento sugerido: INDICADORES)

Esta ação centralizará definitivamente todos os recursos do projeto.
