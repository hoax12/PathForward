import type { ClassifiedIntent, UrgencyLevel } from '../../lib/types'

interface Props {
  intent: ClassifiedIntent
}

const INTENT_LABELS: Record<string, string> = {
  equipment_emergency: 'Equipment Emergency',
  cashflow_gap: 'Cash Flow Gap',
  housing_need: 'Housing Need',
  general_assistance: 'General Assistance',
}

const URGENCY_COLORS: Record<UrgencyLevel, string> = {
  immediate: 'bg-red-100 text-red-800 border-red-200',
  this_week: 'bg-orange-100 text-orange-800 border-orange-200',
  this_month: 'bg-blue-100 text-blue-800 border-blue-200',
}

const URGENCY_LABELS: Record<UrgencyLevel, string> = {
  immediate: 'Urgent',
  this_week: 'This week',
  this_month: 'This month',
}

export default function IntentBadge({ intent }: Props) {
  const label = INTENT_LABELS[intent.primary_intent]
    ?? intent.primary_intent.replace(/_/g, ' ')

  return (
    <div className="text-right">
      <div className="text-sm font-semibold text-gray-900">{label}</div>
      <div className={`inline-block mt-1 text-xs px-2 py-0.5 rounded-full border font-medium ${URGENCY_COLORS[intent.urgency_level]}`}>
        {URGENCY_LABELS[intent.urgency_level]}
      </div>
      <div className="text-xs text-gray-400 mt-1">{Math.round(intent.confidence * 100)}% confidence</div>
    </div>
  )
}
