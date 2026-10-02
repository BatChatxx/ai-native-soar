import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate, useParams } from 'react-router-dom'
import IncidentList from '../components/IncidentList'
import IncidentDetail from '../components/IncidentDetail'
import IncidentCreate from '../components/IncidentCreate'

export default function Incidents() {
  const { id } = useParams()
  const navigate = useNavigate()
  
  if (id) {
    return <IncidentDetail id={id} />
  }

  return <IncidentList onCreate={() => navigate('/incidents/new')} />
}
