describe('Página de Gráficos', () => {
  beforeEach(() => {
    cy.intercept('GET', '**/api/graficos/resumo', {
      parlamentares_ativos: [
        { 
          nome: "Parlamentar Teste", 
          iniciais: "PT",
          uf: "SP",
          descricao: "PT-SP",
          total_propostas: 5 
        }
      ],
      top_estados: [
        { uf: "SP", estado: "São Paulo", total_pls: 10 }
      ],
      tempo_medio_tramitacao: {
        dias: 120
      }
    }).as('getGraficos');
    
    cy.visit('/graficos');
  });

  it('deve exibir os componentes de gráficos usando os dados da API', () => {
    cy.wait('@getGraficos');
    
    cy.contains('Mapa da Legislação de Feminicídio');
    cy.contains('Parlamentar Teste');
    cy.contains('SP');
  });
});
