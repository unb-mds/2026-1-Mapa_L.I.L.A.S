describe('Página de Projetos de Lei', () => {
  beforeEach(() => {
    cy.intercept('GET', '**/api/projetos-de-lei/filtros', { fixture: 'projetos_filtros.json' }).as('getFiltros');
    
    cy.intercept('GET', '**/api/projetos-de-lei*', { fixture: 'projetos_lista.json' }).as('getProjetos');
    
    cy.visit('/projetos');
  });

  it('deve exibir a listagem de projetos corretamente', () => {
    cy.wait(['@getFiltros', '@getProjetos']);
    
    cy.contains('Projetos de Lei');
    cy.contains('Teste de Ementa de PL sobre Feminicídio');
    cy.contains('1 Projeto Encontrado');
  });
});
