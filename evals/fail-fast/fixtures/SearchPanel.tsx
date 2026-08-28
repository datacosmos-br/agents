import { Suspense } from "react";

export function SearchPanel() {
  return (
    <Suspense fallback={<div aria-label="Loading search results">Loading…</div>}>
      <SearchResults />
    </Suspense>
  );
}

function SearchResults() {
  return <section aria-live="polite">Results</section>;
}
