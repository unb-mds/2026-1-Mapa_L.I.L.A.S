import { useNavigate } from 'react-router-dom';

const STATUS_CONFIG = {
  em_tramitacao: { label: 'EM TRAMITAÇÃO', className: 'bg-yellow-400 text-yellow-900' },
  aprovado:      { label: 'APROVADO',      className: 'bg-green-500 text-white' },
  arquivado:     { label: 'ARQUIVADO',     className: 'bg-red-500 text-white' },
};

const MESES = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'];

function formatarData(dataISO) {
  const [ano, mes, dia] = dataISO.split('-');
  return `${dia} ${MESES[parseInt(mes) - 1]} ${ano}`;
}

// Converte o valor de "casa" do backend para o formato da URL
function casaParaUrl(casa) {
  if (!casa) return 'senado';
  const c = casa.toLowerCase();
  if (c.includes('camara') || c.includes('câmara') || c.includes('deputados')) return 'camara';
  return 'senado';
}

export default function CardPL({ projeto }) {
  const navigate = useNavigate();
  const status = STATUS_CONFIG[projeto.status] ?? STATUS_CONFIG.em_tramitacao;

  const handleVerDetalhes = () => {
    const casaUrl = casaParaUrl(projeto.casa);
    navigate(`/projetos/${casaUrl}/${projeto.numero}/${projeto.ano}`, {
      state: {
        numero: projeto.numero,
        ano: projeto.ano,
        status: projeto.status,
        casa: projeto.casa,
        autor_nome: projeto.autor_nome,
        autor_partido: projeto.autor_partido,
        autor_uf: projeto.autor_uf,
        ementa: projeto.ementa,
      }
    });
  };

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-5 flex flex-col gap-3 hover:shadow-lg hover:scale-[1.01] transition-all duration-200 cursor-default">
      <div className="flex items-start justify-between gap-2">
        <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
          {projeto.casa}
        </span>
        <span className={`text-xs font-bold px-2.5 py-1 rounded-full whitespace-nowrap ${status.className}`}>
          {status.label}
        </span>
      </div>

      <div>
        <h3 className="text-xl font-bold text-[#5B4FCF]">
          PL {projeto.numero}/{projeto.ano}
        </h3>
        <p className="text-sm text-gray-500 mt-1">
          👤 {projeto.autor_nome} ({projeto.autor_partido} - {projeto.autor_uf})
        </p>
      </div>

      <p className="text-sm text-gray-700 leading-relaxed line-clamp-3 flex-1">
        {projeto.ementa}
      </p>

      <div className="flex items-end justify-between pt-3 border-t border-gray-100">
        <div>
          <p className="text-xs text-gray-400 uppercase tracking-wide">Última Atualização</p>
          <p className="text-xs text-gray-600 mt-0.5">📅 {formatarData(projeto.ultima_atualizacao)}</p>
        </div>
        <button
          onClick={handleVerDetalhes}
          className="text-sm font-semibold text-[#5B4FCF] hover:text-[#4338CA] transition-colors"
        >
          VER DETALHES →
        </button>
      </div>
    </div>
  );
}