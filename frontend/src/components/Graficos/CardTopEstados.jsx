export default function CardTopEstados({ estados }) {
  const maxPls = Math.max(...estados.map((e) => e.total_pls));

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-5">
      <h3 className="text-sm font-semibold text-gray-800 mb-4 flex items-center gap-2">
        📈 Top 5 Estados
      </h3>

      <div className="space-y-4">
        {estados.map((estado) => {
          const largura = Math.round((estado.total_pls / maxPls) * 100);
          return (
            <div key={estado.uf}>
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm text-gray-700">
                  {estado.estado} ({estado.uf})
                </span>
                <span className="text-sm font-bold text-[#5B4FCF]">
                  {estado.total_pls.toLocaleString('pt-BR')} PLs
                </span>
              </div>
              <div className="w-full bg-gray-100 rounded-full h-1.5">
                <div
                  className="bg-[#5B4FCF] h-1.5 rounded-full transition-all duration-500"
                  style={{ width: `${largura}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}