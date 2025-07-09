describe('Index Test', () => {
  it('Contains Correct Header', () => {
    cy.visit('/')
    cy.get('[data-test="index-header"]').contains("PBJ Prototype")
  })
})