describe('Index page', () => {
  beforeEach(() => {
    cy.visit('/');
  });

  it('loads successfully', () => {
    cy.location('pathname').should('eq', '/');
  });

  it('displays the main header', () => {
    cy.get('[data-test="index-header"]')
    .invoke('text')
    .then((text) => {
      expect(text.trim()).to.equal('PBJ Prototype');
    });
  
  });

  it('displays the paragraph text', () => {
    cy.contains('Prototype Flask UI for PBJ (Positive Behavior & JSON)').should('exist');
  });

  it('has the text input form', () => {
    cy.get('[data-test="index-input"]').within(() => {
      cy.get('label').should('have.attr', 'for', 'user_input');
      cy.get('input#user_input')
        .should('exist')
        .and('have.attr', 'name', 'user_input')
        .and('have.attr', 'required');
      cy.get('button[type="submit"]')
        .should('exist')
        .and('contain', 'Submit');
    });
  });

});
