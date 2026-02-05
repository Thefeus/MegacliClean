# MegaCLI - Sistema de Análise Mega-Sena

**Versão:** 6.3.0 - Clean Edition  
**Data:** Fevereiro 2026  
**Status:** 🏗️ Em Desenvolvimento Ativo

O **MegaCLI** é um sistema avançado de análise estatística e previsão para a Mega-Sena. Diferente de geradores aleatórios comuns, ele utiliza **Ciência de Dados** e **Estatística Rigorosa** para identificar padrões, validar hipóteses e sugerir jogos com base em intervalos de confiança e testes de significância.

---

## 🚀 Funcionalidades Principais

### 🧠 Inteligência Analítica
- **Modo Conservador (Anti-Overfitting)**: Utiliza apenas indicadores robustos (Soma, Pares, Primos, etc.) para evitar o "vício" nos dados de treino. Gera previsões focadas em consistência a longo prazo.
- **Análise Estatística Profunda**: Calcula desvio padrão, média, mediana e frequências para dezenas de métricas.
- **Intervalos de Confiança (IC 95%)**: Todas as métricas são acompanhadas de seus intervalos de confiança, permitindo avaliar se um desvio é apenas ruído ou uma tendência real.

### 🔮 Previsão e Geração
- **Dynamic Prediction (TOP 30N)**: O sistema gera um universo reduzido de 30 números com maior probabilidade estatística para o próximo concurso.
- **Refinamento Inteligente**: Filtra os TOP 30 para TOP 20, TOP 10 e TOP 9 (Elite), maximizando a densidade de acertos.
- **Geração Automática**: Cria jogos otimizados combinando os números selecionados.
- **Modo 11 - Validação Retroativa**: Permite "voltar no tempo" e testar se a estratégia teria funcionado no passado.

### 📊 Visualização e Validação
- **Gráficos Automáticos**: Gera heatmaps, histogramas e gráficos de dispersão para visualizar a distribuição dos números.
- **Split Train/Test**: Separa os dados em treino (80%) e teste (20%) para validar a real eficácia dos modelos, simulando um cenário real de previsão.
- **Detector de Overfitting**: Alerta se o modelo está apenas "decorando" o passado ou se realmente aprendeu padrões generalizáveis.

---

## 🛠️ Instalação

### Pré-requisitos
- Python 3.9 ou superior
- Git (opcional, para clonar)

### Passo a Passo

1. **Clone ou baixe o repositório**
   ```bash
   git clone https://github.com/SeuUsuario/MegaCLI.git
   cd MegaCLI_Clean
   ```

2. **Crie um ambiente virtual (Recomendado)**
   ```bash
   # Windows
   python -m venv env
   .\env\Scripts\activate

   # Linux/Mac
   python3 -m venv env
   source env/bin/activate
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verifique a instalação**
   ```bash
   python megacli.py --no-check
   ```

---

## 📖 Guia de Uso

O sistema pode ser operado via **Menu Interativo** (recomendado para exploração) ou **Linha de Comando** (para automação).

### Modo Interativo
Execute o comando abaixo e navegue pelas opções numéricas:
```bash
python megacli.py
```

#### Menu Principal - Destaques:
- **Opção 1**: Gerar Jogos (Rápido) - Gera 210 jogos baseados nos TOP indicadores.
- **Opção 3**: Análise Completa - Executa todo o pipeline: atualização, análise, geração e validação.
- **Opção 9**: Previsão Próximo Sorteio (TOP 30) - Foca apenas na previsão para o concurso futuro.
- **Opção 11**: Validação Retroativa - Testa suas estratégias no passado.
- **Opção 12**: **Modo Conservador** (💎 Recomendado) - A análise mais segura e robusta disponível.

### Linha de Comando (CLI)
Para usuários avançados ou scripts de automação:

```bash
# Gerar jogos automaticamente
python megacli.py --gerar-jogos

# Executar validação histórica
python megacli.py --validar

# Ver configurações atuais
python megacli.py --config
```

---

## 📂 Estrutura do Projeto

A organização do projeto segue uma arquitetura modular limpa:

```
D:\MegaCLI_Clean\
├── megacli.py                  # 🚀 Ponto de entrada (Main Entry Point)
├── config/                     # ⚙️ Configurações
│   └── config.yaml             # Parâmetros ajustáveis (IA, Análise, Limites)
├── Dados/                      # 💾 Armazenamento de dados
│   └── HISTORICO_MEGASENA.csv  # Base oficial de sorteios (Atualize periodicamente!)
├── Resultado/                  # 📤 Saída do sistema
│   ├── jogos_gerados_...txt    # Jogos prontos para jogar
│   ├── graficos/               # Visualizações geradas
│   └── relatorios/             # Análises detalhadas em Excel/JSON
└── src/                        # 🧠 Código Fonte (Core)
    ├── core/                   # Lógica central (Matemática e Estatística)
    │   ├── modo_conservador.py # Implementação do modo robusto
    │   ├── metricas_confianca.py
    │   └── ...
    ├── validacao/              # Módulos de teste e validação
    │   ├── detector_overfitting.py
    │   └── ...
    ├── menu_interativo.py      # Interface com o usuário
    └── utils/                  # Ferramentas auxiliares
```

---

## 🔬 Detalhes Técnicos

### O Modo Conservador (Opção 12)
Este é o diferencial do MegaCLI v6.3.0. Ele assume que "menos é mais".
1. **Seleção de Indicadores**: Em vez de usar 50+ filtros, ele seleciona apenas os 7 indicadores historicamente mais estáveis.
2. **Universo de 25 Números**: Reduz o universo de 60 para 25 números, aumentando drasticamente a probabilidade de acertar a quadra ou quina dentro desse subconjunto.
3. **Validação Cruzada**: Antes de te entregar os números, o sistema se "auto-desafia", testando se esses números teriam ganho nos últimos 200 concursos. Se não passar no teste, ele recalcula.

### Configuração (YAML)
Toda a inteligência do sistema é parametrizável em `config/config.yaml`. Você pode ajustar:
- **Janelas de Análise**: Quantos jogos passados olhar?
- **Níveis de Risco**: Ser mais agressivo ou conservador.
- **IA**: Configurações de conexão com LLMs (Gemini/OpenAI) para análises semânticas (se ativado).

---

## ⚠️ Aviso Legal
Este software é uma ferramenta de **análise estatística**. Loterias são jogos de azar e **não existe garantia de vitória**. O objetivo deste projeto é puramente educacional e científico, explorando a matemática por trás dos números aleatórios. Jogue com responsabilidade.

---

**Desenvolvido por:** Thefeus & MegaCLI Team  
**Licença:** MIT (Uso pessoal e educacional livre)
**Versão:** 6.3.0 - Clean Edition  
**Data:** Fevereiro 2026

Sistema inteligente para análise estatística e geração de jogos da Mega-Sena com abordagem científica rigorosa.

---

## 🎯 Funcionalidades Principais

### ✅ Análise Estatística Avançada
- **Intervalos de Confiança:** Métricas com significância estatística
- **Split Train/Test:** Validação rigorosa com dados separados
- **Detector de Overfitting:** Proteção contra sobre-ajuste

### ✅ Modo Conservador (v6.3)
- **Anti-Overfitting:** Geração baseada em TOP 9 números mais robustos
- **Geração Automática:** 84 jogos otimizados a partir dos TOP 9
- **Exportação Universal:** TXT, Excel e JSON

### ✅ Análise de Correlação Retroativa (v6.3)
- **Validação Histórica:** Análise de correlação com últimos 100 sorteios
- **Métricas de Performance:** Taxa de acerto, correlação média, overfitting score

### ✅ Visualizações Profissionais (v6.3)
- **Gráficos Interativos:** Distribuição de números, frequências, análises
- **Análise Visual:** Comparação de performance entre métodos

---

## 📋 Instalação Rápida

### Pré-requisitos
- Python 3.9 ou superior
- pip (gerenciador de pacotes Python)

### Passo a Passo

```bash
# 1. Navegue até o diretório
cd D:\MegaCLI_Clean

# 2. Crie ambiente virtual (recomendado)
python -m venv env

# 3. Ative o ambiente virtual
env\Scripts\activate

# 4. Instale as dependências
pip install -r requirements.txt

# 5. Execute o sistema
python megacli.py
```

---

## 🚀 Uso Rápido

### Menu Interativo

Execute `python megacli.py` e escolha uma opção:

**Principais Funcionalidades:**
- **Opção 12:** Modo Conservador (recomendado) - Análise anti-overfitting com TOP 9
- **Opção 4:** Análise de Correlação Retroativa
- **Visualizações:** Gráficos automáticos durante análises

### Exemplo: Modo Conservador

```bash
python megacli.py
# Escolha opção 12
# Os jogos serão gerados em Resultado/
```

**Arquivos Gerados:**
- `previsao_top9_YYYY-MM-DD_HH-MM-SS.txt` - Jogos em formato texto
- `previsao_top9_YYYY-MM-DD_HH-MM-SS.xlsx` - Planilha com análises
- `previsao_top9_YYYY-MM-DD_HH-MM-SS.json` - Dados estruturados
- Gráficos PNG com visualizações

---

## 📊 Estrutura do Projeto

```
D:\MegaCLI_Clean\
├── megacli.py                  # Entry point principal
├── requirements.txt            # Dependências
├── README.md                   # Este arquivo
├── CHANGELOG.md                # Histórico de versões
├── INSTALL.md                  # Guia detalhado de instalação
│
├── config/
│   └── config.yaml             # Configurações centralizadas
│
├── src/
│   ├── menu_interativo.py      # Interface do usuário
│   │
│   ├── core/                   # Módulos principais
│   │   ├── config.py
│   │   ├── previsao_30n.py
│   │   ├── gerador_jogos_top10.py
│   │   ├── metricas_confianca.py
│   │   ├── modo_conservador.py
│   │   └── visualizacao_graficos.py
│   │
│   ├── validacao/              # Validadores
│   │   ├── validador_train_test.py
│   │   ├── detector_overfitting.py
│   │   ├── analise_correlacao.py
│   │   └── validador_historico_100.py
│   │
│   └── utils/                  # Utilitários
│       └── export_jogos_top9.py
│
├── Dados/
│   └── HISTORICO_MEGASENA.csv  # Base de dados histórica
│
└── Resultado/                  # Saídas geradas
    └── exemplos/               # Exemplos de saída
```

---

## 🔬 Metodologia Científica

### Validação Rigorosa
- **Train/Test Split:** 80% treino / 20% teste
- **Validação Cruzada:** Múltiplas janelas temporais
- **Intervalos de Confiança:** 95% de confiança estatística

### Anti-Overfitting
- **Detector Automático:** Identifica sobre-ajuste
- **Modo Conservador:** Usa apenas números mais robustos (TOP 9)
- **Análise Retroativa:** Validação com dados históricos

### Métricas de Qualidade
- **Taxa de Acerto:** Percentual de números corretos
- **Correlação Média:** Força da relação estatística
- **Overfitting Score:** Indicador de generalização

---

## 📦 Dependências Principais

- **pandas:** Manipulação de dados
- **numpy:** Computação numérica
- **matplotlib:** Visualizações
- **scipy:** Análises estatísticas
- **openpyxl:** Geração de planilhas Excel

Veja lista completa em `requirements.txt`

---

## 📝 Changelog

### v6.3.0 (Fevereiro 2026)
- ✅ Modo Conservador com TOP 9
- ✅ Análise de correlação retroativa
- ✅ Visualizações gráficas profissionais
- ✅ Exportação universal (TXT/Excel/JSON)

### v6.2.0 (Janeiro 2026)
- ✅ Split train/test rigoroso
- ✅ Detector de overfitting
- ✅ Métricas com intervalos de confiança

Veja histórico completo em `CHANGELOG.md`

---

## 🆘 Suporte

### Problemas Comuns

**Erro de importação:**
```bash
# Certifique-se de que o ambiente virtual está ativado
env\Scripts\activate
pip install -r requirements.txt
```

**Erro ao executar:**
```bash
# Verifique se está no diretório correto
cd D:\MegaCLI_Clean
python megacli.py
```

Veja mais em `INSTALL.md`

---

## ⚠️ Aviso Legal

Este sistema é apenas para fins educacionais e de análise estatística. Não há garantia de ganhos em jogos de loteria. Use com responsabilidade.

---

## 📄 Licença

Projeto educacional - Uso pessoal

---

**Desenvolvido com análise estatística rigorosa** 📊
