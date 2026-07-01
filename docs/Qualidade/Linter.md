# Padronização e Qualidade Estética (Linter)

Manter um código limpo e organizado é um pilar vital no projeto L.I.L.A.S., especialmente por termos partes do ecossistema divididas em duas linguagens distintas (Python para backend e JavaScript para frontend). O papel dos *linters* é garantir que todos os desenvolvedores sigam as mesmas convenções de formatação e boas práticas, reduzindo drasticamente o aparecimento de *Code Smells*.

## O que é verificado?

O Linter age como o primeiro "fiscal" do nosso código. Antes do código ser considerado pronto, ele é escaneado em busca de:
* Variáveis que foram declaradas mas nunca utilizadas no escopo.
* Imports de bibliotecas que estão "sobrando" no arquivo.
* Quebras de linha excessivas, falta de espaçamento padronizado (como ausência de uma linha vazia no final do arquivo).
* Erros de sintaxe ou de tipagem simples.

### Ferramentas Utilizadas
* **Backend (Python):** Usamos prioritariamente o `flake8`, associado ao `black` para formatação. Juntos, eles forçam a aderência total às PEP-8 (guia de estilo do Python).
* **Frontend (React/Vite):** Adotamos o `ESLint` juntamente ao `Prettier`. Eles alertam sobre uso perigoso de hooks React (como `useEffect` mal estruturado) ou declarações redundantes no JSX.


