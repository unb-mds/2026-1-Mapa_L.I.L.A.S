describe('Página Inicial (Home)', () => {
  beforeEach(() => {
    // Intercepta a chamada da API antes de visitar a página
    cy.intercept('GET', '**/api/projetos-de-lei/stats', { fixture: 'stats.json' }).as('getStats');
    cy.visit('/');
  });

  it('deve exibir os contadores corretamente usando os dados da API', () => {
    // Aguarda a requisição mockada resolver
    cy.wait('@getStats');

    // Valida os valores na tela
    // O fixture tem total: 100, em_tramitacao: 50, aprovados: 30, arquivados: 20
    cy.contains('Total de Projetos de Feminicídio').parent().contains('100');
    cy.contains('Em Tramitação').parent().contains('50');
    cy.contains('Aprovados').parent().contains('30');
    cy.contains('Arquivados').parent().contains('20');
  });
});
