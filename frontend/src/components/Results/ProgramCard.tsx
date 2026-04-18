import { useState } from 'react'
import type { ProgramMatch, SpeedToFund, ProgramType } from '../../lib/types'

interface Props {
  match: ProgramMatch
  rank: number
}

const SPEED_LABELS: Record<SpeedToFund, string> = {
  same_day: 'Same Day',
  '1-3_days': '1–3 Days',
  '1-2_weeks': '1–2 Weeks',
  varies: 'Varies',
}

const SPEED_COLORS: Record<SpeedToFund, string> = {
  same_day: 'bg-green-100 text-green-800',
  '1-3_days': 'bg-blue-100 text-blue-800',
  '1-2_weeks': 'bg-yellow-100 text-yellow-800',
  varies: 'bg-gray-100 text-gray-700',
}

const TYPE_LABELS: Record<ProgramType, string> = {
  grant: 'Grant',
  microloan: 'Microloan',
  fee_free_product: 'Fee-Free',
  referral: 'Referral',
}

export default function ProgramCard({ match, rank }: Props) {
  const [expanded, setExpanded] = useState(false)
  const pct = Math.round(match.eligibility_score * 100)
  const scoreColor = pct >= 70 ? 'text-green-600' : pct >= 40 ? 'text-yellow-600' : 'text-red-500'
  const barColor = pct >= 70 ? 'bg-green-500' : pct >= 40 ? 'bg-yellow-500' : 'bg-red-400'

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
      <div className="p-5">
        <div className="flex items-start justify-between gap-4">
          <div className="min-w-0">
            <div className="flex items-center gap-2 mb-1 flex-wrap">
              <span className="text-xs font-medium text-gray-400">#{rank}</span>
              <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${SPEED_COLORS[match.speed_to_fund]}`}>
                {SPEED_LABELS[match.speed_to_fund]}
              </span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-purple-100 text-purple-800 font-medium">
                {TYPE_LABELS[match.program_type]}
              </span>
            </div>
            <h3 className="text-base font-semibold text-gray-900 leading-tight">{match.name}</h3>
            <p className="text-sm text-gray-500 mt-0.5">{match.org_name}</p>
          </div>
          <div className="text-right shrink-0">
            {match.max_amount != null && (
              <div className="text-lg font-bold text-gray-900">
                ${match.max_amount.toLocaleString()}
              </div>
            )}
            <div className="text-sm">
              <span className={`font-semibold ${scoreColor}`}>{pct}%</span>
              <span className="text-gray-400 ml-1">match</span>
            </div>
          </div>
        </div>

        <div className="mt-3 h-1.5 bg-gray-100 rounded-full overflow-hidden">
          <div className={`h-full rounded-full ${barColor}`} style={{ width: `${pct}%` }} />
        </div>

        <button onClick={() => setExpanded(e => !e)}
          className="mt-3 text-xs text-indigo-600 hover:underline font-medium">
          {expanded ? 'Hide details ↑' : 'Show criteria & documents ↓'}
        </button>
      </div>

      {expanded && (
        <div className="border-t border-gray-100 px-5 py-4 bg-gray-50 space-y-4">
          {match.eligibility_criteria_met.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Criteria met</p>
              <ul className="space-y-1">
                {match.eligibility_criteria_met.map(c => (
                  <li key={c} className="text-sm text-green-700 flex items-start gap-1.5">
                    <span className="shrink-0 mt-0.5">✓</span> {c}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {match.eligibility_criteria_missing.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Criteria missing</p>
              <ul className="space-y-1">
                {match.eligibility_criteria_missing.map(c => (
                  <li key={c} className="text-sm text-red-600 flex items-start gap-1.5">
                    <span className="shrink-0 mt-0.5">✗</span> {c}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {match.documents_needed.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Documents needed</p>
              <ul className="space-y-1">
                {match.documents_needed.map(d => (
                  <li key={d} className="text-sm text-gray-700 flex items-start gap-1.5">
                    <span className="shrink-0 mt-0.5">📄</span> {d}
                  </li>
                ))}
              </ul>
            </div>
          )}
          <div className="flex items-center justify-between text-xs text-gray-400 pt-1">
            <span>Verified {match.data_verified_date}</span>
            {match.application_url && (
              <a href={match.application_url} target="_blank" rel="noopener noreferrer"
                className="inline-flex items-center gap-1 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 px-4 py-1.5 rounded-lg transition-colors">
                Apply Now →
              </a>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
