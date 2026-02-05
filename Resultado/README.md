# Resultado - Arquivos Gerados

Este diretório armazena todos os resultados gerados pelo MegaCLI.

## 📁 Estrutura

```
Resultado/
├── exemplos/          # Exemplos de saída (mantidos)
└── [saídas geradas]   # Arquivos temporários (não versionados)
```

## 📄 Tipos de Arquivos Gerados

### Modo Conservador (Opção 12)

**Formato:** `previsao_top9_YYYY-MM-DD_HH-MM-SS.*`

- **`.txt`** - Jogos em formato texto (fácil leitura)
- **`.xlsx`** - Planilha Excel com análises detalhadas
- **`.json`** - Dados estruturados (programático)
- **`.png`** - Gráficos de visualização

### Análise de Correlação

**Formato:** `correlacao_retroativa_YYYY-MM-DD_HH-MM-SS.*`

- Análise de performance histórica
- Métricas de overfitting
- Comparação de métodos

## 🔄 Limpeza

Arquivos neste diretório são temporários e podem ser removidos:

```bash
# Manter apenas exemplos
cd D:\MegaCLI_Clean\Resultado
del *.txt *.xlsx *.json *.png
# Mantém subpasta exemplos/
```

## ⚠️ Git Ignore

Por padrão, apenas a pasta `exemplos/` é versionada.
Todos os outros arquivos são ignorados pelo `.gitignore`.

---

**Nota:** Arquivos são nomeados com timestamp para evitar sobrescrever resultados anteriores.
