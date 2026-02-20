# FLEXT API

Camada de API HTTP para exposicao e consumo de servicos de dados no ecossistema FLEXT.

Descricao oficial atual: "FLEXT API - High-Performance REST API with FastAPI".

## O que este projeto entrega

- Padroniza contratos REST para chamadas internas e externas.
- Orquestra requisicoes/respostas entre clientes e servicos de dominio.
- Centraliza fronteira HTTP para integracoes de negocio.

## Contexto operacional

- Entrada: requests HTTP + payloads contratuais.
- Saida: responses padronizadas e rastreaveis.
- Dependencias: flext-auth, flext-core e servicos consumidores/provedores.

## Estado atual e risco de adocao

- Qualidade: **Alpha**
- Uso recomendado: **Nao produtivo**
- Nivel de estabilidade: em maturacao funcional e tecnica, sujeito a mudancas de contrato sem garantia de retrocompatibilidade.

## Diretriz para uso nesta fase

Aplicar este projeto somente em desenvolvimento, prova de conceito e homologacao controlada, com expectativa de ajustes frequentes ate maturidade de release.
