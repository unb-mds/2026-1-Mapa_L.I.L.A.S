import { useNavigate } from 'react-router-dom';

export default function CardCTADashboard() {
  const navigate = useNavigate();
  return (
    <div className="bg-white border border-gray-200 border-l-4 border-l-[#5B4FCF] rounded-xl p-6 h-full flex flex-col items-center text-center justify-center gap-4">
      <div className="w-12 h-12 rounded-full bg-purple-100 flex items-center justify-center">
        <span className="text-xl">📊</span>
      </div>
      <div>
        <h3 className="text-base font-bold text-gray-800 mb-1">Quer explorar os dados em detalhes?</h3>
        <p className="text-sm text-gray-500 leading-relaxed">Acesse o painel completo com gráficos, filtros e rankings legislativos.</p>
      </div>
      <button
        onClick={() => navigate('/graficos/dashboard')}
        className="flex items-center gap-2 px-5 py-2.5 bg-[#5B4FCF] hover:bg-[#4338CA] text-white text-sm font-semibold rounded-lg transition-colors"
      >
        Ver Dashboard Detalhado →
      </button>
    </div>
  );
}