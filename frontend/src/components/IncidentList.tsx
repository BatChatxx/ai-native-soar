import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'

interface Incident {
  id: number
  number: string
  title: string
  description: string
  severity: string
  status: string
  created_at: string
  source_type: string
}

interface IncidentListProps {
  onCreate?: () => void
}

export default function IncidentList({ onCreate }: IncidentListProps) {
  const [filter, setFilter] = useState('')

  const { data: incidents, isLoading } = useQuery({
    queryKey: ['incidents'],
    queryFn: async () => {
      const response = await fetch('http://localhost:8000/api/v1/incidents')
      return response.json() as Promise<Incident[]>
    },
  })

  const filteredIncidents = incidents?.filter(inc =>
    inc.title.toLowerCase().includes(filter.toLowerCase()) ||
    inc.number.toLowerCase().includes(filter.toLowerCase())
  )

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Incidents</h1>
          {onCreate && (
            <Link
              to="/incidents/new"
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
            >
              + New Incident
            </Link>
          )}
        </div>

        <div className="mb-4">
          <input
            type="text"
            placeholder="Filter incidents..."
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded-lg"
          />
        </div>

        {isLoading ? (
          <div className="text-center text-gray-500 py-12">Loading incidents...</div>
        ) : incidents?.length === 0 ? (
          <div className="text-center text-gray-500 py-12">No incidents found</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredIncidents?.map((incident) => (
              <Link
                key={incident.id}
                to={`/incidents/${incident.id}`}
                className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
              >
                <div className="flex justify-between items-start mb-2">
                  <span className="text-sm text-gray-500">{incident.number}</span>
                  <span
                    className={`px-2 py-1 text-xs rounded-full ${
                      incident.severity === 'critical'
                        ? 'bg-red-100 text-red-800'
                        : incident.severity === 'high'
                        ? 'bg-orange-100 text-orange-800'
                        : incident.severity === 'medium'
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-green-100 text-green-800'
                    }`}
                  >
                    {incident.severity}
                  </span>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {incident.title}
                </h3>
                <p className="text-sm text-gray-600 line-clamp-2">
                  {incident.description}
                </p>
                <div className="mt-4 flex justify-between items-center text-sm text-gray-500">
                  <span>{incident.status}</span>
                  <span>{new Date(incident.created_at).toLocaleDateString()}</span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
