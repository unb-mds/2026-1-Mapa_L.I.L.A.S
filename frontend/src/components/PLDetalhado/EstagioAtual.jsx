const ESTAGIOS = [
  { key: 'apresentacao', label: 'Apresentação' },
  { key: 'comissao',     label: 'Comissão' },
  { key: 'votacao',      label: 'Votação' },
  { key: 'sancao',       label: 'Sanção' },
];

export default function EstagioAtual({ estagioAtual }) {
  // Caso especial: PL rejeitado/arquivado
  if (estagioAtual === 'rejeitado') {
    return (
      <div className="mt-6">
        <h3 className="text-base font-semibold text-gray-800 mb-3">Estágio Atual</h3>
        <div className="flex items-center gap-2 px-4 py-3 bg-red-50 border border-red-200 rounded-lg">
          <span className="text-red-500">✖</span>
          <p className="text-sm text-red-700 font-medium">Projeto arquivado / rejeitado</p>
        </div>
      </div>
    );
  }

  // Caso especial: PL aprovado (mas ainda não sancionado)
  if (estagioAtual === 'aprovado') {
    return (
      <div className="mt-6">
        <h3 className="text-base font-semibold text-gray-800 mb-3">Estágio Atual</h3>
        <div className="flex items-center gap-2 px-4 py-3 bg-green-50 border border-green-200 rounded-lg">
          <span className="text-green-600">✅</span>
          <p className="text-sm text-green-700 font-medium">Projeto aprovado</p>
        </div>
      </div>
    );
  }

  const indiceAtual = ESTAGIOS.findIndex((e) => e.key === estagioAtual);

  return (
    <div className="mt-6">
      <h3 className="text-base font-semibold text-gray-800 mb-4">Estágio Atual</h3>
      <div className="flex items-center">
        {ESTAGIOS.map((estagio, index) => {
          const concluido = index < indiceAtual;
          const atual     = index === indiceAtual;
          const pendente  = index > indiceAtual;

          return (
            <div key={estagio.key} className="flex items-center flex-1 last:flex-none">
              <div className="flex flex-col items-center">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-all ${
                  concluido
                    ? 'bg-[#5B4FCF] text-white'
                    : atual
                    ? 'bg-[#5B4FCF] text-white ring-4 ring-purple-100'
                    : 'bg-gray-200 text-gray-400'
                }`}>
                  {concluido ? '✓' : atual ? '👤' : ''}
                </div>
                <span className={`text-xs mt-2 font-medium text-center whitespace-nowrap ${
                  pendente ? 'text-gray-400' : 'text-[#5B4FCF]'
                }`}>
                  {estagio.label}
                </span>
              </div>

              {index < ESTAGIOS.length - 1 && (
                <div className={`flex-1 h-0.5 mx-1 mb-5 ${
                  index < indiceAtual ? 'bg-[#5B4FCF]' : 'bg-gray-200'
                }`} />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}