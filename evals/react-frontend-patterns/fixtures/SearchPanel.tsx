import { useEffect, useState } from 'react'

type Result = { id: string; label: string }

export function SearchPanel({ query }: { query: string }) {
  const [results, setResults] = useState<Result[]>([])
  const [loading, setLoading] = useState(false)

  const fetchResults = async () => {
    setLoading(true)
    console.log(query)
    const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`)
    setResults(await response.json())
    setLoading(false)
  }

  useEffect(() => {
    void fetchResults()
  }, [fetchResults])

  return <div>{loading ? 'Loading' : results.map(item => <p key={item.id}>{item.label}</p>)}</div>
}
