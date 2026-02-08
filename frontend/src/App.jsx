import { useMemo, useState } from 'react'

const API_URL = 'http://localhost:8000/prioritize'

const samplePatients = [
  {
    patient_id: 'P-001',
    age: 57,
    waiting_days: 35,
    stage: 3,
    ecog: 1,
    tumor_growth_rate: 0.6,
    socioeconomic_index: 0.7,
    group: 'BPJS-Regional'
  },
  {
    patient_id: 'P-002',
    age: 45,
    waiting_days: 21,
    stage: 2,
    ecog: 0,
    tumor_growth_rate: 0.35,
    socioeconomic_index: 0.2,
    group: 'Asuransi-Perkotaan'
  },
  {
    patient_id: 'P-003',
    age: 64,
    waiting_days: 49,
    stage: 4,
    ecog: 2,
    tumor_growth_rate: 0.75,
    socioeconomic_index: 0.9,
    group: 'BPJS-Regional'
  }
]

export default function App() {
  const [patientsJson, setPatientsJson] = useState(JSON.stringify(samplePatients, null, 2))
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const highRiskWaitingImpact = useMemo(() => {
    if (!result?.prioritized) return 0
    const highRisk = result.prioritized.filter((p) => p.suggested_priority === 'HIGH')
    if (highRisk.length === 0) return 0
    const avg = highRisk.reduce((acc, p) => acc + p.estimated_wait_impact, 0) / highRisk.length
    return avg.toFixed(2)
  }, [result])

  const submitPatients = async () => {
    setError('')
    setLoading(true)
    try {
      const parsed = JSON.parse(patientsJson)
      const resp = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ patients: parsed })
      })
      if (!resp.ok) {
        throw new Error('Gagal memproses prioritisasi.')
      }
      setResult(await resp.json())
    } catch (err) {
      setError(err.message)
      setResult(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="container">
      <h1>WaitList-Fair</h1>
      <p>
        Prioritisasi jadwal radioterapi berbasis AI untuk meminimalkan risiko progression-while-waiting
        dengan pertimbangan fairness antarkelompok pasien.
      </p>

      <section className="card">
        <h2>Input Pasien (JSON)</h2>
        <textarea
          value={patientsJson}
          onChange={(e) => setPatientsJson(e.target.value)}
          rows={16}
        />
        <button type="button" onClick={submitPatients} disabled={loading}>
          {loading ? 'Memproses...' : 'Hitung Prioritas'}
        </button>
        {error && <p className="error">{error}</p>}
      </section>

      {result && (
        <section className="card">
          <h2>Hasil Prioritisasi</h2>
          <p><strong>Baseline Manual:</strong> {result.manual_baseline}</p>
          <p><strong>Jumlah High-Risk:</strong> {result.metrics.high_risk_count}</p>
          <p><strong>Rata-rata dampak tunggu (high-risk):</strong> {highRiskWaitingImpact}</p>
          <p><strong>Equity Gap:</strong> {result.metrics.equity_gap}</p>

          <h3>Rata-rata Priority Score per Kelompok</h3>
          <ul>
            {Object.entries(result.metrics.avg_priority_by_group).map(([group, value]) => (
              <li key={group}>{group}: {value}</li>
            ))}
          </ul>

          <h3>Urutan Prioritas</h3>
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Kelompok</th>
                <th>Risk</th>
                <th>Fairness Boost</th>
                <th>Priority</th>
                <th>Kategori</th>
              </tr>
            </thead>
            <tbody>
              {result.prioritized.map((p) => (
                <tr key={p.patient_id}>
                  <td>{p.patient_id}</td>
                  <td>{p.group}</td>
                  <td>{p.risk_score}</td>
                  <td>{p.fairness_boost}</td>
                  <td>{p.priority_score}</td>
                  <td>{p.suggested_priority}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}
    </main>
  )
}
