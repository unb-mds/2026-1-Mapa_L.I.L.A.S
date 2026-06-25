const OPCOES = [
  { label: 'PARTIDO',        valor: 'partido' },
  { label: 'ESTADO',         valor: 'estado' },
  { label: 'GÊNERO DO AUTOR',valor: 'genero' },
  { label: 'MÊS',            valor: 'mes' },
];

export default function SeletorComparar({ ativo, onChange }) {
  return (
    <div className="mb-5">
      <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
        Comparar por:
      </p>
      <div className="flex flex-wrap gap-2">
        {OPCOES.map((op) => (
          <button
            key={op.valor}
            onClick={() => onChange(op.valor)}
            className={`px-4 py-2 text-sm font-semibold rounded-lg border transition-colors ${
              ativo === op.valor
                ? 'bg-[#5B4FCF] text-white border-[#5B4FCF]'
                : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
            }`}
          >
            {op.label}
          </button>
        ))}
      </div>
    </div>
  );
}