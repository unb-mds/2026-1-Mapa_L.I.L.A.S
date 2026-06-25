export const mockGraficosResumo = {
  tempo_medio_tramitacao: {
    dias: 482,
    variacao_percentual: 12,
    tendencia: "aumento",
  },
  top_estados: [
    { estado: "São Paulo", uf: "SP", total_pls: 1245 },
    { estado: "Rio de Janeiro", uf: "RJ", total_pls: 890 },
    { estado: "Minas Gerais", uf: "MG", total_pls: 654 },
    { estado: "Paraná", uf: "PR", total_pls: 432 },
    { estado: "Rio Grande do Sul", uf: "RS", total_pls: 310 },
  ],
  parlamentares_ativos: [
    { nome: "Deputada Ana", iniciais: "DA", descricao: "Autora PL 123/24", uf: "SP", total_propostas: 45 },
    { nome: "Senadora Rosa", iniciais: "SR", descricao: "Relatora Comissão", uf: "RJ", total_propostas: 38 },
    { nome: "Deputada Clara", iniciais: "DC", descricao: "Frente Parlamentar", uf: "MG", total_propostas: 32 },
  ],
};