# FLEXT-API - PLANO DE CORREÇÕES

**Status**: 8 erros de lint identificados
**Criticidade**: ALTA (gateway principal)
**Abordagem**: Correções manuais cuidadosas

## 📋 ERROS IDENTIFICADOS

### 1. TRY300 - auth_service.py:127
**Erro**: Consider moving return to else block
**Correção**:
```python
# Antes:
try:
    # code
    return result
except Exception as e:
    # handle

# Depois:
try:
    # code
except Exception as e:
    # handle
else:
    return result
```

### 2. D417 - plugin_service.py:37
**Erro**: Missing argument description for `plugin_type`
**Correção**: Adicionar na docstring:
```python
"""Install a plugin.

Args:
    name: Plugin name
    plugin_type: Type of plugin to install
    ...
"""
```

### 3. A002 - plugin_service.py:130
**Erro**: Argument `type` shadows builtin
**Correção**: Renomear para `plugin_type`

### 4. FBT001 - plugin_service.py:131, 167
**Erro**: Boolean positional argument
**Correção**: Adicionar `*` antes para forçar keyword-only

### 5. FBT003 - plugin_service.py:252
**Erro**: Boolean positional value in function call
**Correção**: Usar keyword argument

### 6. BLE001 - plugin_service.py:294
**Erro**: Blind exception catch
**Correção**: Especificar tipo de exceção

### 7. FBT001 - system_service.py:172
**Erro**: Boolean positional argument
**Correção**: Adicionar `*` para keyword-only

## 🔧 ORDEM DE CORREÇÃO

1. **Primeiro**: Verificar testes passam atualmente
2. **Correções simples** (renomear, docstrings)
3. **Correções estruturais** (try/except, argumentos)
4. **Testar após cada correção**

## ⚠️ RISCOS

- Mudanças de API (renomear `type` → `plugin_type`)
- Quebrar código que usa argumentos posicionais
- Alterar comportamento de exceções

## ✅ VALIDAÇÃO

Após cada correção:
```bash
make test  # Deve continuar passando
make lint  # Deve reduzir erros
```