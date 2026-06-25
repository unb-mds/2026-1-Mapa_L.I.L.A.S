import { Link } from 'react-router-dom';
import NavBar from '../../components/NavBar';
import Footer from '../../components/Footer';
import { useStats } from '../../hooks/useStats';

const OBJECTIVES = [
  {
    title: 'Transparência Legislativa',
    description:
      'Tornamos acessíveis os dados sobre proposições legislativas relacionadas ao combate ao feminicídio e à violência doméstica, reunidos em um único lugar.',
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" className="w-7 h-7 text-[#5B4FCF]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
      </svg>
    ),
  },
  {
    title: 'Monitoramento Contínuo',
    description:
      'Acompanhamos diariamente a tramitação de projetos de lei na Câmara dos Deputados e no Senado Federal, mantendo os dados sempre atualizados.',
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" className="w-7 h-7 text-[#5B4FCF]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
    ),
  },
  {
    title: 'Engajamento Cívico',
    description:
      'Transformamos dados complexos do legislativo em informações claras para que cidadãos, pesquisadores e organizações possam atuar com mais efetividade.',
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" className="w-7 h-7 text-[#5B4FCF]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
    ),
  },
];

const TEAM = [
  { name: 'Alice Moura', github: 'https://github.com' },
  { name: 'Alice Rodrigues', github: 'https://github.com' },
  { name: 'Eduardo Rodrigues', github: 'https://github.com' },
  { name: 'Luana Barbosa', github: 'https://github.com' },
  { name: 'Rafael Schetinger', github: 'https://github.com' },
  { name: 'Renan Santos', github: 'https://github.com' },
];

const GITHUB_URL = 'https://github.com/unb-mds/2026-1-Mapa_L.I.L.A.S';
const DOCS_URL = 'https://unb-mds.github.io/2026-1-Mapa_L.I.L.A.S';
const FIGMA_URL = 'https://www.figma.com/board/JerWZI6mxVFXDsDmY6ZMap';

export default function Inicio() {
  const { stats, loading } = useStats();
  const STATS = [
  {
    label: 'Total de Projetos de Feminicídio',
    value: loading ? '--' : stats.total,
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6 text-[#5B4FCF]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
    ),
  },
  {
    label: 'Em Tramitação',
    value: loading ? '--' : stats.emTramitacao,
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6 text-yellow-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
      </svg>
    ),
  },
  {
    label: 'Aprovados',
    value: loading ? '--' : stats.aprovados,
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
  },
  {
    label: 'Arquivados',
    value: loading ? '--' : stats.arquivados,
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8l1 12a2 2 0 002 2h8a2 2 0 002-2L19 8m-9 4h4" />
      </svg>
    ),
  },
];
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <NavBar />

      {/* Hero */}
      <section className="bg-gradient-to-b from-[#f0eeff] to-gray-50 py-20 px-6 text-center">
        <div className="max-w-3xl mx-auto">
          <h1 className="text-5xl md:text-6xl font-black text-gray-900 leading-tight mb-6 uppercase tracking-tight">
            Monitoramento Integral de Leis de Feminicídio
          </h1>
          <p className="text-gray-500 text-base md:text-lg leading-relaxed mb-10 max-w-xl mx-auto">
            Informação e transparência para o combate à violência contra a mulher.
            Monitoramento diário de Projetos de Lei na Câmara e no Senado.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              to="/projetos"
              className="flex items-center gap-2 bg-[#5B4FCF] text-white font-semibold px-6 py-3 rounded-lg hover:bg-[#4338CA] transition-colors text-sm"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              VER PROJETOS DE LEI
            </Link>
            <Link
              to="/graficos"
              className="flex items-center gap-2 border-2 border-[#5B4FCF] text-[#5B4FCF] font-semibold px-6 py-3 rounded-lg hover:bg-[#f0eeff] transition-colors text-sm"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              VER GRÁFICOS
            </Link>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="max-w-7xl mx-auto w-full px-6 -mt-6 mb-16">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {STATS.map((stat) => (
            <div
              key={stat.label}
              className="bg-white border border-gray-200 rounded-xl p-5 flex items-start justify-between shadow-sm hover:shadow-md transition-shadow"
            >
              <div>
                <p className="text-xs text-gray-500 leading-snug mb-2">{stat.label}</p>
                <p className="text-3xl font-black text-gray-900">{stat.value}</p>
              </div>
              <div className="mt-1">{stat.icon}</div>
            </div>
          ))}
        </div>
      </section>

      {/* O que é o L.I.L.A.S. */}
      <section className="max-w-7xl mx-auto w-full px-6 mb-16">
        <div className="bg-gradient-to-br from-[#5B4FCF] to-[#7c6fe0] rounded-2xl p-10 text-white shadow-md flex flex-col md:flex-row gap-8 items-center">
          <div className="flex-1">
            <p className="text-xs font-bold uppercase tracking-widest text-[#c4bbf7] mb-2">O nome por trás da causa</p>
            <h2 className="text-3xl font-black mb-4 leading-tight">
              O que significa <span className="text-[#e9e4ff]">L.I.L.A.S.</span>?
            </h2>
            <p className="text-[#d4ccf7] text-sm leading-relaxed mb-4">
              <strong className="text-white">L.I.L.A.S.</strong> é a sigla para{' '}
              <strong className="text-white">Legislativo Informativo de Leis de Acompanhamento Social</strong> — um nome
              que traduz exatamente o que esta plataforma faz: acompanhar, informar e dar visibilidade ao que acontece
              no legislativo sobre a proteção das mulheres.
            </p>
            <p className="text-[#d4ccf7] text-sm leading-relaxed">
              A escolha não foi por acaso. O <strong className="text-white">lilás</strong> é reconhecido
              mundialmente como a cor símbolo da luta contra o feminicídio e pela defesa dos direitos das mulheres.
              Ao unir o acrônimo à cor, o projeto reafirma seu compromisso: não somos apenas uma ferramenta de dados —
              somos parte de um movimento por justiça e transparência.
            </p>
          </div>
          <div className="flex-shrink-0 flex flex-col items-center gap-2">
            <div className="w-24 h-24 rounded-full bg-white/10 border-4 border-white/30 flex items-center justify-center">
              <span className="text-4xl font-black text-white">🌸</span>
            </div>
            <span className="text-xs text-[#c4bbf7] text-center max-w-[120px] leading-snug">
              Cor símbolo da luta contra o feminicídio
            </span>
          </div>
        </div>
      </section>

      {/* Objetivos */}
      <section className="max-w-7xl mx-auto w-full px-6 mb-16">
        <h2 className="text-2xl font-bold text-gray-900 mb-8 text-center">Nossos Objetivos</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {OBJECTIVES.map((obj) => (
            <div
              key={obj.title}
              className="bg-white border border-gray-200 rounded-xl p-7 shadow-sm hover:shadow-md transition-shadow"
            >
              <div className="w-12 h-12 bg-[#f0eeff] rounded-lg flex items-center justify-center mb-4">
                {obj.icon}
              </div>
              <h3 className="text-base font-bold text-gray-900 mb-2">{obj.title}</h3>
              <p className="text-sm text-gray-500 leading-relaxed">{obj.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Sobre */}
      <section className="max-w-7xl mx-auto w-full px-6 mb-16">
        <div className="bg-white border border-gray-200 rounded-2xl p-10 text-center shadow-sm">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Sobre o Projeto</h2>
          <p className="text-gray-500 text-sm leading-relaxed max-w-2xl mx-auto mb-6">
            Uma plataforma independente, desenvolvida por estudantes da{' '}
            <strong className="text-gray-700">Universidade de Brasília (UnB)</strong>, dedicada ao monitoramento e
            análise de proposições legislativas relacionadas aos direitos da mulher e ao combate ao feminicídio.
            Transformamos dados complexos em informações claras para fortalecer a transparência e o engajamento cívico.
          </p>
          <a
            href={GITHUB_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 border border-gray-300 text-gray-600 font-semibold px-5 py-2 rounded-lg hover:bg-gray-50 transition-colors text-sm"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 0C5.374 0 0 5.373 0 12c0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.509 11.509 0 0112 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 21.797 24 17.3 24 12c0-6.627-5.373-12-12-12z" />
            </svg>
            Ver Mais Sobre o Projeto
          </a>
        </div>
      </section>

      {/* Contato e Equipe */}
      <section className="max-w-7xl mx-auto w-full px-6 mb-16">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

          {/* Equipe */}
          <div className="bg-white border border-gray-200 rounded-2xl p-8 shadow-sm">
            <h2 className="text-lg font-bold text-gray-900 mb-6">Equipe</h2>
            <div className="grid grid-cols-2 gap-3">
              {TEAM.map((member) => (
                <a
                  key={member.name}
                  href={member.github}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 text-sm text-gray-600 hover:text-[#5B4FCF] transition-colors"
                >
                  <div className="w-7 h-7 rounded-full bg-[#f0eeff] flex items-center justify-center flex-shrink-0">
                    <span className="text-[#5B4FCF] text-xs font-bold">{member.name[0]}</span>
                  </div>
                  {member.name}
                </a>
              ))}
            </div>
          </div>

          {/* Contato */}
          <div className="bg-white border border-gray-200 rounded-2xl p-8 shadow-sm">
            <h2 className="text-lg font-bold text-gray-900 mb-6">Contato & Links</h2>
            <div className="flex flex-col gap-4">

              <a
                href={GITHUB_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-3 text-sm text-gray-600 hover:text-[#5B4FCF] transition-colors"
              >
                <div className="w-9 h-9 rounded-lg bg-gray-100 flex items-center justify-center">
                  <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 0C5.374 0 0 5.373 0 12c0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.509 11.509 0 0112 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 21.797 24 17.3 24 12c0-6.627-5.373-12-12-12z" />
                  </svg>
                </div>
                <div>
                  <p className="font-semibold text-gray-800">GitHub</p>
                  <p className="text-xs text-gray-400">unb-mds/2026-1-Mapa_L.I.L.A.S</p>
                </div>
              </a>

              <a
                href={DOCS_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-3 text-sm text-gray-600 hover:text-[#5B4FCF] transition-colors"
              >
                <div className="w-9 h-9 rounded-lg bg-gray-100 flex items-center justify-center">
                  <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                  </svg>
                </div>
                <div>
                  <p className="font-semibold text-gray-800">Documentação</p>
                  <p className="text-xs text-gray-400">unb-mds.github.io/2026-1-Mapa_L.I.L.A.S</p>
                </div>
              </a>

              <a
                href={FIGMA_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-3 text-sm text-gray-600 hover:text-[#5B4FCF] transition-colors"
              >
              </a>

              <div className="flex items-center gap-3 text-sm text-gray-600">
                <div className="w-9 h-9 rounded-lg bg-gray-100 flex items-center justify-center">
                  <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                  </svg>
                </div>
                <div>
                  <p className="font-semibold text-gray-800">Universidade de Brasília</p>
                  <p className="text-xs text-gray-400">Projeto acadêmico — MDS 2026/1</p>
                </div>
              </div>

            </div>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}