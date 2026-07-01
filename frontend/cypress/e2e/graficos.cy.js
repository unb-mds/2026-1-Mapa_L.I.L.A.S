describe('Página de Gráficos', () => {
  beforeEach(() => {
    cy.intercept('GET', '**/api/graficos/resumo', { fixture: 'graficos_resumo.json' }).as('getGraficos');
    
    cy.visit('/graficos');
  });

  it('deve exibir os componentes de gráficos usando os dados da API', () => {
    cy.wait('@getGraficos');
    
    cy.contains('Mapa da Legislação de Feminicídio');
    cy.contains('Parlamentar Teste');
    cy.contains('SP');
  });
});
