import { useEffect, useState } from 'react'

type Result = { id: string; label: string }
export type SearchOutcome =
  | { kind: 'results'; items: Result[] }
  | { kind: 'rejected'; message: string }

export function SearchPanel({
  query,
  search,
}: {
  query: string
  search: (query: string, signal: AbortSignal) => Promise<SearchOutcome>
}) {
  const [outcome, setOutcome] = useState<SearchOutcome | null>(null)
  const [loading, setLoading] = useState(false)

  const fetchResults = async () => {
    setLoading(true)
    console.log(query)
    setOutcome(await search(query, new AbortController().signal))
    setLoading(false)
  }

  useEffect(() => {
    void fetchResults()
  }, [fetchResults])

  return <div>{loading ? 'Loading' : JSON.stringify(outcome)}</div>
}
