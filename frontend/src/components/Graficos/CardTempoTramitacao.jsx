const BADGE_CONFIG = {
  aumento: { icone: '↗', bg: 'bg-pink-50', texto: 'text-red-700', sinal: '+' },
  reducao: { icone: '↘', bg: 'bg-green-50', texto: 'text-green-700', sinal: '-' },
};

export default function CardTempoTramitacao({ dados }) {
  const badge = BADGE_CONFIG[dados.tendencia] ?? BADGE_CONFIG.aumento;

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-6 relative flex flex-col h-full">
      {/* Header alinhado à esquerda, igual aos outros cards */}
      <div className="flex items-start justify-between mb-1">
        <div className="flex items-center gap-2">
          <span className="text-[#5B4FCF] text-lg">⏳</span>
          <h2 className="text-base font-semibold text-gray-700">
            Tempo Médio de Tramitação
          </h2>
        </div>
        <span className="text-xs font-medium text-[#5B4FCF] bg-[#5B4FCF]/10 px-2.5 py-1 rounded-md">
           Geral
        </span>
      </div>

      {/* Número centralizado, ocupando o corpo do card */}
      <div className="flex-1 flex items-center justify-center">
        <div className="flex items-baseline gap-3">
          <span className="text-7xl font-bold text-[#5B4FCF]">
            {dados.dias.toLocaleString('pt-BR')}
          </span>
          <span className="text-2xl text-gray-400">dias</span>
        </div>
      </div>
    </div>
  );
}