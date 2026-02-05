# Guia de Instalação - MegaCLI v6.3

**Sistema de Análise Mega-Sena - Edição Limpa**

---

## 📋 Pré-requisitos

### Software Necessário

1. **Python 3.9 ou superior**
   - Download: https://www.python.org/downloads/
   - Durante a instalação, marque "Add Python to PATH"

2. **pip** (gerenciador de pacotes)
   - Geralmente já vem com Python
   - Verificar: `python -m pip --version`

3. **Git** (opcional, para clonar repositório)
   - Download: https://git-scm.com/downloads

### Requisitos do Sistema

- **Sistema Operacional:** Windows 10/11, Linux ou macOS
- **RAM:** Mínimo 4GB (recomendado 8GB)
- **Espaço em Disco:** ~100MB para instalação + dados
- **Conexão com Internet:** Para download de dependências

---

## 🚀 Instalação Passo a Passo

### 1. Preparar o Ambiente

```bash
# Navegue até o diretório do projeto
cd D:\MegaCLI_Clean
```

### 2. Criar Ambiente Virtual (Recomendado)

**Por que usar ambiente virtual?**
- Isola dependências do projeto
- Evita conflitos com outras instalações Python
- Facilita manutenção

**No Windows:**
```bash
python -m venv env
```

**No Linux/macOS:**
```bash
python3 -m venv env
```

### 3. Ativar Ambiente Virtual

**No Windows:**
```bash
env\Scripts\activate
```

**No Linux/macOS:**
```bash
source env/bin/activate
```

**Confirmação:** O prompt deve mostrar `(env)` no início

### 4. Instalar Dependências

```bash
pip install -r requirements.txt
```

**Tempo estimado:** 2-5 minutos (depende da conexão)

**Pacotes instalados:**
- pandas - Manipulação de dados
- numpy - Computação numérica
- matplotlib - Gráficos
- scipy - Estatística
- openpyxl - Excel
- E outros (veja requirements.txt)

### 5. Verificar Instalação

```bash
# Listar pacotes instalados
pip list

# Verificar imports principais
python -c "import pandas, numpy, matplotlib; print('OK')"
```

Se exibir "OK", a instalação está correta!

---

## ✅ Primeira Execução

### Teste Básico

```bash
python megacli.py
```

**Deve exibir:**
```
==============================================
      MEGACLI - Sistema de Análise
            Mega-Sena v6.3
==============================================

MENU PRINCIPAL
...
```

### Teste Completo - Modo Conservador

1. Execute: `python megacli.py`
2. Escolha opção: `12` (Modo Conservador)
3. Aguarde processamento (~1-2 minutos)
4. Verifique arquivos gerados em `Resultado/`

**Arquivos esperados:**
- `previsao_top9_YYYY-MM-DD_HH-MM-SS.txt`
- `previsao_top9_YYYY-MM-DD_HH-MM-SS.xlsx`
- `previsao_top9_YYYY-MM-DD_HH-MM-SS.json`
- Gráficos PNG

---

## 🔧 Solução de Problemas

### Erro: "Python não reconhecido"

**Problema:** Python não está no PATH

**Solução:**
1. Reinstale Python marcando "Add to PATH"
2. OU adicione manualmente ao PATH do sistema

### Erro: "No module named 'pandas'"

**Problema:** Dependências não instaladas ou ambiente não ativado

**Solução:**
```bash
# Ative o ambiente virtual
env\Scripts\activate

# Reinstale dependências
pip install -r requirements.txt
```

### Erro: "Permission denied"

**Problema:** Falta de permissões

**Solução Windows:**
```bash
# Execute PowerShell como Administrador
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Solução Linux/macOS:**
```bash
chmod +x megacli.py
```

### Erro: "HISTORICO_MEGASENA.csv não encontrado"

**Problema:** Arquivo de dados faltando

**Solução:**
1. Verifique se `Dados/HISTORICO_MEGASENA.csv` existe
2. Se necessário, copie do projeto original

### Erro ao gerar gráficos (matplotlib)

**Problema:** Backend de visualização

**Solução:**
```bash
# Reinstalar matplotlib
pip uninstall matplotlib
pip install matplotlib
```

---

## 📦 Atualização de Dependências

### Atualizar todos os pacotes

```bash
pip install --upgrade -r requirements.txt
```

### Atualizar pacote específico

```bash
pip install --upgrade pandas
```

### Verificar versões

```bash
pip freeze > installed_versions.txt
```

---

## 🔄 Desinstalação

### Remover ambiente virtual

```bash
# Desative o ambiente
deactivate

# Delete o diretório
rmdir /s env  # Windows
rm -rf env    # Linux/macOS
```

### Remover projeto completo

```bash
# Navegue para o diretório pai
cd D:\

# Delete o projeto
rmdir /s MegaCLI_Clean  # Windows
rm -rf MegaCLI_Clean    # Linux/macOS
```

---

## 📝 Configuração Avançada

### Personalizar config.yaml

Edite `config/config.yaml` para ajustar:
- Parâmetros de análise
- Thresholds de confiança
- Configurações de exportação

### Variáveis de Ambiente

Crie arquivo `.env` na raiz (se necessário):
```ini
# Exemplo
DEBUG=True
LOG_LEVEL=INFO
```

---

## 🆘 Suporte Adicional

### Logs de Erro

Logs são salvos em:
- `logs/` (se configurado)
- Console durante execução

Para debug detalhado:
```bash
python megacli.py --verbose
```

### Verificar Integridade

```bash
# Listar arquivos copiados
dir /s /b D:\MegaCLI_Clean  # Windows
find D:\MegaCLI_Clean      # Linux/macOS

# Contar arquivos Python
dir /s *.py | find /c ".py"  # Windows
find . -name "*.py" | wc -l  # Linux/macOS
```

---

## ✅ Checklist de Instalação

- [ ] Python 3.9+ instalado
- [ ] pip funcionando
- [ ] Ambiente virtual criado
- [ ] Ambiente virtual ativado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Teste básico OK (`python megacli.py`)
- [ ] Teste Opção 12 OK
- [ ] Arquivos gerados em `Resultado/`
- [ ] Gráficos sendo criados

---

## 🎯 Próximos Passos

1. ✅ Instalação completa
2. 📖 Leia `README.md` para entender funcionalidades
3. 🚀 Execute Opção 12 (Modo Conservador recomendado)
4. 📊 Analise os resultados gerados
5. 🔬 Explore outras opções do menu

---

**Instalação bem-sucedida!** 🎉

Para dúvidas, consulte `README.md` ou documentação em `docs/`
