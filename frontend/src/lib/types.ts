export interface Location {
  zip_code?: string
  city?: string
  county?: string
}

export type IncomeBand = '0-20k' | '20-35k' | '35-50k' | '50-75k' | '75k+'
export type EmploymentStatus = 'self_employed' | '1099_contractor' | 'employee' | 'unemployed'
export type BusinessType = 'food' | 'retail' | 'services' | 'healthcare' | 'childcare' | 'other'
export type SpeedToFund = 'same_day' | '1-3_days' | '1-2_weeks' | 'varies'
export type ProgramType = 'grant' | 'microloan' | 'fee_free_product' | 'referral'
export type UrgencyLevel = 'immediate' | 'this_week' | 'this_month'

export interface IntakeProfile {
  session_id?: string
  location: Location
  income_band: IncomeBand
  employment_status: EmploymentStatus
  business_type?: BusinessType | null
  urgent_needs: string[]
  free_text: string
  monthly_revenue?: number | null
  has_paypal_account: boolean
  extracted_attributes: Record<string, unknown>
}

export interface IntakeResponse {
  session_id: string
  status: 'processing'
}

export interface ClassifiedIntent {
  primary_intent: string
  urgency_level: UrgencyLevel
  extracted_facts: Record<string, unknown>
  confidence: number
}

export interface ActionStep {
  description: string
  program_id?: string | null
  is_parallel: boolean
  deadline_note?: string | null
}

export interface ProgramMatch {
  program_id: string
  name: string
  org_name: string
  eligibility_score: number
  eligibility_criteria_met: string[]
  eligibility_criteria_missing: string[]
  speed_to_fund: SpeedToFund
  max_amount?: number | null
  program_type: ProgramType
  documents_needed: string[]
  application_url?: string | null
  data_verified_date: string
}

export interface RoutingResult {
  session_id: string
  classified_intent: ClassifiedIntent
  ranked_matches: ProgramMatch[]
  action_plan: ActionStep[]
  fairness_flags: string[]
  generated_at: string
}
