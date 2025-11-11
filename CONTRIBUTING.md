# Contribuindo para o Projeto

Obrigado por considerar contribuir para o Sistema de Monitoramento de Recargas! 🎉

## Como Contribuir

### Reportar Bugs

Se você encontrou um bug, por favor abra uma issue incluindo:

- Descrição clara do problema
- Passos para reproduzir
- Comportamento esperado vs. comportamento atual
- Versão do Python e sistema operacional
- Logs relevantes (remova informações sensíveis!)

### Sugerir Melhorias

Sugestões de novas funcionalidades são bem-vindas! Abra uma issue com:

- Descrição detalhada da funcionalidade
- Casos de uso
- Possível implementação (se tiver ideias)

### Pull Requests

1. **Fork o projeto**
2. **Crie uma branch** para sua feature
   ```bash
   git checkout -b feature/MinhaFeature
   ```

3. **Desenvolva seguindo o padrão do projeto**
   - Docstrings em todas as funções
   - Type hints quando possível
   - Comentários em código complexo
   - Logging adequado

4. **Teste sua mudança**
   ```bash
   python3 servcel_extractor.py
   ```

5. **Commit com mensagens claras**
   ```bash
   git commit -m "Add: Implementa feature X"
   git commit -m "Fix: Corrige problema Y"
   git commit -m "Docs: Atualiza documentação Z"
   ```

6. **Push para seu fork**
   ```bash
   git push origin feature/MinhaFeature
   ```

7. **Abra um Pull Request**
   - Descreva suas mudanças
   - Referencie issues relacionadas
   - Aguarde review

## Padrões de Código

### Python Style Guide

Seguimos a [PEP 8](https://www.python.org/dev/peps/pep-0008/):

```python
# Bom
def calcular_percentual(total: int, parte: int) -> float:
    """
    Calcula percentual de parte em relação ao total

    Args:
        total: Valor total
        parte: Valor parcial

    Returns:
        Percentual calculado
    """
    if total == 0:
        return 0.0
    return (parte / total) * 100

# Ruim
def calc(t,p):
    return (p/t)*100 if t!=0 else 0
```

### Commits

- Use verbos no imperativo: "Add", "Fix", "Update", "Remove"
- Seja específico: "Fix: Corrige parsing de data no analyzer" em vez de "Fix bug"
- Primeira linha com no máximo 50 caracteres
- Corpo do commit com detalhes, se necessário

### Documentação

- Toda função pública deve ter docstring
- Use type hints
- Atualize o README.md se adicionar funcionalidades

## Processo de Review

1. Verificação automática de estilo (se configurado)
2. Review de código por mantenedor
3. Testes manuais
4. Merge após aprovação

## Código de Conduta

- Seja respeitoso e profissional
- Aceite críticas construtivas
- Foque no que é melhor para o projeto
- Ajude outros contribuidores

## Dúvidas?

Abra uma issue com a tag `question` ou entre em contato com os mantenedores.

Obrigado por contribuir! 🚀
