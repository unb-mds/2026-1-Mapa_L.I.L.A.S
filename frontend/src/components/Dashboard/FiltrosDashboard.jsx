const UFS = ['AC','AL','AM','AP','BA','CE','DF','ES','GO','MA','MG','MS','MT',
             'PA','PB','PE','PI','PR','RJ','RN','RO','RR','RS','SC','SE','SP','TO'];

const MESES = [
  { label: 'Janeiro',   valor: '1' },
  { label: 'Fevereiro', valor: '2' },
  { label: 'Março',     valor: '3' },
  { label: 'Abril',     valor: '4' },
  { label: 'Maio',      valor: '5' },
  { label: 'Junho',     valor: '6' },
  { label: 'Julho',     valor: '7' },
  { label: 'Agosto',    valor: '8' },
  { label: 'Setembro',  valor: '9' },
  { label: 'Outubro',   valor: '10' },
  { label: 'Novembro',  valor: '11' },
  { label: 'Dezembro',  valor: '12' },
];

function Select({ label, value, onChange, children }) {
  return (
    <div>
      <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
        {label}
      </label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white focus:outline-none focus:border-[#5B4FCF] focus:ring-1 focus:ring-[#5B4FCF]"
      >
        {children}
      </select>
    </div>
  );
}

export default function FiltrosDashboard({ compararPor, filtros, onChange }) {
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-5 mb-5">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Estado — oculto quando comparar por estado */}
        {compararPor !== 'estado' && (
          <Select label="Estado" value={filtros.estado} onChange={(v) => onChange('estado', v)}>
            <option value="">Todos os Estados</option>
            {UFS.map((uf) => <option key={uf} value={uf}>{uf}</option>)}
          </Select>
        )}

        {/* Partido — oculto quando comparar por partido */}
        {compararPor !== 'partido' && (
          <Select label="Partido" value={filtros.partido} onChange={(v) => onChange('partido', v)}>
            <option value="">Todos os Partidos</option>
            {['PT','PL','MDB','UNIÃO','PSB','PSOL','PSD','PP','REPUBLICANOS','PDT'].map((p) => (
              <option key={p} value={p}>{p}</option>
            ))}
          </Select>
        )}

        {/* Gênero — oculto quando comparar por genero */}
        {compararPor !== 'genero' && (
          <Select label="Gênero do Autor" value={filtros.genero} onChange={(v) => onChange('genero', v)}>
            <option value="">Todos</option>
            <option value="masculino">Masculino</option>
            <option value="feminino">Feminino</option>
          </Select>
        )}

        {/* Mês — oculto quando comparar por mes */}
        {compararPor !== 'mes' && (
          <Select label="Período (Mês)" value={filtros.mes} onChange={(v) => onChange('mes', v)}>
            <option value="">Todos os Meses</option>
            {MESES.map((m) => <option key={m.valor} value={m.valor}>{m.label}</option>)}
          </Select>
        )}
      </div>
    </div>
  );
}