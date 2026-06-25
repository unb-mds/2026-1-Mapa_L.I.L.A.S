# Estudo: Implementação dos Dashboards — Mapa L.I.L.A.S.

> **Relacionado à issue:** Discussão da forma que vamos implementar os dashboards (quais bibliotecas, quantos gráficos)  
> **Release:** Release 2  
> **Data:** Junho de 2026

---

## 1. Contexto

A plataforma L.I.L.A.S. precisava de uma seção de visualização de dados para que o usuário pudesse analisar a distribuição dos Projetos de Lei de forma visual e interativa. A decisão passou por três perguntas principais:

- Qual biblioteca de gráficos usar?
- Quantos e quais tipos de gráficos implementar?
- Como organizar os filtros sem criar contradições lógicas?

---

## 2. Biblioteca Escolhida: Recharts

### O que é?
**Recharts** é uma biblioteca de gráficos para React, construída sobre SVG e D3. Ela fornece componentes prontos e declarativos que se integram naturalmente ao ecossistema React.

### Por que Recharts?

| Critério | Recharts | Chart.js | D3.js |
|---|---|---|---|
| Integração com React | ✅ Nativa | ⚠️ Wrapper necessário | ❌ Manual |
| Curva de aprendizado | ✅ Baixa | ✅ Baixa | ❌ Alta |
| Responsividade | ✅ `ResponsiveContainer` | ⚠️ Manual | ❌ Manual |
| Já disponível no projeto | ✅ Sim | ❌ Não | ❌ Não |

A escolha do Recharts foi direta: **já estava listada como dependência disponível no projeto** e oferece a melhor integração com React sem código extra.

### Instalação

```bash
npm install recharts
```

---

## 3. Gráficos Implementados

Foram implementados **2 tipos de gráficos**, alternáveis por abas na mesma página:

### 3.1 Gráfico de Colunas (`BarChart`)

Ideal para **comparar quantidades entre categorias**. Mostra claramente qual partido, estado, gênero ou mês tem mais proposições.

**Componentes Recharts utilizados:**
```jsx
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
```

**Estrutura básica:**
```jsx
<ResponsiveContainer width="100%" height={350}>
  <BarChart data={dados}>
    <CartesianGrid strokeDasharray="3 3" vertical={false} />
    <XAxis dataKey="label" />
    <YAxis />
    <Tooltip />
    <Bar dataKey="total" fill="#5B4FCF" radius={[4, 4, 0, 0]} />
  </BarChart>
</ResponsiveContainer>
```

---

### 3.2 Gráfico de Pizza (`PieChart`)

Ideal para **visualizar proporções** do total. Mostra o peso percentual de cada partido, estado, gênero ou mês no conjunto total de PLs.

**Componentes Recharts utilizados:**
```jsx
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';
```

**Estrutura básica:**
```jsx
<PieChart>
  <Pie data={dados} dataKey="total" nameKey="label" outerRadius={140}>
    {dados.map((_, index) => (
      <Cell key={index} fill={CORES[index % CORES.length]} />
    ))}
  </Pie>
  <Tooltip />
</PieChart>
```

A legenda lateral foi construída **manualmente** (não usamos o componente `Legend` do Recharts) para ter mais controle sobre o layout e exibir o total + percentual de cada fatia.

---

## 4. Decisão de Design: "Comparar por" + Filtros

### O problema original
Os protótipos iniciais tinham filtros de Partido, Estado, Gênero e Mês, mas o **eixo do gráfico** também era um desses — o que criava uma contradição: se o gráfico já mostrava dados **por partido**, filtrar por partido não fazia sentido.

### A solução implementada
Separamos **dimensão de comparação** de **filtro de recorte**:

- **"Comparar por"** → define o eixo X do gráfico (o que estamos comparando)
- **Filtros** → recortam os dados antes de agrupar

**Regra principal:** o filtro igual à dimensão ativa **fica oculto automaticamente**.

| Comparar por | Filtros visíveis |
|---|---|
| Partido | Estado, Gênero, Mês |
| Estado | Partido, Gênero, Mês |
| Gênero do Autor | Estado, Partido, Mês |
| Mês | Estado, Partido, Gênero |

**Exemplo prático:** Se o usuário escolhe "Comparar por: Partido" e filtra "Estado: SP", o gráfico mostra a distribuição de PLs por partido **considerando apenas os PLs de São Paulo**.

---

## 5. Estrutura de Componentes

A página foi dividida em componentes pequenos e independentes, seguindo o padrão do projeto:

```
pages/Dashboard/index.jsx       ← orquestra tudo
components/Dashboard/
  ├── BreadcrumbDashboard.jsx   ← navegação de contexto
  ├── SeletorComparar.jsx       ← botões PARTIDO/ESTADO/GÊNERO/MÊS
  ├── FiltrosDashboard.jsx      ← filtros com ocultação dinâmica
  ├── CardIndicadores.jsx       ← 3 cards de resumo (total, partido, estado)
  ├── GraficoColunas.jsx        ← BarChart do recharts
  ├── GraficoPizza.jsx          ← PieChart + legenda lateral
  └── BotaoExportar.jsx         ← exportação em PNG
hooks/useDashboard.js           ← estado, filtros e chamada à API
```

---

## 6. Exportação em PNG

Para permitir que o usuário baixe o gráfico como imagem, implementamos uma solução usando o SVG nativo que o Recharts gera:

```javascript
const exportarPNG = () => {
  const svg = chartRef.current.querySelector('svg');
  const svgData = new XMLSerializer().serializeToString(svg);
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  const img = new Image();

  const url = URL.createObjectURL(
    new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' })
  );

  img.onload = () => {
    canvas.width = img.width;
    canvas.height = img.height;
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(img, 0, 0);
    
    const link = document.createElement('a');
    link.download = 'grafico-lilas.png';
    link.href = canvas.toDataURL('image/png');
    link.click();
  };

  img.src = url;
};
```

**Fluxo:** SVG do gráfico → Blob → Canvas → PNG → Download automático.

---

## 7. Integração com o Backend

O endpoint definido para o Dashboard foi:

```
GET /api/graficos/distribuicao?comparar_por=partido&estado=SP&genero=feminino
```

Enquanto o backend não implementa o endpoint, os dados são servidos por mocks locais em `src/mocks/dashboard.js`, com dados diferentes para cada dimensão de comparação. A troca para dados reais é feita mudando uma única linha:

```javascript
const USE_MOCK_DASHBOARD = false; // muda para false quando o back estiver pronto
```

---

## 8. Resumo das Decisões

| Decisão | Escolha | Motivo |
|---|---|---|
| Biblioteca de gráficos | Recharts | Já disponível, integração nativa com React |
| Tipos de gráfico | Colunas + Pizza | Colunas para comparação, Pizza para proporção |
| Número de gráficos | 2 (alternáveis por aba) | Evita poluição visual, mesmos dados em duas visualizações |
| Controle de filtros | "Comparar por" + ocultação dinâmica | Evita contradição lógica entre filtro e eixo |
| Exportação | PNG via Canvas | Simples, sem dependência extra |
| Dados durante dev | Mock por dimensão | Permite desenvolver sem depender do backend |

---

*Documento gerado como registro da issue: "Discussão da forma que vamos implementar os dashboards (quais bibliotecas, quantos gráficos)"*
