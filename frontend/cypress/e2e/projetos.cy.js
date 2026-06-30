describe('Página de Projetos de Lei', () => {
  beforeEach(() => {
    cy.intercept('GET', '**/api/projetos-de-lei/filtros', {
      partidos: ['PT', 'PL'],
      ufs: ['SP', 'RJ'],
      anos: [2023, 2024]
    }).as('getFiltros');
    
    cy.intercept('GET', '**/api/projetos-de-lei*', {
      projetos: [
        {
          id: 'pl-123-2023',
          numero: '123',
          ano: 2023,
          ementa: 'Teste de Ementa de PL sobre Feminicídio',
          status: 'em_tramitacao',
          casa: 'Câmara dos Deputados',
          autor_nome: 'Deputada Fictícia',
          autor_partido: 'PT',
          autor_uf: 'SP',
          ultima_atualizacao: '2023-05-10'
        }
      ],
      total: 1,
      page: 1,
      per_page: 6,
      total_pages: 1
    }).as('getProjetos');
    
    cy.visit('/projetos');
  });

  it('deve exibir a listagem de projetos corretamente', () => {
    cy.wait(['@getFiltros', '@getProjetos']);
    
    cy.contains('Projetos de Lei');
    cy.contains('Teste de Ementa de PL sobre Feminicídio');
    cy.contains('1 Projeto Encontrado');
  });
});
