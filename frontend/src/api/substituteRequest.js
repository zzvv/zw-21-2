import request from './request.js'

export function listSubstituteRequests(params) {
  return request.get('/substitute-requests', { params })
}

export function createSubstituteRequest(data) {
  return request.post('/substitute-requests', data)
}

export function assignSubstitute(id, data) {
  return request.put(`/substitute-requests/${id}/assign`, data)
}

export function rejectSubstitute(id, remark) {
  return request.put(`/substitute-requests/${id}/reject`, { remark })
}

export function deleteSubstituteRequest(id) {
  return request.delete(`/substitute-requests/${id}`)
}