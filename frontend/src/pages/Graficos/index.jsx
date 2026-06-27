import { useGraficosResumo } from '../../hooks/useGraficosResumo';
import NavBar from '../../components/NavBar';
import Footer from '../../components/Footer';
import CardTempoTramitacao from '../../components/Graficos/CardTempoTramitacao';
import CardCTADashboard from '../../components/Graficos/CardCTADashboard';
import CardTopEstados from '../../components/Graficos/CardTopEstados';
import CardParlamentaresAtivos from '../../components/Graficos/CardParlamentaresAtivos';

function SkeletonGraficos() {
  return (
    <div className="animate-pulse">
      <div className="h-8 bg-gray-200 rounded w-96 mb-2" />
      <div className="h-4 bg-gray-200 rounded w-72 mb-8" />
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white border border-gray-200 rounded-xl p-6 h-64" />
        <div className="bg-white border border-gray-200 rounded-xl p-5 h-64" />
        <div className="bg-white border border-gray-200 rounded-xl p-6 h-64" />
        <div className="bg-white border border-gray-200 rounded-xl p-5 h-64" />
      </div>
    </div>
  );
}

export default function Graficos() {
  const { dados, loading, error, recarregar } = useGraficosResumo();

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <NavBar />

      <main className="flex-1 max-w-7xl mx-auto w-full px-6 py-10">
        {loading && <SkeletonGraficos />}

        {!loading && error && (
          <div className="flex flex-col items-center justify-center py-24 gap-4">
            <p className="text-gray-500 text-center">
              Não foi possível carregar os dados. Tente novamente.
            </p>
            <button
              onClick={recarregar}
              className="px-5 py-2 text-sm font-semibold bg-[#5B4FCF] text-white rounded-lg hover:bg-[#4338CA] transition-colors"
            >
              Tentar novamente
            </button>
          </div>
        )}

        {!loading && !error && dados && (
          <>
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Mapa da Legislação de Feminicídio
              </h1>
              <p className="text-gray-500 text-sm leading-relaxed max-w-xl">
                Acompanhe a densidade de propostas legislativas sobre feminicídio por estado em tempo real.
              </p>
            </div>

            {/* Grid 2x2 com todas as células de altura igual */}
            <div
              className="grid grid-cols-1 lg:grid-cols-2 gap-6"
              style={{ gridAutoRows: '1fr' }}
            >
              <div className="h-full">
                <CardParlamentaresAtivos parlamentares={dados.parlamentares_ativos} />
              </div>
              <div className="h-full">
                <CardTopEstados estados={dados.top_estados} />
              </div>
              <div className="h-full">
                <CardTempoTramitacao dados={dados.tempo_medio_tramitacao} />
              </div>
              <div className="h-full">
                <CardCTADashboard />
              </div>
            </div>
          </>
        )}
      </main>

      <Footer />
    </div>
  );
}