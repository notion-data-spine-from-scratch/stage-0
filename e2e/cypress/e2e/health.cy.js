describe('health', () => {
  it('returns ok', () => {
    cy.request('/health').its('status').should('eq', 200)
  })
})
