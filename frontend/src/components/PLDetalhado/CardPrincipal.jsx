import EstagioAtual from './EstagioAtual';

const STATUS_CONFIG = {
  em_tramitacao: { label: 'EM TRAMITAÇÃO', className: 'bg-yellow-400 text-yellow-900' },
  em_votacao:    { label: 'EM VOTAÇÃO',    className: 'bg-orange-500 text-white' },
  aprovado:      { label: 'APROVADO',      className: 'bg-green-500 text-white' },
  arquivado:     { label: 'ARQUIVADO',     className: 'bg-red-500 text-white' },
};

const METADADOS = [
  { label: 'Data de Apresentação', campo: 'data_apresentacao' },
  { label: 'Autor',                campo: 'autor_nome' },
  { label: 'Origem',               campo: 'casa' },
  { label: 'Regime',               campo: 'regime' },
];

function valorOuVazio(valor) {
  if (valor === null || valor === undefined || valor === '') return 'Não informado';
  return valor;
}

export default function CardPrincipal({ pl }) {
  const status = STATUS_CONFIG[pl.status] ?? STATUS_CONFIG.em_tramitacao;

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-6">
      {/* Número + Badge */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <h1 className="text-2xl font-bold text-gray-900">
          PL {pl.numero}/{pl.ano}
        </h1>
        <span className={`text-xs font-bold px-3 py-1.5 rounded-full whitespace-nowrap flex-shrink-0 ${status.className}`}>
          {status.label}
        </span>
      </div>

      {/* Ementa */}
      <p className="text-sm text-gray-600 leading-relaxed mb-6">
        {valorOuVazio(pl.ementa)}
      </p>

      {/* Metadados em grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-4 border-t border-gray-100">
        {METADADOS.map(({ label, campo }) => (
          <div key={campo}>
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-0.5">
              {label}
            </p>
            <p className="text-sm font-medium text-gray-800">
              {valorOuVazio(pl[campo])}
            </p>
          </div>
        ))}
      </div>

      {/* Timeline de estágio */}
      <EstagioAtual estagioAtual={pl.estagio_atual} />
    </div>
  );
}