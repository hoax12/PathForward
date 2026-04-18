import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import type { RoutingResult } from '../lib/types'
import { fetchResults } from '../lib/api'
import ProgramCard from '../components/Results/ProgramCard'
import ActionPlan from '../components/Results/ActionPlan'
import IntentBadge from '../components/Results/IntentBadge'

export default function ResultsPage() {
  const { sessionId } = useParams<{ sessionId: string }>()
  const [result, setResult] = useState<RoutingResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!sessionId) return
    let active = true

    const poll = async () => {
      try {
        const data = await fetchResults(sessionId)
        if (!active) return
        if (data !== null) {
          setResult(data)
        } else {
          setTimeout(poll, 1500)
        }
      } catch (err) {
        if (!active) return
        setError(err instanceof Error ? err.message : 'Failed to load results')
      }
    }

    void poll()
    return () => { active = false }
  }, [sessionId])

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="text-center max-w-sm">
          <div className="w-12 h-12 rounded-full bg-red-100 flex items-center justify-center mx-auto mb-4 text-2xl">!</div>
          <p className="text-gray-800 font-medium mb-2">Something went wrong</p>
          <p className="text-sm text-red-600 mb-6">{error}</p>
          <Link to="/" className="text-indigo-600 hover:underline text-sm">← Start a new search</Link>
        </div>
      </div>
    )
  }

  if (!result) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-700 font-medium">Finding the best programs for you…</p>
          <p className="text-gray-400 text-sm mt-1">This takes about 2–5 seconds</p>
        </div>
      </div>
    )
  }

  const { classified_intent, ranked_matches, action_plan, fairness_flags, generated_at } = result

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-3xl mx-auto px-4 py-8">
        <div className="flex items-start justify-between mb-6">
          <div>
            <Link to="/" className="text-sm text-indigo-600 hover:underline block mb-2">← New search</Link>
            <h1 className="text-2xl font-bold text-gray-900">Your Matches</h1>
            <p className="text-sm text-gray-500 mt-1">
              {ranked_matches.length} program{ranked_matches.length !== 1 ? 's' : ''} found
            </p>
          </div>
          <IntentBadge intent={classified_intent} />
        </div>

        {fairness_flags.length > 0 && (
          <div className="mb-6 p-3 bg-amber-50 border border-amber-200 rounded-lg text-sm text-amber-800">
            {fairness_flags.join(' · ')}
          </div>
        )}

        <div className="space-y-4 mb-8">
          {ranked_matches.length === 0
            ? <p className="text-gray-500 text-center py-12">No matching programs found for your profile.</p>
            : ranked_matches.map((match, i) => (
                <ProgramCard key={match.program_id} match={match} rank={i + 1} />
              ))}
        </div>

        {action_plan.length > 0 && <ActionPlan steps={action_plan} />}

        <p className="text-xs text-gray-400 text-center mt-8">
          Generated {new Date(generated_at).toLocaleString()} · LA County demo scope only
        </p>
      </div>
    </div>
  )
}
