import { useState, useMemo } from 'react';
import { PieChart, Pie, Cell, Tooltip } from 'recharts';

const COR_BASE = [
  '#26215C', '#3C3489', '#534AB7', '#6B63C9',
  '#7F77DD', '#948EE0', '#AFA9EC', '#C5C0EE', '#D4CFEE', '#E8E5F7',
];
const CORES_SIMPLES = ['#5B4FCF','#8B7DD8','#B5AEED','#D4CFEE','#E8E5F7','#3D3399','#7C6FBF','#A89BD6'];
const COR_OUTROS = '#9CA3AF';
const TOP_N = 10;

// Layout simples — para Gênero e Mês (poucos itens)
function LegendaSimples({ dados, total, ativo, setAtivo }) {
  const pct = (v) => ((v / total) * 100).toFixed(1);
  return (
    <div className="flex flex-col gap-3">
      {dados.map((item, index) => (
        <div
          key={item.label}
          className="flex items-center gap-3 cursor-default rounded px-1 py-0.5 transition-colors"
          style={{ backgroundColor: ativo === index ? 'rgba(83,74,183,0.08)' : 'transparent' }}
          onMouseEnter={() => setAtivo(index)}
          onMouseLeave={() => setAtivo(null)}
        >
          <span
            className="w-3 h-3 rounded-full flex-shrink-0"
            style={{ backgroundColor: CORES_SIMPLES[index % CORES_SIMPLES.length] }}
          />
          <div>
            <p className="text-sm font-semibold text-gray-800">{item.label}</p>
            <p className="text-xs text-gray-500">
              {item.total.toLocaleString('pt-BR')} ({pct(item.total)}%)
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}

// Layout complexo — para Partido e Estado (muitos itens)
function LegendaCompleta({ fatias, total, partidosOutros, ativo, setAtivo }) {
  const [outrosAberto, setOutrosAberto] = useState(false);
  const pct = (v) => ((v / total) * 100).toFixed(1);

  return (
    <div className="grid grid-cols-2 gap-x-6 gap-y-2 w-full">
      {fatias.map((item, index) => {
        if (item.ehOutros) {
          return (
            <div key={item.label} className="col-span-2">
              <button
                type="button"
                onClick={() => setOutrosAberto((v) => !v)}
                onMouseEnter={() => setAtivo(index)}
                onMouseLeave={() => setAtivo(null)}
                className="flex items-center gap-2 w-full rounded px-1 py-1 mt-1 border-t border-gray-100 pt-2 transition-colors hover:bg-gray-50 text-left"
                style={{ backgroundColor: ativo === index ? 'rgba(83,74,183,0.08)' : undefined }}
                aria-expanded={outrosAberto}
              >
                <span className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: item.cor }} />
                <span className="text-sm text-gray-700">{item.label}</span>
                <svg className="w-3.5 h-3.5 text-gray-400 transition-transform" style={{ transform: outrosAberto ? 'rotate(180deg)' : 'rotate(0deg)' }} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M6 9l6 6 6-6" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                <span className="text-xs text-gray-500 ml-auto whitespace-nowrap">
                  {item.total.toLocaleString('pt-BR')} · {pct(item.total)}%
                </span>
              </button>
              {outrosAberto && (
                <div className="grid grid-cols-2 gap-x-6 gap-y-1 mt-2 pl-5">
                  {partidosOutros.map((p) => (
                    <div key={p.label} className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full flex-shrink-0 bg-gray-300" />
                      <span className="text-xs text-gray-600 truncate">{p.label}</span>
                      <span className="text-xs text-gray-400 ml-auto whitespace-nowrap">
                        {p.total.toLocaleString('pt-BR')} · {pct(p.total)}%
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        }
        return (
          <div
            key={item.label}
            className="flex items-center gap-2 cursor-default rounded px-1 py-0.5 transition-colors"
            style={{ backgroundColor: ativo === index ? 'rgba(83,74,183,0.08)' : 'transparent' }}
            onMouseEnter={() => setAtivo(index)}
            onMouseLeave={() => setAtivo(null)}
          >
            <span className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: item.cor }} />
            <span className="text-sm text-gray-800 truncate">{item.label}</span>
            <span className="text-xs text-gray-500 ml-auto whitespace-nowrap">
              {item.total.toLocaleString('pt-BR')} · {pct(item.total)}%
            </span>
          </div>
        );
      })}
    </div>
  );
}

export default function GraficoPizza({ dados, chartRef, compararPor }) {
  const [ativo, setAtivo] = useState(null);
  const layoutComplexo = compararPor === 'partido' || compararPor === 'estado';

  const { fatias, total, partidosOutros } = useMemo(() => {
    const ordenado = [...dados].sort((a, b) => b.total - a.total);
    const totalGeral = ordenado.reduce((acc, d) => acc + d.total, 0);

    if (!layoutComplexo) {
      return {
        fatias: ordenado.map((d, i) => ({ ...d, cor: CORES_SIMPLES[i % CORES_SIMPLES.length], ehOutros: false })),
        total: totalGeral,
        partidosOutros: [],
      };
    }

    const principais = ordenado.slice(0, TOP_N);
    const resto = ordenado.slice(TOP_N);
    const lista = principais.map((d, i) => ({ ...d, cor: COR_BASE[i % COR_BASE.length], ehOutros: false }));

    let restoDetalhado = [];
    if (resto.length > 0) {
      const totalResto = resto.reduce((acc, d) => acc + d.total, 0);
      restoDetalhado = resto;
      lista.push({ label: `Outros (${resto.length})`, total: totalResto, cor: COR_OUTROS, ehOutros: true });
    }

    return { fatias: lista, total: totalGeral, partidosOutros: restoDetalhado };
  }, [dados, layoutComplexo]);

  const coresGrafico = layoutComplexo ? fatias.map((f) => f.cor) : CORES_SIMPLES;

  return (
    <div
      ref={chartRef}
      className={`flex gap-8 ${layoutComplexo ? 'grid grid-cols-1 lg:grid-cols-[300px_1fr] items-center justify-items-center' : 'flex-col lg:flex-row items-center justify-center'}`}
    >
      <div style={{ width: 300, height: 350, flexShrink: 0 }}>
        <PieChart width={300} height={350}>
          <Pie
            data={fatias}
            dataKey="total"
            nameKey="label"
            cx="50%"
            cy="50%"
            outerRadius={140}
            isAnimationActive={true}
            onMouseEnter={(_, index) => setAtivo(index)}
            onMouseLeave={() => setAtivo(null)}
          >
            {fatias.map((item, index) => (
              <Cell
                key={item.label}
                fill={layoutComplexo ? item.cor : coresGrafico[index % coresGrafico.length]}
                opacity={ativo === null || ativo === index ? 1 : 0.35}
                style={{ transition: 'opacity 0.15s' }}
              />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{ borderRadius: '8px', border: '1px solid #E5E7EB', fontSize: '13px' }}
            formatter={(value, name) => [
              `${value.toLocaleString('pt-BR')} (${((value / total) * 100).toFixed(1)}%)`,
              name,
            ]}
          />
        </PieChart>
      </div>

      {layoutComplexo ? (
        <LegendaCompleta fatias={fatias} total={total} partidosOutros={partidosOutros} ativo={ativo} setAtivo={setAtivo} />
      ) : (
        <LegendaSimples dados={fatias} total={total} ativo={ativo} setAtivo={setAtivo} />
      )}
    </div>
  );
}