const CORES_AVATAR = [
  'bg-purple-200 text-purple-800',
  'bg-pink-200 text-pink-800',
  'bg-emerald-200 text-emerald-800',
];

export default function CardParlamentaresAtivos({ parlamentares }) {
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-5">
      <h3 className="text-sm font-semibold text-gray-800 mb-4 flex items-center gap-2">
        👥 Parlamentares Ativos
      </h3>

      <div className="space-y-4">
        {parlamentares.map((p, index) => (
          <div key={p.nome} className="flex items-start gap-3">
            {/* Avatar */}
            <div className={`w-9 h-9 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 ${CORES_AVATAR[index % CORES_AVATAR.length]}`}>
              {p.iniciais}
            </div>

            {/* Info */}
            <div className="flex-1 min-w-0">
              <div className="flex items-start justify-between gap-2">
                <p className="text-sm font-semibold text-gray-800 leading-tight">{p.nome}</p>
                <span className="text-xs bg-gray-100 text-gray-500 px-1.5 py-0.5 rounded flex-shrink-0">
                  {p.uf}
                </span>
              </div>
              <div className="flex items-center justify-between mt-0.5">
                <p className="text-xs text-gray-400">{p.descricao}</p>
                <span className="text-xs font-bold text-[#5B4FCF]">
                  {p.total_propostas} prop.
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 pt-3 border-t border-gray-100 text-center">
        <button className="text-sm font-semibold text-[#5B4FCF] hover:text-[#4338CA] transition-colors">
          Ver todos →
        </button>
      </div>
    </div>
  );
}