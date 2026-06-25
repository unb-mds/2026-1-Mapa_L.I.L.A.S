export default function CardIndicadores({ indicadores, loading }) {
  const cards = [
    {
      valor: loading ? '—' : (indicadores?.total_pls ?? 0).toLocaleString('pt-BR'),
      label: 'TOTAL DE PLS',
    },
    {
      valor: loading ? '—' : (indicadores?.partido_mais_ativo ?? '—'),
      label: 'PARTIDO COM MAIS PROPOSTAS',
    },
    {
      valor: loading ? '—' : (indicadores?.estado_mais_ativo ?? '—'),
      label: 'ESTADO COM MAIS PROPOSTAS',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-5">
      {cards.map((card) => (
        <div
          key={card.label}
          className="bg-white border border-gray-200 rounded-xl p-5 text-center"
        >
          {loading ? (
            <div className="animate-pulse">
              <div className="h-8 bg-gray-200 rounded w-24 mx-auto mb-2" />
              <div className="h-3 bg-gray-200 rounded w-32 mx-auto" />
            </div>
          ) : (
            <>
              <p className="text-3xl font-bold text-[#5B4FCF]">{card.valor}</p>
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mt-1">
                {card.label}
              </p>
            </>
          )}
        </div>
      ))}
    </div>
  );
}