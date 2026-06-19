const BADGE_CONFIG = {
  aumento: { icone: '↗', bg: 'bg-pink-50', texto: 'text-red-700', sinal: '+' },
  reducao: { icone: '↘', bg: 'bg-green-50', texto: 'text-green-700', sinal: '-' },
};

export default function CardTempoTramitacao({ dados }) {
  const badge = BADGE_CONFIG[dados.tendencia] ?? BADGE_CONFIG.aumento;

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-6 relative flex flex-col items-center text-center h-full">
      <span className="absolute top-5 right-5 text-4xl opacity-20 select-none">⏳</span>

      <h2 className="text-base font-semibold text-gray-700 mb-4">
        Tempo Médio de Tramitação
      </h2>

      <div className="flex items-baseline gap-2 mb-2">
        <span className="text-5xl font-bold text-[#5B4FCF]">
          {dados.dias.toLocaleString('pt-BR')}
        </span>
        <span className="text-lg text-gray-400">dias</span>
      </div>

      <p className="text-sm text-gray-500 mb-4">
        úteis em média para PLs de feminicídio
      </p>

      <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium ${badge.bg} ${badge.texto}`}>
        {badge.icone} {badge.sinal}{dados.variacao_percentual}% vs ano anterior
      </span>
    </div>
  );
}