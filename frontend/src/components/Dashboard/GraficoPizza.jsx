import { PieChart, Pie, Cell, Tooltip } from 'recharts';

const CORES = ['#5B4FCF','#8B7DD8','#B5AEED','#D4CFEE','#E8E5F7','#3D3399','#7C6FBF','#A89BD6'];

export default function GraficoPizza({ dados, chartRef }) {
  const total = dados.reduce((acc, d) => acc + d.total, 0);

  return (
    <div ref={chartRef} className="flex flex-col lg:flex-row items-center justify-center gap-8">
      {/* Gráfico com tamanho fixo para centralizar corretamente */}
      <div style={{ width: 300, height: 350, flexShrink: 0 }}>
        <PieChart width={300} height={350}>
          <Pie
            data={dados}
            dataKey="total"
            nameKey="label"
            cx="50%"
            cy="50%"
            outerRadius={140}
            isAnimationActive={true}
          >
            {dados.map((_, index) => (
              <Cell key={index} fill={CORES[index % CORES.length]} />
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

      {/* Legenda lateral */}
      <div className="flex flex-col gap-3 min-w-48">
        {dados.map((item, index) => (
          <div key={item.label} className="flex items-center gap-3">
            <div
              className="w-3 h-3 rounded-full flex-shrink-0"
              style={{ backgroundColor: CORES[index % CORES.length] }}
            />
            <div>
              <p className="text-sm font-semibold text-gray-800">{item.label}</p>
              <p className="text-xs text-gray-500">
                {item.total.toLocaleString('pt-BR')} ({((item.total / total) * 100).toFixed(1)}%)
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}