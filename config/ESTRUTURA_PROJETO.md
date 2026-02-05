# Estrutura do Projeto MegaCLI

**Versão Documentada:** 6.3.0
**Data de Atualização:** 04/02/2026

Este documento reflete a organização atual dos arquivos e diretórios do projeto, após a reestruturação para centralização de fontes e limpeza da raiz.

## 📂 Diretório Raiz (`/`)

A raiz do projeto contém apenas os arquivos essenciais para execução e configuração de ambiente.

- `main.py`: Entry point simplificado. Execute `python main.py` para iniciar a aplicação.
- `requirements.txt`: Lista de dependências Python.
- `.gitignore`: Arquivos ignorados pelo Git.
- `Dados/`: Diretório de armazenamento de dados brutos (ex: planilhas históricas).
- `Resultado/`: Diretório de saída para logs, jogos gerados e relatórios.

## 📂 Código Fonte (`src/`)

Todo o código-fonte da aplicação reside aqui.

- `megacli.py`: Lógica principal de inicialização da CLI (chamado pelo `main.py`).
- `menu_interativo.py`: Interface de usuário do terminal.

### `src/core/`
Núcleo da lógica de negócio e configurações.

- `config.py`: Carregamento de configurações.
- `paths.py`: Gerenciamento de caminhos do sistema.
- `analise_params.py`: Definição de parâmetros de análise.
- `gerador_jogos_top10.py`: Lógica de geração de jogos.
- E outros módulos core...

### `src/validacao/`
Módulos responsáveis pela validação, backtesting e análise estatística.

- `validador_1000_jogos.py`: Validação contra histórico extenso.
- `ranking_indicadores.py`: Sistema de pontuação de estratégias.
- E outros módulos de validação...

### `src/utils/`
Utilitários gerais e exportadores.

- `sistema_exportacao.py`: Exportação para Excel/TXT.
- E outros scripts auxiliares...

## 📂 Configuração (`config/`)

Arquivos de configuração e mapeamento do sistema.

- `fontes.py`: **Source Map**. Registro central de todos os módulos. O sistema de imports utiliza este arquivo para desacoplar a estrutura física da lógica.
- `ESTRUTURA_PROJETO.md`: Este documento.
- `__init__.py`: Torna a pasta um pacote Python.

## 📂 Documentação (`docs/`)

Documentação geral do projeto.

- `AUDIT_FONTES.md`: Relatório de auditoria de arquivos Python.
- `CHANGELOG.md`: Histórico de mudanças.
- `INSTALL.md`: Guia de instalação.
- `GUIA_OPERACIONAL.md` (se existir).

---

## 🚀 Como Executar

A partir da raiz:

```bash
# Modo Interativo
python main.py

# Com argumentos
python main.py --gerar-jogos
python main.py --config
```

## 🔄 Fluxo de Imports

O projeto utiliza o padrão **Source Map** via `config/fontes.py`.
Em vez de importar `src.core.modulo`, preferir:

```python
from config.fontes import NOME_MODULO
```

Isso garante que, se arquivos forem movidos dentro de `src/`, apenas `config/fontes.py` precisa ser atualizado, sem quebrar o restante do código.
