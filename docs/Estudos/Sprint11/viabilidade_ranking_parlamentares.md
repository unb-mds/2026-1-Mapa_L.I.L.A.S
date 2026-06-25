# Estudo de Viabilidade Técnica
## Funcionalidade de Ranking de Parlamentares — Release 02
**Mapa L.I.L.A.S · MDS UnB 2026.1 · Junho de 2026**

---

## 1. Resumo Executivo

Este documento avalia a viabilidade técnica de implementar o ranking de parlamentares na Release 02 do Mapa L.I.L.A.S, respondendo às quatro perguntas levantadas pela equipe.

A Release 01 entregou a infraestrutura base completa: tabelas do banco criadas, coleta das APIs da Câmara e do Senado funcionando, e a tela de PLs com filtros de partido, UF, status e ano já operacionais. O ranking parte dessa base — não do zero.

| Pergunta | Resposta resumida |
|---|---|
| Temos dados suficientes? | **Parcialmente.** Autoria, UF e partido já estão no banco. Tema exige extensão do schema. |
| Como seria feito / quais critérios? | Contagem de proposições por parlamentar, filtrável por UF e partido. Votações e emendas têm custo alto. |
| Quais endpoints são necessários? | 1 endpoint novo no FastAPI. Nenhuma migração de banco para o critério principal. |
| Quanto de complexidade adiciona? | **Baixa** para o critério principal. Alta se votações/emendas forem incluídas agora. |

> **Recomendação:** implementar o ranking de proposições (autor + coautor) com filtros de UF e partido na Release 02, aproveitando a infraestrutura já entregue. Tema, votações e emendas devem ser avaliados para a fora do escopo.

---

## 2. Estado atual após a Release 01

O que já está disponível e impacta diretamente o ranking:

| Componente | Status após Release 01 | Impacto no ranking |
|---|---|---|
| Tabelas do banco PostgreSQL | ✅ Criadas e funcionando | As tabelas `autoria_camara`, `autoria_senado` e `parlamentares` já existem. |
| Coleta da API da Câmara | ✅ Funcionando | Proposições e autorias da Câmara já estão sendo persistidas. |
| Coleta da API do Senado | ✅ Funcionando | Proposições e autorias do Senado já estão sendo persistidas. |
| Filtros de UF e partido | ✅ Existem na tela de PLs | A lógica de filtro já foi validada no frontend e no backend — pode ser reaproveitada. |
| FastAPI configurado | ✅ Funcionando | O novo endpoint de ranking é aditivo, sem tocar no que já existe. |
| React + TailwindCSS | ✅ Funcionando | O componente de tabela do ranking segue os padrões visuais já estabelecidos na tela de PLs. |
| Docker | ✅ Configurado | Nenhuma mudança de infraestrutura necessária. |

---

## 3. Análise do Schema

### 3.1 O que já suporta o ranking

| Tabela | Campo relevante | Uso no ranking |
|---|---|---|
| `parlamentares` | `id, nome_eleitoral, sigla_partido, sigla_uf, sexo, casa` | Identidade do parlamentar; filtros de UF e partido nativos. |
| `autoria_camara` | `id_pl, id_parlamentar, tipo_autoria` | Contagem de proposições da Câmara. `tipo_autoria` diferencia autor de coautor. |
| `autoria_senado` | `id_pl, id_parlamentar, tipo_autoria` | Idem para o Senado. |
| `pls_camara` / `pls_senado` | `id, sigla_tipo, ano` | JOIN para filtrar por tipo e período se necessário. |

> ✅ O critério principal (total de proposições) já pode ser calculado com as tabelas existentes via `COUNT + JOIN`, **sem nenhuma migração de schema**.

### 3.2 O que está faltando por filtro

| Filtro | Situação | Complexidade | O que é preciso |
|---|---|---|---|
| UF | ✅ Disponível | Nenhuma | `sigla_uf` já está em `parlamentares`. |
| Partido | ✅ Disponível | Nenhuma | `sigla_partido` já está em `parlamentares`. |
| Período / Ano | ✅ Disponível | Nenhuma | Campo `ano` existe em `pls_camara`; `data_apresentacao` no Senado. |
| Tema (Senado) | ⚠️ Parcial | Baixa | `assunto_geral_codigo` já vem no payload do Senado, mas não está persistido em `pls_senado`. |
| Tema (Câmara) | ❌ Ausente | Média | Nova tabela `proposicoes_temas_camara` + coleta via endpoint separado `/referencias/proposicoes/codTema`. |

---

## 4. Critérios de Ordenação

| Critério | Dados disponíveis? | Custo | Recomendação |
|---|---|---|---|
| Total de proposições (autor + coautor) | ✅ Sim | Baixo | ✅ Release 02 |
| Só autoria principal (excluir coautorias) | ✅ Sim | Baixo | ✅ Release 02 (toggle) |
| Votações em plenário | ⚠️ Não mapeado | Alto | ❌ Fora do escopo |
| Propostas de emenda | ⚠️ Não mapeado | Alto | ❌ Fora do escopo |

### Por que votações e emendas ficam para depois

Exigem coleta de endpoints distintos, fora do escopo da coleta atual. Incluí-los agora:

- Adicionaria 2–3 novas tabelas sem aprovação de migração Alembic.
- Criaria novos jobs de coleta fora do ciclo de 2h já definido.
- Violaria a regra da Constituição do projeto: *"Uma tarefa por vez. Não implemente duas tarefas no mesmo diff."*

---

## 5. Query Central do Ranking

Opera sobre o schema atual, sem migração:

```sql
-- Ranking: total de proposições por parlamentar
SELECT
    p.id,
    p.nome_eleitoral,
    p.sigla_partido,
    p.sigla_uf,
    p.casa,
    COUNT(*) AS total_proposicoes
FROM parlamentares p
LEFT JOIN autoria_camara ac  ON ac.id_parlamentar  = p.id
LEFT JOIN autoria_senado  as_ ON as_.id_parlamentar = p.id
WHERE
    (:uf      IS NULL OR p.sigla_uf      = :uf)
    AND (:partido IS NULL OR p.sigla_partido = :partido)
GROUP BY p.id, p.nome_eleitoral, p.sigla_partido, p.sigla_uf, p.casa
ORDER BY total_proposicoes DESC
LIMIT :limite OFFSET :pagina;
```

**Observações:**

- `:uf` e `:partido` assumem `NULL` quando não informados — filtros opcionais sem alterar a query base.
- `LEFT JOIN` garante que parlamentares sem proposições ainda apareçam (total = 0).
- Paginação via `LIMIT/OFFSET` protege a performance.
- Os índices em `sigla_uf`, `sigla_partido` e `id_parlamentar` já foram previstos na Tarefa 5 da Funcionalidade 1 do `claude.md` — verificar se foram aplicados antes de subir o endpoint.

---

## 6. Endpoint FastAPI

Um único endpoint novo, aditivo, sem tocar no que já existe:

| Campo | Detalhe |
|---|---|
| Rota | `GET /api/v1/parlamentares/ranking` |
| Query params | `uf` (str, opcional), `partido` (str, opcional), `limite` (int, default 20), `pagina` (int, default 0) |
| Resposta | `{ total_registros, pagina, resultados: [{ id, nome_eleitoral, sigla_partido, sigla_uf, casa, total_proposicoes }] }` |
| Modelos Pydantic | `ParlamentarRankingItem` + `ParlamentarRankingResponse` |
| Cache sugerido | 30 min — o dado muda apenas a cada ciclo de coleta (2h). |

---

## 7. O Filtro por Tema: Decisão em Aberto

A assimetria entre as APIs exige uma decisão antes de implementar:

| | Câmara | Senado |
|---|---|---|
| Como o tema vem | Endpoint/arquivo separado por ano. Relação N:N com as proposições. | Embutido no payload da matéria (`assunto_geral_codigo`). |
| Schema atual | ❌ Não mapeado | ⚠️ Não persistido |
| O que é preciso | Nova tabela `proposicoes_temas_camara` + job de coleta extra. | Adicionar 2 colunas em `pls_senado` + migração Alembic. |
| Custo estimado | 2–3 dias | 0,5–1 dia |

### Opções para a equipe decidir

1. **Excluir tema da Release 02 (recomendado):** lançar o ranking com UF e partido. Tema entra na fora do escopo.
2. **Tema parcial:** persistir o assunto do Senado agora (custo baixo) e deixar o da Câmara para depois.
3. **Tema completo agora:** custo médio-alto. Só recomendado se for critério bloqueante para o usuário.

---

## 8. Exportação para PDF

O dado do ranking pode ser reaproveitado diretamente na exportação em PDF, sem duplicação de lógica:

| Aspecto | Avaliação |
|---|---|
| Fonte de dados | O mesmo `GET /api/v1/parlamentares/ranking` é consumido tanto pelo React quanto pelo gerador de PDF. |
| Abordagem | Backend Python (`WeasyPrint` ou `ReportLab`) recebe o JSON e gera o PDF. Endpoint: `GET /api/v1/parlamentares/ranking/exportar?formato=pdf`. |
| Regra da Constituição | Exportação é tarefa separada — não pode ser codificada na mesma PR do endpoint de ranking. |
| Dependência | Depende do endpoint de ranking estar estável. Planejar para depois do endpoint de ranking estar estável, ainda dentro da Release 02. |

---

## 9. Mapa de Complexidade

| Componente | Esforço estimado | Complexidade | Inclui na Release 02? |
|---|---|---|---|
| Query de ranking (`COUNT + JOIN`) | 0,5 dia | 🟢 Baixa | ✅ Sim |
| Modelos Pydantic do endpoint | 0,5 dia | 🟢 Baixa | ✅ Sim |
| Endpoint `GET /parlamentares/ranking` | 1 dia | 🟢 Baixa | ✅ Sim |
| Componente React (tabela de ranking) | 1–2 dias | 🟡 Baixa–Média | ✅ Sim |
| Persistência do assunto do Senado (tema parcial) | 0,5–1 dia | 🟢 Baixa | ✅ Se aprovado |
| Tabela de temas da Câmara + coleta | 2–3 dias | 🟡 Média | ❌ Fora do escopo |
| Exportação PDF do ranking | 1–2 dias | 🟡 Baixa–Média | ❌ Fora do escopo |
| Critério de votações | 3–5 dias | 🔴 Alta | ❌ Fora do escopo |
| Critério de propostas de emenda | 3–5 dias | 🔴 Alta | ❌ Fora do escopo |

**Total da Release 02 recomendada:** ~3–4 dias (backend + frontend), aproveitando a infraestrutura já entregue.

---

## 10. Checklist de Decisões para a Equipe

| # | Decisão | Opções | Recomendação |
|---|---|---|---|
| 1 | O ranking conta coautorias ou só autoria principal? | Ambas / Só autor principal | Ambas, com toggle no frontend |
| 2 | Tema entra na Release 02? | Sim / Não / Parcial (só Senado) | Não (fora do escopo) |
| 3 | Votações e emendas entram na Release 02? | Sim / Não | Não (fora do escopo) |
| 4 | Exportação PDF é escopo da Release 02 ou 03? | 02 / 03 | ❌ Fora do escopo |
| 5 | Quantos parlamentares por página (limite padrão)? | 10 / 20 / 50 | 20 |

---

## 11. Conclusão

O ranking de parlamentares por total de proposições é viável para a Release 02 com o schema já entregue na Release 01. Nenhuma migração de banco é necessária para o critério principal. Os filtros de UF e partido reaproveitam a lógica já validada na tela de PLs. O esforço total estimado é de 3–4 dias.

O filtro por tema e os critérios de votações/emendas são implementáveis, mas com custo que pode comprometer a Release 02 — a equipe deve decidir explicitamente se entram ou ficam fora do escopo do projeto.

A exportação em PDF reutilizará o endpoint do ranking sem duplicação de lógica, mas deve entrar como tarefa autônoma após o ranking estar estável, ainda dentro da Release 02.

> **Próximo passo:** levar o Checklist da Seção 10 para o próximo refinamento, alinhar as 5 decisões e abrir as issues separadas para Release 02 e fora do escopo.

---

*🌺 Mapa L.I.L.A.S · MDS UnB 2026.1*
