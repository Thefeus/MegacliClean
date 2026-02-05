# Notas sobre Dependências - MegaCLI_Clean

## ⚠️ Mudanças em requirements.txt

### Conflito Resolvido (03/02/2026)

**Problema original:**
- `langchain-community 0.0.13` (muito antiga)
- `langchain-core 1.2.5` (nova)
- **Incompatibilidade:** langchain-community 0.0.13 requer langchain-core <0.2

**Solução aplicada:**
Todas as versões do langchain atualizadas para série 0.3.x (compatíveis):

```
langchain==0.3.13
langchain-core==0.3.28
langchain-google-genai==2.0.8
langchain-community==0.3.13
langchain-ollama==0.2.2
```

### Dependências Adicionadas

**Visualização (necessárias para gráficos):**
- `matplotlib==3.10.0`
- `seaborn==0.13.2`

---

## 📦 Instalação

```bash
cd D:\MegaCLI_Clean
python -m venv env
env\Scripts\activate
pip install -r requirements.txt
```

**Nota:** A instalação pode demorar alguns minutos devido ao torch e transformers.

---

## ✅ Dependências Essenciais para Funcionalidades

| Funcionalidade | Dependências |
|----------------|--------------|
| Análise de dados | pandas, numpy, scipy |
| Visualizações | matplotlib, seaborn |
| Machine Learning | scikit-learn, xgboost |
| IA/LLM | langchain (série 0.3.x) |
| Excel | openpyxl |
| Modo Conservador | Todas acima |

---

**Última atualização:** 03/02/2026
