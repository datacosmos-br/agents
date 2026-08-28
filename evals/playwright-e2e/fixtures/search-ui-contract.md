# Search UI contract

- Route: `/items`
- Input: `[data-testid="search-input"]`
- Cards: `[data-testid="item-card"]`
- Empty state: `[data-testid="no-results"]`
- Search request: `GET /api/search?q=<encoded query>`
- Successful fixture query: `alpha`, returning an item named `Alpha adapter`
- Empty fixture query: `zz-no-match`
- Screenshot destination: `artifacts/search-results.png`
