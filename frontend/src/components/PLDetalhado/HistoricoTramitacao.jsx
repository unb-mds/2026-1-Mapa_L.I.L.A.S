export default function HistoricoTramitacao({ historico, estagioAtual }) {
  const arquivado = estagioAtual === 'rejeitado';
  const semDados = !historico || historico.length === 0;

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-6 mt-5">
      <h2 className="text-base font-semibold text-gray-800 mb-5 flex items-center gap-2">
        🕐 Histórico de Tramitação
      </h2>

      {(arquivado || semDados) ? (
        <p className="text-sm text-gray-400 text-center py-4">
          {arquivado
            ? 'Histórico não disponível para projetos arquivados.'
            : 'Histórico de tramitação não disponível.'}
        </p>
      ) : (
        <div className="relative">
          <div className="absolute left-2 top-2 bottom-2 w-0.5 bg-gray-200" />
          <div className="space-y-6">
            {historico.map((evento, index) => (
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
        </div>
      )}
    </div>
  );
}