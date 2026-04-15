'use client'

import { useState, useEffect, useCallback } from 'react'
import {
  Organization,
  OrganizationMember,
  OrganizationWithMembers,
  OrganizationRole,
  listOrganizations,
  createOrganization,
  getOrganization,
  updateOrganization,
  deleteOrganization,
  inviteMember,
  updateMemberRole,
  removeMember,
  transferOwnership,
  leaveOrganization,
} from '@/lib/api'
import { formatApiError } from '@/lib/api'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card'
import { Skeleton } from '@/components/ui/Skeleton'
import { useToast } from '@/hooks/useToast'
import {
  Users,
  Plus,
  Trash2,
  Settings,
  Crown,
  UserPlus,
  UserMinus,
  Shield,
  User,
  AlertCircle,
  CheckCircle,
  X,
  MoreHorizontal,
  LogOut,
  Building2,
} from 'lucide-react'

interface TeamTabProps {
  user?: {
    id: string
    email: string
    full_name?: string
  }
}

type ViewState = 'list' | 'create' | 'detail' | 'invite'

// Helper to get initials for avatar
function getInitials(name: string): string {
  if (!name) return '?'
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

// Helper to generate consistent avatar color
function getAvatarColor(seed: string): string {
  const colors = [
    'bg-red-500',
    'bg-orange-500',
    'bg-amber-500',
    'bg-green-500',
    'bg-emerald-500',
    'bg-teal-500',
    'bg-cyan-500',
    'bg-sky-500',
    'bg-blue-500',
    'bg-indigo-500',
    'bg-violet-500',
    'bg-purple-500',
    'bg-fuchsia-500',
    'bg-pink-500',
    'bg-rose-500',
  ]
  const index = seed.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
  return colors[index % colors.length]
}

export default function TeamTab({ user }: TeamTabProps) {
  const { showToast } = useToast()
  const [viewState, setViewState] = useState<ViewState>('list')
  const [loading, setLoading] = useState(true)
  const [organizations, setOrganizations] = useState<Organization[]>([])
  const [selectedOrg, setSelectedOrg] = useState<OrganizationWithMembers | null>(null)
  
  // Form states
  const [newOrgName, setNewOrgName] = useState('')
  const [inviteEmail, setInviteEmail] = useState('')
  const [inviteRole, setInviteRole] = useState<OrganizationRole>('member')
  const [isSubmitting, setIsSubmitting] = useState(false)
  
  // Confirmation dialogs
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [showRemoveConfirm, setShowRemoveConfirm] = useState<string | null>(null)
  const [showLeaveConfirm, setShowLeaveConfirm] = useState(false)
  const [showTransferConfirm, setShowTransferConfirm] = useState<string | null>(null)
  
  // Action loading states
  const [actionLoading, setActionLoading] = useState<string | null>(null)

  const loadOrganizations = useCallback(async () => {
    try {
      setLoading(true)
      const orgs = await listOrganizations()
      setOrganizations(orgs)
    } catch (error) {
      console.error('Failed to load organizations:', error)
      showToast('Failed to load organizations', 'error')
    } finally {
      setLoading(false)
    }
  }, [showToast])

  useEffect(() => {
    loadOrganizations()
  }, [loadOrganizations])

  const handleCreateOrganization = async () => {
    if (!newOrgName.trim()) {
      showToast('Please enter an organization name', 'error')
      return
    }

    try {
      setIsSubmitting(true)
      await createOrganization({ name: newOrgName.trim() })
      showToast('Organization created successfully', 'success')
      setNewOrgName('')
      setViewState('list')
      await loadOrganizations()
    } catch (error) {
      console.error('Failed to create organization:', error)
      showToast(formatApiError(error, 'Failed to create organization'), 'error')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleViewOrganization = async (orgId: string) => {
    try {
      setLoading(true)
      const org = await getOrganization(orgId)
      setSelectedOrg(org)
      setViewState('detail')
    } catch (error) {
      console.error('Failed to load organization details:', error)
      showToast('Failed to load organization details', 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleInviteMember = async () => {
    if (!inviteEmail.trim() || !selectedOrg) {
      showToast('Please enter an email address', 'error')
      return
    }

    try {
      setIsSubmitting(true)
      await inviteMember(selectedOrg.id, { email: inviteEmail.trim(), role: inviteRole })
      showToast('Invitation sent successfully', 'success')
      setInviteEmail('')
      setInviteRole('member')
      // Refresh organization details
      const org = await getOrganization(selectedOrg.id)
      setSelectedOrg(org)
    } catch (error) {
      console.error('Failed to invite member:', error)
      showToast(formatApiError(error, 'Failed to invite member'), 'error')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleUpdateMemberRole = async (memberId: string, newRole: OrganizationRole) => {
    if (!selectedOrg) return

    try {
      setActionLoading(`role-${memberId}`)
      await updateMemberRole(selectedOrg.id, memberId, newRole)
      showToast('Role updated successfully', 'success')
      // Refresh organization details
      const org = await getOrganization(selectedOrg.id)
      setSelectedOrg(org)
    } catch (error) {
      console.error('Failed to update role:', error)
      showToast(formatApiError(error, 'Failed to update role'), 'error')
    } finally {
      setActionLoading(null)
    }
  }

  const handleRemoveMember = async (memberId: string) => {
    if (!selectedOrg) return

    try {
      setActionLoading(`remove-${memberId}`)
      await removeMember(selectedOrg.id, memberId)
      showToast('Member removed successfully', 'success')
      setShowRemoveConfirm(null)
      // Refresh organization details
      const org = await getOrganization(selectedOrg.id)
      setSelectedOrg(org)
    } catch (error) {
      console.error('Failed to remove member:', error)
      showToast(formatApiError(error, 'Failed to remove member'), 'error')
    } finally {
      setActionLoading(null)
    }
  }

  const handleDeleteOrganization = async () => {
    if (!selectedOrg) return

    try {
      setActionLoading('delete')
      await deleteOrganization(selectedOrg.id)
      showToast('Organization deleted successfully', 'success')
      setShowDeleteConfirm(false)
      setSelectedOrg(null)
      setViewState('list')
      await loadOrganizations()
    } catch (error) {
      console.error('Failed to delete organization:', error)
      showToast(formatApiError(error, 'Failed to delete organization'), 'error')
    } finally {
      setActionLoading(null)
    }
  }

  const handleTransferOwnership = async (newOwnerId: string) => {
    if (!selectedOrg) return

    try {
      setActionLoading('transfer')
      await transferOwnership(selectedOrg.id, newOwnerId)
      showToast('Ownership transferred successfully', 'success')
      setShowTransferConfirm(null)
      // Refresh organization details
      const org = await getOrganization(selectedOrg.id)
      setSelectedOrg(org)
    } catch (error) {
      console.error('Failed to transfer ownership:', error)
      showToast(formatApiError(error, 'Failed to transfer ownership'), 'error')
    } finally {
      setActionLoading(null)
    }
  }

  const handleLeaveOrganization = async () => {
    if (!selectedOrg) return

    try {
      setActionLoading('leave')
      await leaveOrganization(selectedOrg.id)
      showToast('Left organization successfully', 'success')
      setShowLeaveConfirm(false)
      setSelectedOrg(null)
      setViewState('list')
      await loadOrganizations()
    } catch (error) {
      console.error('Failed to leave organization:', error)
      showToast(formatApiError(error, 'Failed to leave organization'), 'error')
    } finally {
      setActionLoading(null)
    }
  }

  // Get current user's role in the selected organization
  const getCurrentUserRole = (): string | null => {
    if (!selectedOrg || !user) return null
    if (selectedOrg.owner_id === user.id) return 'owner'
    return selectedOrg.current_user_role || null
  }

  const canManageMembers = (): boolean => {
    const role = getCurrentUserRole()
    return role === 'owner' || role === 'admin'
  }

  const isOwner = (): boolean => {
    return getCurrentUserRole() === 'owner'
  }

  // Render functions
  const renderLoading = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-10 w-32" />
      </div>
      <Card>
        <CardContent className="p-6">
          <div className="space-y-4">
            <Skeleton className="h-20 w-full" />
            <Skeleton className="h-20 w-full" />
            <Skeleton className="h-20 w-full" />
          </div>
        </CardContent>
      </Card>
    </div>
  )

  const renderEmptyState = () => (
    <div className="text-center py-12">
      <div className="mx-auto h-16 w-16 rounded-full bg-blue-50 flex items-center justify-center mb-4">
        <Building2 className="h-8 w-8 text-blue-600" />
      </div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">No Organizations</h3>
      <p className="text-gray-500 max-w-sm mx-auto mb-6">
        You are not part of any organizations yet. Create one to start collaborating with your team.
      </p>
      <Button onClick={() => setViewState('create')}>
        <Plus className="h-4 w-4 mr-2" />
        Create Organization
      </Button>
    </div>
  )

  const renderOrganizationList = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Team Management</h2>
          <p className="text-gray-600 mt-1">Manage your organizations and team members</p>
        </div>
        <Button onClick={() => setViewState('create')}>
          <Plus className="h-4 w-4 mr-2" />
          New Organization
        </Button>
      </div>

      {organizations.length === 0 ? (
        renderEmptyState()
      ) : (
        <div className="grid gap-4">
          {organizations.map((org) => (
            <Card
              key={org.id}
              interactive
              onClick={() => handleViewOrganization(org.id)}
              className="cursor-pointer"
            >
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="h-12 w-12 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white font-bold text-lg">
                      {getInitials(org.name)}
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900 text-lg">{org.name}</h3>
                      <div className="flex items-center gap-2 text-sm text-gray-500 mt-1">
                        <Users className="h-4 w-4" />
                        <span>{org.member_count || 1} member{org.member_count !== 1 ? 's' : ''}</span>
                        {org.is_owner && (
                          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                            <Crown className="h-3 w-3 mr-1" />
                            Owner
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  <Button variant="outline" size="sm">
                    Manage
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )

  const renderCreateOrganization = () => (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="outline" onClick={() => setViewState('list')}>
          ← Back
        </Button>
        <h2 className="text-2xl font-bold text-gray-900">Create Organization</h2>
      </div>

      <Card>
        <CardContent className="p-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Organization Name
              </label>
              <Input
                value={newOrgName}
                onChange={(e) => setNewOrgName(e.target.value)}
                placeholder="Enter organization name"
                onKeyDown={(e) => e.key === 'Enter' && handleCreateOrganization()}
              />
            </div>

            <div className="flex items-center gap-2 text-sm text-gray-600">
              <AlertCircle className="h-4 w-4" />
              <span>You will be the owner of this organization.</span>
            </div>

            <div className="flex gap-3 pt-2">
              <Button variant="outline" onClick={() => setViewState('list')}>
                Cancel
              </Button>
              <Button
                onClick={handleCreateOrganization}
                disabled={!newOrgName.trim() || isSubmitting}
              >
                {isSubmitting ? (
                  <>
                    <div className="h-4 w-4 mr-2 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Creating...
                  </>
                ) : (
                  <>
                    <Plus className="h-4 w-4 mr-2" />
                    Create Organization
                  </>
                )}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )

  const renderOrganizationDetail = () => {
    if (!selectedOrg) return null

    const currentRole = getCurrentUserRole()
    const canManage = canManageMembers()

    return (
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-4">
            <Button variant="outline" onClick={() => setViewState('list')}>
              ← Back
            </Button>
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white font-bold">
                {getInitials(selectedOrg.name)}
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{selectedOrg.name}</h2>
                <p className="text-sm text-gray-500">
                  {selectedOrg.member_count || selectedOrg.members.length} members · You are {currentRole}
                </p>
              </div>
            </div>
          </div>
          
          <div className="flex gap-2">
            {isOwner() && (
              <Button
                variant="outline"
                onClick={() => setShowDeleteConfirm(true)}
                className="text-red-600 hover:bg-red-50"
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Delete
              </Button>
            )}
            {!isOwner() && (
              <Button
                variant="outline"
                onClick={() => setShowLeaveConfirm(true)}
                className="text-orange-600 hover:bg-orange-50"
              >
                <LogOut className="h-4 w-4 mr-2" />
                Leave
              </Button>
            )}
          </div>
        </div>

        {/* Invite Section (Admin/Owner only) */}
        {canManage && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <UserPlus className="h-5 w-5" />
                Invite Member
              </CardTitle>
              <CardDescription>
                Invite team members to collaborate in this organization
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex gap-3">
                <Input
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                  placeholder="Enter email address"
                  className="flex-1"
                  onKeyDown={(e) => e.key === 'Enter' && handleInviteMember()}
                />
                <select
                  value={inviteRole}
                  onChange={(e) => setInviteRole(e.target.value as OrganizationRole)}
                  className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="member">Member</option>
                  <option value="admin">Admin</option>
                </select>
                <Button
                  onClick={handleInviteMember}
                  disabled={!inviteEmail.trim() || isSubmitting}
                >
                  {isSubmitting ? (
                    <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <>
                      <UserPlus className="h-4 w-4 mr-2" />
                      Invite
                    </>
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Members List */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5" />
              Members
            </CardTitle>
            <CardDescription>
              Manage organization members and their roles
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {selectedOrg.members.map((member) => {
                const isCurrentUser = member.user_id === user?.id
                const isOrgOwner = member.user_id === selectedOrg.owner_id
                const canEdit = canManage && !isCurrentUser && !isOrgOwner

                return (
                  <div
                    key={member.id}
                    className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className={`h-10 w-10 rounded-full flex items-center justify-center text-white text-sm font-medium ${
                          member.avatar_url ? '' : getAvatarColor(member.user_id)
                        }`}
                        style={
                          member.avatar_url
                            ? { backgroundImage: `url(${member.avatar_url})`, backgroundSize: 'cover' }
                            : {}
                        }
                      >
                        {!member.avatar_url && getInitials(member.user_name || 'U')}
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-gray-900">
                            {member.user_name || 'Unknown User'}
                            {isCurrentUser && (
                              <span className="text-gray-400 font-normal ml-1">(You)</span>
                            )}
                          </span>
                          {isOrgOwner && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                              <Crown className="h-3 w-3 mr-1" />
                              Owner
                            </span>
                          )}
                        </div>
                        <span className="text-sm text-gray-500">{member.user_email || member.user_id}</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-3">
                      {canEdit ? (
                        <>
                          <select
                            value={member.role}
                            onChange={(e) => handleUpdateMemberRole(member.id, e.target.value as OrganizationRole)}
                            disabled={actionLoading === `role-${member.id}`}
                            className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          >
                            <option value="member">Member</option>
                            <option value="admin">Admin</option>
                          </select>

                          {isOwner() && (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => setShowTransferConfirm(member.user_id)}
                              disabled={actionLoading === 'transfer'}
                              className="text-blue-600 hover:bg-blue-50"
                            >
                              <Crown className="h-4 w-4 mr-1" />
                              Make Owner
                            </Button>
                          )}

                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setShowRemoveConfirm(member.id)}
                            disabled={actionLoading === `remove-${member.id}`}
                            className="text-red-600 hover:bg-red-50"
                          >
                            <UserMinus className="h-4 w-4" />
                          </Button>
                        </>
                      ) : (
                        <span
                          className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${
                            isOrgOwner
                              ? 'bg-yellow-100 text-yellow-800'
                              : member.role === 'admin'
                              ? 'bg-blue-100 text-blue-800'
                              : 'bg-gray-100 text-gray-800'
                          }`}
                        >
                          {isOrgOwner ? (
                            <>
                              <Crown className="h-3 w-3 mr-1" />
                              Owner
                            </>
                          ) : member.role === 'admin' ? (
                            <>
                              <Shield className="h-3 w-3 mr-1" />
                              Admin
                            </>
                          ) : (
                            <>
                              <User className="h-3 w-3 mr-1" />
                              Member
                            </>
                          )}
                        </span>
                      )}
                    </div>
                  </div>
                )
              })}

              {selectedOrg.members.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  No members found
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Delete Confirmation Modal */}
        {showDeleteConfirm && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <Card className="w-full max-w-md">
              <CardHeader>
                <CardTitle className="text-red-600 flex items-center gap-2">
                  <AlertCircle className="h-5 w-5" />
                  Delete Organization
                </CardTitle>
                <CardDescription>
                  Are you sure you want to delete <strong>{selectedOrg.name}</strong>? This action cannot be undone.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex gap-3 justify-end">
                  <Button variant="outline" onClick={() => setShowDeleteConfirm(false)}>
                    Cancel
                  </Button>
                  <Button
                    onClick={handleDeleteOrganization}
                    disabled={actionLoading === 'delete'}
                    className="bg-red-600 hover:bg-red-700"
                  >
                    {actionLoading === 'delete' ? (
                      <div className="h-4 w-4 mr-2 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    ) : (
                      <Trash2 className="h-4 w-4 mr-2" />
                    )}
                    Delete Organization
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Leave Confirmation Modal */}
        {showLeaveConfirm && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <Card className="w-full max-w-md">
              <CardHeader>
                <CardTitle className="text-orange-600 flex items-center gap-2">
                  <LogOut className="h-5 w-5" />
                  Leave Organization
                </CardTitle>
                <CardDescription>
                  Are you sure you want to leave <strong>{selectedOrg.name}</strong>? You will lose access to all organization content.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex gap-3 justify-end">
                  <Button variant="outline" onClick={() => setShowLeaveConfirm(false)}>
                    Cancel
                  </Button>
                  <Button
                    onClick={handleLeaveOrganization}
                    disabled={actionLoading === 'leave'}
                    className="bg-orange-600 hover:bg-orange-700"
                  >
                    {actionLoading === 'leave' ? (
                      <div className="h-4 w-4 mr-2 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    ) : (
                      <LogOut className="h-4 w-4 mr-2" />
                    )}
                    Leave Organization
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Remove Member Confirmation Modal */}
        {showRemoveConfirm && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <Card className="w-full max-w-md">
              <CardHeader>
                <CardTitle className="text-red-600 flex items-center gap-2">
                  <AlertCircle className="h-5 w-5" />
                  Remove Member
                </CardTitle>
                <CardDescription>
                  Are you sure you want to remove this member from the organization?
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex gap-3 justify-end">
                  <Button variant="outline" onClick={() => setShowRemoveConfirm(null)}>
                    Cancel
                  </Button>
                  <Button
                    onClick={() => handleRemoveMember(showRemoveConfirm)}
                    disabled={actionLoading?.startsWith('remove')}
                    className="bg-red-600 hover:bg-red-700"
                  >
                    {actionLoading?.startsWith('remove') ? (
                      <div className="h-4 w-4 mr-2 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    ) : (
                      <UserMinus className="h-4 w-4 mr-2" />
                    )}
                    Remove Member
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Transfer Ownership Confirmation Modal */}
        {showTransferConfirm && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <Card className="w-full max-w-md">
              <CardHeader>
                <CardTitle className="text-blue-600 flex items-center gap-2">
                  <Crown className="h-5 w-5" />
                  Transfer Ownership
                </CardTitle>
                <CardDescription>
                  Are you sure you want to transfer ownership of <strong>{selectedOrg.name}</strong> to this member? You will become an admin.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex gap-3 justify-end">
                  <Button variant="outline" onClick={() => setShowTransferConfirm(null)}>
                    Cancel
                  </Button>
                  <Button
                    onClick={() => handleTransferOwnership(showTransferConfirm)}
                    disabled={actionLoading === 'transfer'}
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    {actionLoading === 'transfer' ? (
                      <div className="h-4 w-4 mr-2 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    ) : (
                      <Crown className="h-4 w-4 mr-2" />
                    )}
                    Transfer Ownership
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    )
  }

  if (loading && viewState === 'list') {
    return renderLoading()
  }

  switch (viewState) {
    case 'create':
      return renderCreateOrganization()
    case 'detail':
      return renderOrganizationDetail()
    case 'list':
    default:
      return renderOrganizationList()
  }
}
