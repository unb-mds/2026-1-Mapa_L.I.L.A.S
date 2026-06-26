import { useState } from 'react';

const LIMITE_INICIAL = 5;

export default function HistoricoTramitacao({ historico }) {
  const [verTodos, setVerTodos] = useState(false);
  const semDados = !historico || historico.length === 0;

  const eventosMostrados = verTodos ? historico : historico?.slice(0, LIMITE_INICIAL);
  const temMais = historico && historico.length > LIMITE_INICIAL;

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-6 mt-5">
      <h2 className="text-base font-semibold text-gray-800 mb-5 flex items-center gap-2">
        🕐 Histórico de Tramitação
      </h2>

      {semDados ? (
        <p className="text-sm text-gray-400 text-center py-4">
          Histórico de tramitação não disponível.
        </p>
      ) : (
        <div className="relative">
          <div className="absolute left-2 top-2 bottom-2 w-0.5 bg-gray-200" />
          <div className="space-y-6">
            {eventosMostrados.map((evento, index) => (
              <div key={index} className="flex gap-4 relative">
                <div className={`w-5 h-5 rounded-full border-2 flex-shrink-0 mt-0.5 z-10 ${
                  index === 0 ? 'bg-[#5B4FCF] border-[#5B4FCF]' : 'bg-white border-gray-300'
                }`} />
                <div>
                  <p className="text-sm font-semibold text-[#5B4FCF]">{evento.data}</p>
                  <p className="text-sm font-bold text-gray-800 mt-0.5">{evento.titulo}</p>
                  <p className="text-sm text-gray-500 mt-0.5 leading-relaxed">{evento.descricao}</p>
                </div>
              </div>
            ))}
          </div>

          {temMais && (
            <div className="mt-6 flex justify-center">
              <button
                onClick={() => setVerTodos(!verTodos)}
                className="text-sm font-semibold text-[#5B4FCF] hover:text-[#4338CA] transition-colors border border-[#5B4FCF] rounded-lg px-4 py-2 hover:bg-purple-50"
              >
                {verTodos
                  ? 'Ver menos'
                  : `Ver mais (${historico.length - LIMITE_INICIAL} etapas restantes)`}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}