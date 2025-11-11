# Como subir para o GitHub

Este guia mostra como inicializar o repositório Git e fazer upload para o GitHub.

## Pré-requisitos

- Conta no GitHub
- Git instalado localmente
- SSH key configurada (recomendado) ou HTTPS

## Passo a Passo

### 1. Inicializar Repositório Local

```bash
cd /projetos/monitoracao-recargas

# Inicializar git
git init

# Adicionar todos os arquivos
git add .

# Primeiro commit
git commit -m "Initial commit: Sistema de Monitoramento de Recargas

- Automação com Selenium WebDriver
- Análise de dados com Pandas
- Sistema de alertas por email
- Thresholds dinâmicos por período
- Documentação completa"
```

### 2. Criar Repositório no GitHub

1. Acesse https://github.com
2. Clique em **New repository**
3. Preencha:
   - **Repository name:** `monitoracao-recargas`
   - **Description:** Sistema automatizado de monitoramento de transações com alertas inteligentes
   - **Visibility:** Public (para portfólio)
   - ⚠️ **NÃO** marque "Initialize with README" (já temos um)
4. Clique em **Create repository**

### 3. Conectar Repositório Local ao GitHub

```bash
# Adicionar remote (substitua SEU-USUARIO)
git remote add origin git@github.com:SEU-USUARIO/monitoracao-recargas.git

# Ou via HTTPS:
# git remote add origin https://github.com/SEU-USUARIO/monitoracao-recargas.git

# Renomear branch para main (se necessário)
git branch -M main

# Push inicial
git push -u origin main
```

### 4. Verificar Upload

Acesse: `https://github.com/SEU-USUARIO/monitoracao-recargas`

Você deve ver:
- ✅ README.md renderizado
- ✅ Badges no topo
- ✅ Arquivos Python
- ✅ config.example.py (mas NÃO config.py)
- ✅ LICENSE

### 5. Configurar GitHub (Opcional mas Recomendado)

#### Adicionar Topics

No GitHub, clique em **Add topics** e adicione:
- `python`
- `selenium`
- `automation`
- `web-scraping`
- `data-analysis`
- `monitoring`
- `pandas`
- `alert-system`

#### Adicionar Descrição

```
🤖 Sistema automatizado de monitoramento de transações com detecção inteligente de anomalias e alertas em tempo real
```

#### Ativar GitHub Pages (Opcional)

Settings → Pages → Source: main branch

### 6. Manter o Repositório

```bash
# Fazer mudanças
# ... editar arquivos ...

# Ver status
git status

# Adicionar mudanças
git add .

# Commit
git commit -m "Descrição da mudança"

# Push
git push
```

## Estrutura Final no GitHub

```
monitoracao-recargas/
├── 📄 README.md                  # Página principal (renderizado)
├── 📄 LICENSE                    # Licença MIT
├── 📄 CONTRIBUTING.md            # Guia de contribuição
├── 📄 GITHUB_SETUP.md            # Este arquivo
├── 🔧 config.example.py          # Template de configuração
├── 🔧 .gitignore                 # Arquivos ignorados
├── 🐍 servcel_extractor.py       # Script principal
├── 🐍 recarga_analyzer.py        # Análise de dados
├── 🐍 email_sender.py            # Envio de emails
├── 🐍 report_generator.py        # Geração de relatórios
├── 📦 requirements.txt           # Dependências
├── 🔧 setup.sh                   # Script de instalação
└── 🔧 run_alarmistica.sh         # Script de execução cron
```

## Checklist de Segurança ✅

Antes de fazer push, certifique-se:

- [ ] `config.py` **NÃO** está no repositório
- [ ] Nenhuma senha ou credencial está commitada
- [ ] `.gitignore` está configurado corretamente
- [ ] Todos os arquivos sensíveis estão em `.gitignore`
- [ ] `config.example.py` contém apenas dados de exemplo

## Próximos Passos

1. **Adicione ao seu LinkedIn:**
   - Portfolio → Add project
   - Link para o GitHub
   - Descrição das tecnologias usadas

2. **Melhore ao longo do tempo:**
   - Adicione issues como "TODO"
   - Aceite contribuições externas
   - Atualize documentação conforme evolui

3. **Divulgue:**
   - LinkedIn post sobre o projeto
   - Twitter/X com hashtags #Python #Automation
   - Dev.to article explicando o desenvolvimento

## Dicas para Portfólio

✅ **Boas práticas que impressionam:**
- README.md detalhado e profissional
- Código limpo e documentado
- Diagramas de arquitetura
- Badges de status
- Licença open source
- Guia de contribuição
- Commits com mensagens claras
- Issues e PRs organizados

✅ **No README, destaque:**
- Problemas técnicos resolvidos
- Tecnologias utilizadas
- Decisões arquiteturais
- Impacto do projeto (ex: "Redução de 40% no tempo de detecção")

---

**Pronto!** Seu projeto profissional está no GitHub! 🚀
