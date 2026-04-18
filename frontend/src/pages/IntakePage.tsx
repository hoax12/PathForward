import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import type { IntakeProfile, IncomeBand, EmploymentStatus, BusinessType } from '../lib/types'
import { submitIntake } from '../lib/api'

const STEPS = ['Basic Info', 'Needs & Urgency', 'Your Situation']

const INCOME_OPTIONS: IncomeBand[] = ['0-20k', '20-35k', '35-50k', '50-75k', '75k+']

const EMPLOYMENT_OPTIONS: { value: EmploymentStatus; label: string }[] = [
  { value: 'self_employed', label: 'Self-employed' },
  { value: '1099_contractor', label: '1099 Contractor' },
  { value: 'employee', label: 'Employee (W-2)' },
  { value: 'unemployed', label: 'Unemployed' },
]

const BUSINESS_OPTIONS: { value: BusinessType; label: string }[] = [
  { value: 'food', label: 'Food & Beverage' },
  { value: 'retail', label: 'Retail' },
  { value: 'services', label: 'Services' },
  { value: 'healthcare', label: 'Healthcare' },
  { value: 'childcare', label: 'Childcare' },
  { value: 'other', label: 'Other' },
]

const URGENT_NEEDS = ['equipment', 'cash flow', 'rent', 'food', 'utilities', 'childcare', 'healthcare', 'legal']

interface FormState {
  zip_code: string
  city: string
  income_band: IncomeBand
  employment_status: EmploymentStatus
  business_type: BusinessType | ''
  urgent_needs: string[]
  free_text: string
}

const INITIAL: FormState = {
  zip_code: '',
  city: '',
  income_band: '20-35k',
  employment_status: 'self_employed',
  business_type: '',
  urgent_needs: [],
  free_text: '',
}

export default function IntakePage() {
  const navigate = useNavigate()
  const [step, setStep] = useState(0)
  const [form, setForm] = useState<FormState>(INITIAL)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const set = <K extends keyof FormState>(field: K, value: FormState[K]) =>
    setForm(prev => ({ ...prev, [field]: value }))

  const toggleNeed = (need: string) =>
    set('urgent_needs', form.urgent_needs.includes(need)
      ? form.urgent_needs.filter(n => n !== need)
      : [...form.urgent_needs, need])

  const handleSubmit = async () => {
    setLoading(true)
    setError(null)
    try {
      const profile: IntakeProfile = {
        location: { zip_code: form.zip_code || undefined, city: form.city || undefined, county: 'Los Angeles' },
        income_band: form.income_band,
        employment_status: form.employment_status,
        business_type: form.business_type || null,
        urgent_needs: form.urgent_needs,
        free_text: form.free_text,
        has_paypal_account: false,
        extracted_attributes: {},
      }
      const { session_id } = await submitIntake(profile)
      navigate(`/results/${session_id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg p-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">PathForward</h1>
          <p className="text-gray-500 text-sm mt-1">LA County benefits routing · 90 seconds</p>
        </div>

        <div className="flex items-center mb-8">
          {STEPS.map((label, i) => (
            <div key={label} className="flex items-center flex-1">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                i <= step ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-500'
              }`}>{i + 1}</div>
              {i < STEPS.length - 1 && (
                <div className={`flex-1 h-1 mx-2 rounded ${i < step ? 'bg-indigo-600' : 'bg-gray-200'}`} />
              )}
            </div>
          ))}
        </div>

        <h2 className="text-lg font-semibold text-gray-800 mb-6">{STEPS[step]}</h2>

        {step === 0 && (
          <div className="space-y-5">
            <div className="grid grid-cols-2 gap-4">
              {(['zip_code', 'city'] as const).map((field, i) => (
                <div key={field}>
                  <label className="block text-sm font-medium text-gray-700 mb-1">{i === 0 ? 'ZIP Code' : 'City'}</label>
                  <input
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    value={form[field]}
                    onChange={e => set(field, e.target.value)}
                    placeholder={i === 0 ? '90011' : 'Los Angeles'}
                    maxLength={i === 0 ? 5 : undefined}
                  />
                </div>
              ))}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Annual Income</label>
              <div className="grid grid-cols-3 gap-2">
                {INCOME_OPTIONS.map(opt => (
                  <button key={opt} type="button" onClick={() => set('income_band', opt)}
                    className={`py-2 px-3 rounded-lg text-sm border transition-colors ${
                      form.income_band === opt ? 'bg-indigo-600 text-white border-indigo-600' : 'border-gray-300 text-gray-700 hover:border-indigo-400'
                    }`}>${opt}</button>
                ))}
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Employment Status</label>
              <div className="grid grid-cols-2 gap-2">
                {EMPLOYMENT_OPTIONS.map(opt => (
                  <button key={opt.value} type="button" onClick={() => set('employment_status', opt.value)}
                    className={`py-2 px-3 rounded-lg text-sm border transition-colors text-left ${
                      form.employment_status === opt.value ? 'bg-indigo-600 text-white border-indigo-600' : 'border-gray-300 text-gray-700 hover:border-indigo-400'
                    }`}>{opt.label}</button>
                ))}
              </div>
            </div>
          </div>
        )}

        {step === 1 && (
          <div className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Urgent Needs (select all that apply)</label>
              <div className="flex flex-wrap gap-2">
                {URGENT_NEEDS.map(need => (
                  <button key={need} type="button" onClick={() => toggleNeed(need)}
                    className={`py-1.5 px-3 rounded-full text-sm border transition-colors capitalize ${
                      form.urgent_needs.includes(need) ? 'bg-indigo-600 text-white border-indigo-600' : 'border-gray-300 text-gray-700 hover:border-indigo-400'
                    }`}>{need}</button>
                ))}
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Business Type (if applicable)</label>
              <div className="grid grid-cols-3 gap-2">
                {BUSINESS_OPTIONS.map(opt => (
                  <button key={opt.value} type="button"
                    onClick={() => set('business_type', form.business_type === opt.value ? '' : opt.value)}
                    className={`py-2 px-3 rounded-lg text-sm border transition-colors ${
                      form.business_type === opt.value ? 'bg-indigo-600 text-white border-indigo-600' : 'border-gray-300 text-gray-700 hover:border-indigo-400'
                    }`}>{opt.label}</button>
                ))}
              </div>
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-4">
            <p className="text-sm text-gray-600">Tell us more in your own words. What&apos;s your most pressing situation right now?</p>
            <textarea
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
              rows={6}
              value={form.free_text}
              onChange={e => set('free_text', e.target.value)}
              placeholder="My mixer broke last week and I need to fulfill catering orders by Friday…"
            />
          </div>
        )}

        {error && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">{error}</div>
        )}

        <div className="flex justify-between mt-8">
          {step > 0
            ? <button onClick={() => setStep(s => s - 1)}
                className="px-5 py-2.5 text-sm font-medium text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50">Back</button>
            : <div />}
          {step < STEPS.length - 1
            ? <button onClick={() => setStep(s => s + 1)}
                className="px-5 py-2.5 text-sm font-medium bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">Continue</button>
            : <button onClick={handleSubmit} disabled={loading}
                className="px-5 py-2.5 text-sm font-medium bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-60">
                {loading ? 'Finding programs…' : 'Find My Programs'}
              </button>}
        </div>
      </div>
    </div>
  )
}
