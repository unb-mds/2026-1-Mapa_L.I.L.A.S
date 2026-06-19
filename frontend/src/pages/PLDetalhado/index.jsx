import { useParams, Link } from 'react-router-dom';
import { usePLDetalhado } from '../../hooks/usePLDetalhado';
import NavBar from '../../components/NavBar';
import Footer from '../../components/Footer';
import Breadcrumb from '../../components/PLDetalhado/Breadcrumb';
import CardPrincipal from '../../components/PLDetalhado/CardPrincipal';
import HistoricoTramitacao from '../../components/PLDetalhado/HistoricoTramitacao';
import CardIntegraPDF from '../../components/PLDetalhado/CardIntegraPDF';
import CardSincronizacao from '../../components/PLDetalhado/CardSincronizacao';
import CardTemas from '../../components/PLDetalhado/CardTemas';

function SkeletonDetalhado() {
  return (
    <div className="animate-pulse">
      <div className="h-4 bg-gray-200 rounded w-64 mb-6" />
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-5">
          <div className="bg-white border border-gray-200 rounded-xl p-6 space-y-4">
            <div className="h-7 bg-gray-200 rounded w-36" />
            <div className="space-y-2">
              <div className="h-3 bg-gray-200 rounded w-full" />
              <div className="h-3 bg-gray-200 rounded w-5/6" />
              <div className="h-3 bg-gray-200 rounded w-4/6" />
            </div>
            <div className="grid grid-cols-4 gap-4 pt-4">
              {[1,2,3,4].map(i => <div key={i} className="h-8 bg-gray-200 rounded" />)}
            </div>
            <div className="h-16 bg-gray-200 rounded mt-4" />
          </div>
          <div className="bg-white border border-gray-200 rounded-xl p-6 h-48" />
        </div>
        <div className="space-y-4">
          <div className="bg-white border border-gray-200 rounded-xl p-6 h-40" />
          <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 h-24" />
          <div className="bg-white border border-gray-200 rounded-xl p-5 h-20" />
        </div>
      </div>
    </div>
  );
}

function NaoEncontrado() {
  return (
    <div className="flex flex-col items-center justify-center py-24 gap-4">
      <p className="text-gray-500 text-center">Projeto de Lei não encontrado.</p>
      <Link
        to="/projetos"
        className="px-5 py-2 text-sm font-semibold bg-[#5B4FCF] text-white rounded-lg hover:bg-[#4338CA] transition-colors"
      >
        Voltar para a listagem
      </Link>
    </div>
  );
}

export default function PLDetalhado() {
  const { casa, numero, ano } = useParams();
  const { pl, loading, error } = usePLDetalhado(casa, numero, ano);

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <NavBar />
      <main className="flex-1 max-w-7xl mx-auto w-full px-6 py-10">
        {loading && <SkeletonDetalhado />}
        {!loading && error === 'not_found' && <NaoEncontrado />}
        {!loading && error && error !== 'not_found' && (
          <div className="flex flex-col items-center justify-center py-24 gap-4">
            <p className="text-gray-500 text-center">Não foi possível carregar o projeto. Tente novamente.</p>
            <Link to="/projetos" className="text-sm text-[#5B4FCF] hover:underline">
              Voltar para a listagem
            </Link>
          </div>
        )}
        {!loading && !error && pl && (
          <>
            <Breadcrumb numero={pl.numero} ano={pl.ano} />
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 space-y-5">
                <CardPrincipal pl={pl} />
                {/* Passa estagioAtual para o Histórico saber se o PL foi arquivado */}
                <HistoricoTramitacao
                  historico={pl.historico}
                  estagioAtual={pl.estagio_atual}
                />
              </div>
              <div className="space-y-4">
                <CardIntegraPDF urlPdf={pl.url_pdf} />
                <CardSincronizacao />
                <CardTemas temas={pl.temas} />
              </div>
            </div>
          </>
        )}
      </main>
      <Footer />
    </div>
  );
}