'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  MessageSquare,
  Send,
  Reply,
  Check,
  Smile,
  AtSign,
  MoreHorizontal,
  Pin,
  ThumbsUp,
  Heart,
  Laugh,
  Frown,
  RefreshCw,
  Loader2,
} from 'lucide-react'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { useToast } from '@/hooks/useToast'
import { cn } from '@/lib/utils'
import {
  getComments,
  createComment,
  updateComment,
  deleteComment,
  resolveComment,
  unresolveComment,
  addCommentReaction,
  removeCommentReaction,
  getCommentReactions,
  lookupMentions,
  type ContentComment,
  type MentionUser,
} from '@/lib/api'

interface EMOJI_OPTION {
  emoji: string
  label: string
}

const EMOJI_OPTIONS: EMOJI_OPTION[] = [
  { emoji: '👍', label: 'Thumbs Up' },
  { emoji: '❤️', label: 'Heart' },
  { emoji: '😂', label: 'Laugh' },
  { emoji: '😮', label: 'Surprised' },
  { emoji: '🎉', label: 'Celebrate' },
  { emoji: '🤔', label: 'Thinking' },
  { emoji: '👀', label: 'Eyes' },
  { emoji: '🔥', label: 'Fire' },
]

interface CommentsPanelProps {
  contentId?: string
}

// Reactions state per comment (fetched separately or embedded)
interface ReactionMap {
  [emoji: string]: string[]  // emoji -> user_ids
}

export default function CommentsPanel({ contentId }: CommentsPanelProps) {
  const [comments, setComments] = useState<ContentComment[]>([])
  const [reactions, setReactions] = useState<Record<string, ReactionMap>>({})
  const [loading, setLoading] = useState(!contentId)
  const [newComment, setNewComment] = useState('')
  const [replyingTo, setReplyingTo] = useState<string | null>(null)
  const [replyText, setReplyText] = useState('')
  const [showEmojiPicker, setShowEmojiPicker] = useState<string | null>(null)
  const [showMentions, setShowMentions] = useState(false)
  const [mentionFilter, setMentionFilter] = useState('')
  const [mentionTarget, setMentionTarget] = useState<'new' | string>('new')
  const [mentionUsers, setMentionUsers] = useState<MentionUser[]>([])
  const [expandedThreads, setExpandedThreads] = useState<Set<string>>(new Set())
  const commentInputRef = useRef<HTMLTextAreaElement>(null)
  const { showToast } = useToast()

  const loadComments = useCallback(async () => {
    if (!contentId) return
    try {
      setLoading(true)
      const result = await getComments(contentId)
      setComments(result.items)
      // Load reactions for each comment
      const reactionMap: Record<string, ReactionMap> = {}
      for (const comment of result.items) {
        try {
          const cReactions = await getCommentReactions(comment.id)
          reactionMap[comment.id] = {}
          for (const r of cReactions) {
            reactionMap[comment.id][r.emoji] = r.user_ids
          }
        } catch {
          // Reactions may not exist yet
          reactionMap[comment.id] = {}
        }
      }
      setReactions(reactionMap)
    } catch {
      showToast('Failed to load comments', 'error')
    } finally {
      setLoading(false)
    }
  }, [contentId, showToast])

  useEffect(() => {
    loadComments()
  }, [loadComments])

  const topLevelComments = comments.filter(c => c.parent_id === null)

  const getReplies = (commentId: string) => comments.filter(c => c.parent_id === commentId)

  const handleAddComment = async () => {
    if (!contentId || !newComment.trim()) return
    try {
      const created = await createComment(contentId, { text: newComment.trim() })
      setComments(prev => [...prev, created])
      setReactions(prev => ({ ...prev, [created.id]: {} }))
      setNewComment('')
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to add comment'
      showToast(message, 'error')
    }
  }

  const handleAddReply = async (parentId: string) => {
    if (!contentId || !replyText.trim()) return
    try {
      const created = await createComment(contentId, {
        text: replyText.trim(),
        parent_id: parentId,
      })
      setComments(prev => [...prev, created])
      setReactions(prev => ({ ...prev, [created.id]: {} }))
      setReplyText('')
      setReplyingTo(null)
      // Auto-expand parent thread
      setExpandedThreads(prev => new Set([...prev, parentId]))
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to add reply'
      showToast(message, 'error')
    }
  }

  const handleResolve = async (commentId: string) => {
    const comment = comments.find(c => c.id === commentId)
    if (!comment) return

    try {
      if (comment.is_resolved) {
        await unresolveComment(commentId)
      } else {
        await resolveComment(commentId)
      }
      setComments(prev =>
        prev.map(c => c.id === commentId ? { ...c, is_resolved: !c.is_resolved } : c)
      )
      showToast(comment.is_resolved ? 'Comment reopened' : 'Comment resolved', 'success')
    } catch {
      showToast('Failed to update comment status', 'error')
    }
  }

  const handleReaction = async (commentId: string, emoji: string) => {
    const commentReactions = reactions[commentId] || {}
    const users = commentReactions[emoji] || []
    // Determine current user ID from any existing reaction
    // For now, toggle: if reaction exists, remove; otherwise add
    try {
      if (users.length > 0) {
        // Try removing first (assuming current user added it)
        await removeCommentReaction(commentId, emoji)
        setReactions(prev => {
          const map = { ...(prev[commentId] || {}) }
          const uList = [...(map[emoji] || [])]
          // Remove last user (approximation - we don't have current user ID easily)
          if (uList.length > 0) uList.pop()
          if (uList.length === 0) delete map[emoji]
          else map[emoji] = uList
          return { ...prev, [commentId]: map }
        })
      } else {
        await addCommentReaction(commentId, emoji)
        setReactions(prev => {
          const map = { ...(prev[commentId] || {}) }
          map[emoji] = ['current-user'] // Placeholder, will refresh on next load
          return { ...prev, [commentId]: map }
        })
      }
    } catch {
      // Silently fail for reactions
    }
    setShowEmojiPicker(null)
  }

  const handleMentionInput = async (value: string, target: 'new' | string) => {
    setMentionTarget(target)
    if (target === 'new') {
      setNewComment(value)
    } else {
      setReplyText(value)
    }
    const lastAtIndex = value.lastIndexOf('@')
    if (lastAtIndex !== -1) {
      const filterText = value.slice(lastAtIndex + 1).split(' ')[0]
      setMentionFilter(filterText)
      setShowMentions(true)
      // Fetch mention suggestions from API
      try {
        const users = await lookupMentions(filterText)
        setMentionUsers(users)
      } catch {
        setMentionUsers([])
      }
    } else {
      setShowMentions(false)
    }
  }

  const selectMention = (user: MentionUser) => {
    const currentText = mentionTarget === 'new' ? newComment : replyText
    const lastAtIndex = currentText.lastIndexOf('@')
    const beforeMention = currentText.slice(0, lastAtIndex)
    const userName = user.full_name || user.email || 'User'
    const newText = `${beforeMention}@${userName} `
    if (mentionTarget === 'new') {
      setNewComment(newText)
    } else {
      setReplyText(newText)
    }
    setShowMentions(false)
  }

  const toggleThread = (commentId: string) => {
    setExpandedThreads(prev => {
      const next = new Set(prev)
      if (next.has(commentId)) next.delete(commentId)
      else next.add(commentId)
      return next
    })
  }

  const formatTimeAgo = (dateStr: string) => {
    const date = new Date(dateStr)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    if (diffMins < 60) return `${diffMins}m ago`
    const diffHours = Math.floor(diffMins / 60)
    if (diffHours < 24) return `${diffHours}h ago`
    const diffDays = Math.floor(diffHours / 24)
    if (diffDays < 7) return `${diffDays}d ago`
    return date.toLocaleDateString()
  }

  // Get author display name from user_id (we use user_id as fallback)
  const getAuthorName = (comment: ContentComment) => {
    // The backend returns user_id; we can try to resolve from mentions or show user_id prefix
    return comment.user_id.slice(0, 8)
  }

  if (!contentId) {
    return (
      <div className="flex flex-col items-center py-16">
        <MessageSquare className="w-12 h-12 text-slate-300 dark:text-slate-600 mb-4" />
        <h3 className="text-lg font-semibold text-slate-500 dark:text-slate-400 mb-2">No Content Selected</h3>
        <p className="text-sm text-slate-400 dark:text-slate-500">Select a content item to view and manage its comments.</p>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="flex flex-col items-center py-12">
        <Loader2 className="w-8 h-8 text-blue-400 animate-spin mb-3" />
        <p className="text-slate-400">Loading comments...</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
            <MessageSquare className="w-6 h-6 text-blue-500" />
            Comments
          </h2>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            {comments.filter(c => !c.is_resolved).length} unresolved · {comments.length} total
          </p>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={loadComments}
          title="Refresh comments"
        >
          <RefreshCw className="w-4 h-4" />
        </Button>
      </div>

      {/* New Comment Input */}
      <Card variant="glass">
        <CardContent>
          <div className="flex gap-3">
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center">
              <span className="text-white text-xs font-bold">Y</span>
            </div>
            <div className="flex-1">
              <div className="relative">
                <textarea
                  ref={commentInputRef}
                  value={newComment}
                  onChange={e => handleMentionInput(e.target.value, 'new')}
                  className="w-full px-4 py-3 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-sm text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                  rows={3}
                  placeholder="Add a comment... (use @ to mention someone)"
                />
                {/* Mention autocomplete */}
                <AnimatePresence>
                  {showMentions && mentionUsers.length > 0 && (
                    <motion.div
                      initial={{ opacity: 0, y: -5 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -5 }}
                      className="absolute left-0 bottom-full mb-2 w-56 py-1 bg-white dark:bg-slate-800 rounded-xl shadow-xl border border-slate-200 dark:border-slate-700 z-30 max-h-48 overflow-auto"
                    >
                      {mentionUsers
                        .filter(u => {
                          const name = u.full_name || u.email || ''
                          return name.toLowerCase().includes(mentionFilter.toLowerCase())
                        })
                        .map(user => (
                          <button
                            key={user.id}
                            onClick={() => selectMention(user)}
                            className="w-full px-3 py-2 text-sm text-left hover:bg-slate-50 dark:hover:bg-slate-700 flex items-center gap-2"
                          >
                            <div className="w-6 h-6 rounded-full bg-gradient-to-br from-blue-400 to-violet-500 flex items-center justify-center">
                              <span className="text-white text-[10px] font-bold">
                                {(user.full_name || user.email || 'U')[0]}
                              </span>
                            </div>
                            <span className="text-slate-900 dark:text-slate-100">
                              {user.full_name || user.email}
                            </span>
                          </button>
                        ))}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
              <div className="flex items-center justify-between mt-2">
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => {
                      const textarea = commentInputRef.current
                      if (textarea) {
                        const pos = textarea.selectionStart
                        const before = newComment.slice(0, pos)
                        const after = newComment.slice(pos)
                        setNewComment(`${before}@${after}`)
                        setShowMentions(true)
                        setMentionFilter('')
                        textarea.focus()
                      }
                    }}
                    className="p-1.5 rounded-lg text-slate-400 hover:text-blue-500 hover:bg-blue-50 dark:hover:bg-blue-500/10 transition-colors"
                    title="Mention someone"
                  >
                    <AtSign className="h-4 w-4" />
                  </button>
                </div>
                <Button
                  variant="primary"
                  size="sm"
                  onClick={handleAddComment}
                  disabled={!newComment.trim()}
                >
                  <Send className="h-3.5 w-3.5 mr-1" />
                  Comment
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Comments List */}
      <div className="space-y-4">
        <AnimatePresence>
          {topLevelComments.length === 0 ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center py-12"
            >
              <MessageSquare className="h-12 w-12 text-slate-300 dark:text-slate-600 mx-auto mb-4" />
              <p className="text-slate-500 dark:text-slate-400 text-lg font-medium">No comments yet</p>
              <p className="text-slate-400 dark:text-slate-500 text-sm mt-1">
                Start the conversation by adding a comment
              </p>
            </motion.div>
          ) : (
            topLevelComments.map((comment, index) => {
              const replies = getReplies(comment.id)
              const isExpanded = expandedThreads.has(comment.id)
              const commentReactions = reactions[comment.id] || {}
              return (
                <motion.div
                  key={comment.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <Card
                    variant="glass"
                    className={cn(
                      comment.is_resolved && 'opacity-60'
                    )}
                  >
                    <CardContent>
                      {/* Comment Header */}
                      <div className="flex items-start gap-3">
                        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-violet-400 to-purple-600 flex items-center justify-center">
                          <span className="text-white text-xs font-bold">
                            {getAuthorName(comment)[0]}
                          </span>
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="font-semibold text-sm text-slate-900 dark:text-slate-100">
                              {getAuthorName(comment)}
                            </span>
                            <span className="text-xs text-slate-500 dark:text-slate-400">
                              {formatTimeAgo(comment.created_at)}
                            </span>
                            {comment.is_resolved && (
                              <Badge variant="success" size="sm">Resolved</Badge>
                            )}
                          </div>
                          <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
                            {comment.text}
                          </p>

                          {/* Reactions */}
                          <div className="flex items-center gap-2 mt-2 flex-wrap">
                            {Object.entries(commentReactions).map(([emoji, users]) => (
                              <button
                                key={emoji}
                                onClick={() => handleReaction(comment.id, emoji)}
                                className={cn(
                                  'inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs transition-colors',
                                  users.includes('current-user')
                                    ? 'bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-500/30'
                                    : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700 hover:bg-slate-200 dark:hover:bg-slate-700'
                                )}
                              >
                                <span>{emoji}</span>
                                <span>{users.length}</span>
                              </button>
                            ))}
                            <div className="relative">
                              <button
                                onClick={() => setShowEmojiPicker(showEmojiPicker === comment.id ? null : comment.id)}
                                className="p-1 rounded-full text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
                              >
                                <Smile className="h-4 w-4" />
                              </button>
                              <AnimatePresence>
                                {showEmojiPicker === comment.id && (
                                  <motion.div
                                    initial={{ opacity: 0, scale: 0.9 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    exit={{ opacity: 0, scale: 0.9 }}
                                    className="absolute left-0 bottom-full mb-2 p-2 bg-white dark:bg-slate-800 rounded-xl shadow-xl border border-slate-200 dark:border-slate-700 z-20 grid grid-cols-4 gap-1"
                                  >
                                    {EMOJI_OPTIONS.map(opt => (
                                      <button
                                        key={opt.emoji}
                                        onClick={() => handleReaction(comment.id, opt.emoji)}
                                        className="p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors text-lg"
                                        title={opt.label}
                                      >
                                        {opt.emoji}
                                      </button>
                                    ))}
                                  </motion.div>
                                )}
                              </AnimatePresence>
                            </div>
                          </div>

                          {/* Actions */}
                          <div className="flex items-center gap-3 mt-2">
                            <button
                              onClick={() => {
                                setReplyingTo(replyingTo === comment.id ? null : comment.id)
                                setReplyText('')
                              }}
                              className="text-xs text-slate-500 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 flex items-center gap-1 transition-colors"
                            >
                              <Reply className="h-3.5 w-3.5" />
                              Reply
                            </button>
                            <button
                              onClick={() => handleResolve(comment.id)}
                              className="text-xs text-slate-500 dark:text-slate-400 hover:text-emerald-600 dark:hover:text-emerald-400 flex items-center gap-1 transition-colors"
                            >
                              <Check className="h-3.5 w-3.5" />
                              {comment.is_resolved ? 'Reopen' : 'Resolve'}
                            </button>
                          </div>

                          {/* Reply Input */}
                          <AnimatePresence>
                            {replyingTo === comment.id && (
                              <motion.div
                                initial={{ height: 0, opacity: 0 }}
                                animate={{ height: 'auto', opacity: 1 }}
                                exit={{ height: 0, opacity: 0 }}
                                className="overflow-hidden"
                              >
                                <div className="mt-3 pl-4 border-l-2 border-blue-500/30">
                                  <div className="flex gap-2">
                                    <textarea
                                      value={replyText}
                                      onChange={e => handleMentionInput(e.target.value, comment.id)}
                                      className="flex-1 px-3 py-2 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-sm text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                                      rows={2}
                                      placeholder={`Reply...`}
                                    />
                                  </div>
                                  <div className="flex items-center gap-2 mt-2">
                                    <Button variant="primary" size="sm" onClick={() => handleAddReply(comment.id)} disabled={!replyText.trim()}>
                                      Reply
                                    </Button>
                                    <Button variant="ghost" size="sm" onClick={() => { setReplyingTo(null); setReplyText('') }}>
                                      Cancel
                                    </Button>
                                  </div>
                                </div>
                              </motion.div>
                            )}
                          </AnimatePresence>

                          {/* Replies */}
                          {replies.length > 0 && (
                            <div className="mt-3">
                              <button
                                onClick={() => toggleThread(comment.id)}
                                className="text-xs text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-1 mb-2"
                              >
                                {isExpanded ? 'Hide' : 'Show'} {replies.length} {replies.length === 1 ? 'reply' : 'replies'}
                              </button>
                              <AnimatePresence>
                                {isExpanded && (
                                  <motion.div
                                    initial={{ height: 0, opacity: 0 }}
                                    animate={{ height: 'auto', opacity: 1 }}
                                    exit={{ height: 0, opacity: 0 }}
                                    className="space-y-3 pl-4 border-l-2 border-slate-200 dark:border-slate-700"
                                  >
                                    {replies.map((reply, ri) => {
                                      const replyReactions = reactions[reply.id] || {}
                                      return (
                                        <motion.div
                                          key={reply.id}
                                          initial={{ opacity: 0, x: -10 }}
                                          animate={{ opacity: 1, x: 0 }}
                                          transition={{ delay: ri * 0.05 }}
                                          className="flex items-start gap-2"
                                        >
                                          <div className="flex-shrink-0 w-6 h-6 rounded-full bg-gradient-to-br from-emerald-400 to-teal-600 flex items-center justify-center">
                                            <span className="text-white text-[10px] font-bold">
                                              {getAuthorName(reply)[0]}
                                            </span>
                                          </div>
                                          <div className="flex-1 min-w-0">
                                            <div className="flex items-center gap-2">
                                              <span className="font-medium text-xs text-slate-900 dark:text-slate-100">
                                                {getAuthorName(reply)}
                                              </span>
                                              <span className="text-xs text-slate-400">
                                                {formatTimeAgo(reply.created_at)}
                                              </span>
                                            </div>
                                            <p className="text-sm text-slate-600 dark:text-slate-400 mt-0.5">
                                              {reply.text}
                                            </p>
                                            <div className="flex items-center gap-2 mt-1">
                                              {Object.entries(replyReactions).map(([emoji, users]) => (
                                                <button
                                                  key={emoji}
                                                  onClick={() => handleReaction(reply.id, emoji)}
                                                  className={cn(
                                                    'inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full text-[10px] transition-colors',
                                                    users.includes('current-user')
                                                      ? 'bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-300'
                                                      : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400'
                                                  )}
                                                >
                                                  <span>{emoji}</span>
                                                  <span>{users.length}</span>
                                                </button>
                                              ))}
                                            </div>
                                          </div>
                                        </motion.div>
                                      )
                                    })}
                                  </motion.div>
                                )}
                              </AnimatePresence>
                            </div>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              )
            })
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}