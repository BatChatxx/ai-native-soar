import { useState, useEffect } from 'react'

interface AutomationRun {
  slug: string
  name: string
  description: string
  risk: string
  input_schema: object
}

interface AutomationRunProps {
  automation: AutomationRun
}

export default function AutomationRun({ automation }: AutomationRunProps) {
  const [input, setInput] = useState('')
  const [status, setStatus] = useState<'idle' | 'running' | 'completed' | 'failed'>('idle')
  const [output, setOutput] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    setStatus('running')
    setError(null)
    setOutput(null)

    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/automation/${automation.slug}/run`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ input, incident_id: 1 }), // TODO: Get actual incident ID
        }
      )

      if (response.ok) {
        const data = await response.json()
        setOutput(JSON.stringify(data, null, 2))
        setStatus('completed')
      } else {
        throw new Error('Failed to run automation')
      }
    } catch (err) {
      setStatus('failed')
      setError(err instanceof Error ? err.message : 'Unknown error')
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{automation.name}</h3>
      <p className="text-sm text-gray-600 mb-4">{automation.description}</p>

      <div className="mb-4">
        <span className={`inline-block px-2 py-1 text-xs rounded-full ${
          automation.risk === 'READ' ? 'bg-green-100 text-green-800' :
          automation.risk === 'ENRICH' ? 'bg-blue-100 text-blue-800' :
          automation.risk === 'MODIFY_LOW' ? 'bg-yellow-100 text-yellow-800' :
          automation.risk === 'MODIFY' ? 'bg-orange-100 text-orange-800' :
          automation.risk === 'CONTAIN' ? 'bg-red-100 text-red-800' :
          automation.risk === 'EXECUTE' ? 'bg-red-200 text-red-800' :
          'bg-purple-100 text-purple-800'
        }`}>
          Risk: {automation.risk}
        </span>
      </div>

      {automation.input_schema && (
        <div className="mb-4 p-4 bg-gray-50 rounded-lg">
          <h4 className="text-sm font-semibold text-gray-700 mb-2">Input Schema:</h4>
          <pre className="text-xs text-gray-600 overflow-auto max-h-40">
            {JSON.stringify(automation.input_schema, null, 2)}
          </pre>
        </div>
      )}

      <form onSubmit={handleSubmit} className="mb-4">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Enter automation input..."
          className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
          rows={3}
        />
        <button
          type="submit"
          disabled={status === 'running'}
          className="mt-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 text-sm"
        >
          {status === 'running' ? 'Running...' : 'Run Automation'}
        </button>
      </form>

      {(status === 'completed' || status === 'failed') && (
        <div className={`rounded-lg p-4 text-sm ${
          status === 'completed' ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'
        }`}>
          <span className="font-semibold mb-2 block">
            {status === 'completed' ? 'Execution completed' : 'Execution failed'}
          </span>
          <pre className="whitespace-pre-wrap overflow-auto max-h-60">
            {output || error}
          </pre>
        </div>
      )}
    </div>
  )
}
