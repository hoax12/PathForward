import type { ActionStep } from '../../lib/types'

interface Props {
  steps: ActionStep[]
}

export default function ActionPlan({ steps }: Props) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
      <h2 className="text-base font-semibold text-gray-900 mb-4">Your Action Plan</h2>
      <div className="space-y-4">
        {steps.map((step, i) => (
          <div key={i} className="flex items-start gap-3">
            <div className={`mt-0.5 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold shrink-0 ${
              step.is_parallel ? 'bg-blue-100 text-blue-700' : 'bg-indigo-600 text-white'
            }`}>
              {step.is_parallel ? '||' : i + 1}
            </div>
            <div className="flex-1">
              <p className="text-sm text-gray-800">{step.description}</p>
              {step.deadline_note && (
                <p className="text-xs text-amber-600 mt-1 font-medium">{step.deadline_note}</p>
              )}
              {step.is_parallel && (
                <p className="text-xs text-blue-500 mt-1">Can be done in parallel</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
