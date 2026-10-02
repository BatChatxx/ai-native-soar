import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useParams, Link } from 'react-router-dom'

interface Incident {
  id: number
  number: string
  title: string
  description: string
  severity: string
  status: string
  created_at: string
  source_type: string
  evidence: Evidence[]
  comments: Comment[]
}

interface Evidence {
  id: string
  file: string
  hash: string
  uploaded_at: string
}

interface Comment {
  id: string
  content: string
  created_at: string
  author: string
}

interface IncidentDetailProps {
  id: number
}

export default function IncidentDetail({ id }: IncidentDetailProps) {
  const params = useParams()
  const incidentId = parseInt(params.id || id.toString())

  const [newComment, setNewComment] = useState('')

  const { data: incident, isLoading } = useQuery({
    queryKey: ['incident', incidentId],
    queryFn: async () => {
      const response = await fetch(`http://localhost:8000/api/v1/incidents/${incidentId}`)
      return response.json() as Promise<Incident>
    },
  })

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-gray-500">Loading incident...</div>
      </div>
    )
  }

  if (!incident) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-gray-500">Incident not found</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-7xl mx-auto p-6">
        <div className="mb-4 flex items-center gap-4">
          <Link to="/incidents" className="text-blue-600 hover:text-blue-800">
            ← Back to Incidents
          </Link>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{incident.number}</h1>
              <h2 className="text-xl text-gray-700 mt-2">{incident.title}</h2>
            </div>
            <div className="flex gap-2">
              <span
                className={`px-3 py-1 text-sm rounded-full ${
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
              <span className="px-3 py-1 text-sm bg-gray-100 text-gray-800 rounded-full">
                {incident.status}
              </span>
            </div>
          </div>

          <p className="text-gray-700 mb-4">{incident.description}</p>

          <div className="flex items-center gap-4 text-sm text-gray-500">
            <span>Source: {incident.source_type}</span>
            <span>Created: {new Date(incident.created_at).toLocaleString()}</span>
          </div>

          <div className="mt-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Evidence</h3>
            {incident.evidence?.length === 0 ? (
              <p className="text-gray-500">No evidence attached yet.</p>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {incident.evidence.map((evidence) => (
                  <div key={evidence.id} className="border border-gray-200 rounded-lg p-4">
                    <a
                      href={evidence.file}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800"
                    >
                      {evidence.file}
                    </a>
                    <div className="mt-2 text-sm text-gray-500">
                      Hash: {evidence.hash}
                    </div>
                    <div className="text-sm text-gray-400">
                      Uploaded: {new Date(evidence.uploaded_at).toLocaleString()}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Timeline</h3>
          <div className="space-y-2">
            <TimelineEvent time="10:21" message="Incident created" />
            <TimelineEvent time="10:22" message="Observable extracted" />
            <TimelineEvent time="10:23" message="SIEM query executed" />
            <TimelineEvent time="10:24" message="Evidence attached" />
            <TimelineEvent time="10:25" message="AI investigation started" />
            <TimelineEvent time="10:27" message="Containment requested" />
            <TimelineEvent time="10:28" message="Analyst approved action" />
            <TimelineEvent time="10:29" message="Endpoint contained" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 mt-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Comments</h3>
          <div className="space-y-4">
            {incident.comments?.map((comment) => (
              <div key={comment.id} className="border-b border-gray-200 pb-4">
                <div className="flex justify-between items-center mb-2">
                  <span className="font-semibold text-gray-900">{comment.author}</span>
                  <span className="text-sm text-gray-500">
                    {new Date(comment.created_at).toLocaleString()}
                  </span>
                </div>
                <p className="text-gray-700">{comment.content}</p>
              </div>
            ))}
          </div>

          <div className="mt-4">
            <textarea
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              placeholder="Add a comment..."
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows={3}
            />
            <button
              onClick={() => console.log('Comment submitted')}
              className="mt-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
            >
              Post Comment
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

function TimelineEvent({ time, message }: { time: string; message: string }) {
  return (
    <div className="flex gap-3">
      <div className="w-16 text-sm text-gray-500 font-mono">{time}</div>
      <div className="flex-1 bg-gray-50 rounded-lg px-4 py-3">
        <p className="text-gray-700">{message}</p>
      </div>
    </div>
  )
}
