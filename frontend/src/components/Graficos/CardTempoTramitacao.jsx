const BADGE_CONFIG = {
  aumento: { icone: '↗', bg: 'bg-pink-50', texto: 'text-red-700', sinal: '+' },
  reducao: { icone: '↘', bg: 'bg-green-50', texto: 'text-green-700', sinal: '-' },
};

export default function CardTempoTramitacao({ dados }) {
  const badge = BADGE_CONFIG[dados.tendencia] ?? BADGE_CONFIG.aumento;

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-6 relative flex flex-col items-center text-center justify-center h-full">
      <span className="absolute top-5 right-5 text-5xl opacity-20 select-none">⏳</span>

      <h2 className="text-xl font-semibold text-gray-700 mb-1">
        Tempo Médio de Tramitação
      </h2>

      <p className="text-sm text-gray-400 mb-6">
        nos últimos 12 meses
      </p>

      <div className="flex items-baseline gap-3 mb-6">
        <span className="text-7xl font-bold text-[#5B4FCF]">
          {dados.dias.toLocaleString('pt-BR')}
        </span>
        <span className="text-2xl text-gray-400">dias</span>
      </div>

      <span className={`inline-flex items-center gap-1 px-4 py-1.5 rounded-full text-base font-medium ${badge.bg} ${badge.texto}`}>
        {badge.icone} {badge.sinal}{dados.variacao_percentual}% vs ano anterior
      </span>
    </div>
  );
}