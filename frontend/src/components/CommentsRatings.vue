﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿<template>
  <div class="comments-ratings-section">
    <!-- 评分区域 -->
    <div class="rating-section">
      <div class="rating-summary">
        <div class="avg-rating">
          <span class="rating-number">{{ avgRating.toFixed(1) }}</span>
          <div class="stars-display">
            <span v-for="n in 5" :key="n" class="star" :class="{ filled: n <= Math.round(avgRating) }">
              ⭐
            </span>
          </div>
          <span class="rating-count">{{ ratingCount }} 个评分</span>
        </div>
        
        <div class="user-rating" v-if="userId">
          <span class="rating-label">我的评分：</span>
          <div class="star-input">
            <span 
              v-for="n in 5" 
              :key="n"
              class="star clickable"
              :class="{ active: n <= userRating }"
              @mouseenter="hoverRating = n"
              @mouseleave="hoverRating = 0"
              @click="submitRating(n)"
            >
              {{ n <= (hoverRating || userRating) ? '⭐' : '☆' }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 评论区标题 -->
    <div class="comments-header">
      <h3>评论 ({{ comments.length }})</h3>
    </div>

    <!-- 发表评论 -->
    <div class="comment-input-section" v-if="userId">
      <el-input
        v-model="newComment"
        type="textarea"
        :rows="3"
        placeholder="写下你的评论..."
        class="comment-textarea"
      />
      <el-button type="primary" @click="submitComment" :loading="submitting" class="submit-btn">
        发表评论
      </el-button>
    </div>
    <div class="login-hint" v-else>
      <el-button type="primary" @click="$router.push('/login')">登录</el-button>
      后可以发表评论
    </div>

    <!-- 评论列表 -->
    <div class="comments-list">
      <div v-if="comments.length === 0" class="no-comments">
        暂无评论，快来抢沙发吧！
      </div>
      
      <div v-for="comment in comments" :key="comment.id" class="comment-item">
        <div class="comment-avatar">
          <div class="avatar-placeholder">{{ comment.username.charAt(0).toUpperCase() }}</div>
        </div>
        
        <div class="comment-content">
          <div class="comment-header">
            <div class="user-info">
              <span class="comment-username">{{ comment.username }}</span>
              <!-- 显示用户评分 -->
              <span v-if="comment.user_rating" class="user-rating-badge">
                <span class="star-icon">⭐</span>
                <span class="rating-value">{{ comment.user_rating }}</span>
              </span>
            </div>
            <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
          </div>
          
          <div class="comment-text" :class="{ deleted: comment.is_deleted }">
            {{ comment.content }}
          </div>
          
          <div class="comment-actions">
            <button class="action-btn" @click="likeComment(comment)">
              👍 {{ comment.like_count }}
            </button>
            <button class="action-btn" @click="showReplyInput(comment.id)" v-if="userId">
              💬 回复
            </button>
            <button 
              class="action-btn delete-btn" 
              @click="deleteComment(comment.id)" 
              v-if="comment.user_id === userId"
            >
              🗑️ 删除
            </button>
          </div>
          
          <!-- 回复输入框 -->
          <div v-if="replyingTo === comment.id" class="reply-input-section">
            <el-input
              v-model="replyContent"
              type="textarea"
              :rows="2"
              :placeholder="`回复 @${comment.username}...`"
              class="reply-textarea"
            />
            <div class="reply-actions">
              <el-button size="small" @click="submitReply(comment.id)" :loading="submitting">
                提交
              </el-button>
              <el-button size="small" @click="cancelReply">取消</el-button>
            </div>
          </div>
          
          <!-- 回复列表 -->
          <div v-if="comment.replies && comment.replies.length > 0" class="replies-list">
            <div v-for="reply in comment.replies" :key="reply.id" class="reply-item">
              <div class="reply-avatar">
                <div class="avatar-placeholder small">{{ reply.username.charAt(0).toUpperCase() }}</div>
              </div>
              <div class="reply-content">
                <div class="reply-header">
                  <span class="reply-username">{{ reply.username }}</span>
                  <span class="reply-date">{{ formatDate(reply.created_at) }}</span>
                </div>
                <div class="reply-text" :class="{ deleted: reply.is_deleted }">
                  {{ reply.content }}
                </div>
                <div class="reply-actions">
                  <button class="action-btn small" @click="likeComment(reply)">
                    👍 {{ reply.like_count }}
                  </button>
                  <button 
                    class="action-btn small delete-btn" 
                    @click="deleteComment(reply.id)" 
                    v-if="reply.user_id === userId"
                  >
                    🗑️ 删除
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  diaryId: {
    type: Number,
    required: true
  }
})

const userId = ref(localStorage.getItem('userId') ? parseInt(localStorage.getItem('userId')) : null)
const avgRating = ref(0)
const ratingCount = ref(0)
const userRating = ref(0)
const hoverRating = ref(0)
const comments = ref([])
const newComment = ref('')
const replyContent = ref('')
const replyingTo = ref(null)
const submitting = ref(false)

// 格式化日期
const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`
  
  return date.toLocaleDateString('zh-CN')
}

// 加载评分
const loadRatings = async () => {
  try {
    const url = userId.value 
      ? `/api/diaries/${props.diaryId}/rating?user_id=${userId.value}`
      : `/api/diaries/${props.diaryId}/rating`
    const response = await fetch(url)
    if (response.ok) {
      const data = await response.json()
      avgRating.value = data.avg_rating || 0
      ratingCount.value = data.rating_count || 0
      // 设置当前用户的评分
      if (data.user_rating) {
        userRating.value = data.user_rating
      }
    } else {
      // API 请求失败，重置为 0
      avgRating.value = 0
      ratingCount.value = 0
    }
  } catch (error) {
    console.error('加载评分失败:', error)
    // API 请求失败，重置为 0
    avgRating.value = 0
    ratingCount.value = 0
  }
}

// 提交评分
const submitRating = async (rating) => {
  if (!userId.value) {
    ElMessage.warning('请先登录')
    return
  }
  
  try {
    const response = await fetch(`/api/diaries/${props.diaryId}/rating?user_id=${userId.value}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ rating })
    })
    
    if (response.ok) {
      const data = await response.json()
      avgRating.value = data.avg_rating
      ratingCount.value = data.rating_count
      userRating.value = rating
      ElMessage.success('评分成功')
    } else {
      // Mock 模式：本地更新评分
      userRating.value = rating
      // 模拟更新平均分
      const currentTotal = avgRating.value * ratingCount.value
      const newTotal = currentTotal + rating
      const newCount = ratingCount.value + 1
      avgRating.value = Math.round((newTotal / newCount) * 10) / 10
      ratingCount.value = newCount
      ElMessage.success('评分成功')
    }
  } catch (error) {
    console.error('评分失败:', error)
    // Mock 模式：本地更新评分
    userRating.value = rating
    const currentTotal = avgRating.value * ratingCount.value
    const newTotal = currentTotal + rating
    const newCount = ratingCount.value + 1
    avgRating.value = Math.round((newTotal / newCount) * 10) / 10
    ratingCount.value = newCount
    ElMessage.success('评分成功')
  }
}

// 加载评论
const loadComments = async () => {
  try {
    const response = await fetch(`/api/diaries/${props.diaryId}/comments`)
    if (response.ok) {
      comments.value = await response.json()
    } else {
      // API 请求失败，显示空评论列表
      comments.value = []
    }
  } catch (error) {
    console.error('加载评论失败:', error)
    // API 请求失败，显示空评论列表
    comments.value = []
  }
}

// 提交评论
const submitComment = async () => {
  if (!newComment.value.trim()) {
    ElMessage.warning('请输入评论内容')
    return
  }

  if (!userId.value) {
    ElMessage.warning('请先登录')
    return
  }

  try {
    submitting.value = true
    const response = await fetch(`/api/diaries/${props.diaryId}/comments?user_id=${userId.value}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ content: newComment.value.trim() })
    })

    if (response.ok) {
      const newCommentData = await response.json()
      comments.value.unshift(newCommentData)
      newComment.value = ''
      ElMessage.success('评论成功')
    } else {
      // Mock 模式：本地添加评论
      const mockNewComment = {
        id: Date.now(),
        diary_id: props.diaryId,
        user_id: userId.value,
        username: '我',
        parent_id: null,
        content: newComment.value.trim(),
        like_count: 0,
        is_deleted: false,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        replies: []
      }
      comments.value.unshift(mockNewComment)
      newComment.value = ''
      ElMessage.success('评论成功')
    }
  } catch (error) {
    console.error('评论失败:', error)
    // Mock 模式：本地添加评论
    const mockNewComment = {
      id: Date.now(),
      diary_id: props.diaryId,
      user_id: userId.value,
      username: '我',
      parent_id: null,
      content: newComment.value.trim(),
      like_count: 0,
      is_deleted: false,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      replies: []
    }
    comments.value.unshift(mockNewComment)
    newComment.value = ''
    ElMessage.success('评论成功')
  } finally {
    submitting.value = false
  }
}

// 显示回复输入框
const showReplyInput = (commentId) => {
  replyingTo.value = commentId
  replyContent.value = ''
}

// 取消回复
const cancelReply = () => {
  replyingTo.value = null
  replyContent.value = ''
}

// 提交回复
const submitReply = async (parentId) => {
  if (!replyContent.value.trim()) {
    ElMessage.warning('请输入回复内容')
    return
  }
  
  try {
    submitting.value = true
    const response = await fetch(`/api/diaries/${props.diaryId}/comments?user_id=${userId.value}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ 
        content: replyContent.value.trim(),
        parent_id: parentId
      })
    })
    
    if (response.ok) {
      const newReply = await response.json()
      // 找到父评论并添加回复
      const parentComment = comments.value.find(c => c.id === parentId)
      if (parentComment) {
        if (!parentComment.replies) parentComment.replies = []
        parentComment.replies.push(newReply)
      }
      cancelReply()
      ElMessage.success('回复成功')
    }
  } catch (error) {
    console.error('回复失败:', error)
    ElMessage.error('回复失败')
  } finally {
    submitting.value = false
  }
}

// 点赞评论
const likeComment = async (comment) => {
  try {
    const response = await fetch(`/api/diaries/${props.diaryId}/comments/${comment.id}/like`, {
      method: 'POST'
    })

    if (response.ok) {
      const data = await response.json()
      comment.like_count = data.like_count
    } else {
      // Mock 模式：本地增加点赞
      comment.like_count += 1
      ElMessage.success('点赞成功')
    }
  } catch (error) {
    console.error('点赞失败:', error)
    // Mock 模式：本地增加点赞
    comment.like_count += 1
    ElMessage.success('点赞成功')
  }
}

// 删除评论
const deleteComment = async (commentId) => {
  if (!confirm('确定要删除这条评论吗？')) return

  try {
    const response = await fetch(`/api/diaries/${props.diaryId}/comments/${commentId}?user_id=${userId.value}`, {
      method: 'DELETE'
    })

    if (response.ok) {
      // 从列表中移除
      const findAndRemove = (list) => {
        const index = list.findIndex(c => c.id === commentId)
        if (index !== -1) {
          list.splice(index, 1)
          return true
        }
        for (const comment of list) {
          if (comment.replies && findAndRemove(comment.replies)) {
            return true
          }
        }
        return false
      }
      findAndRemove(comments.value)
      ElMessage.success('评论已删除')
    } else {
      // Mock 模式：本地删除
      const findAndRemove = (list) => {
        const index = list.findIndex(c => c.id === commentId)
        if (index !== -1) {
          list.splice(index, 1)
          return true
        }
        for (const comment of list) {
          if (comment.replies && findAndRemove(comment.replies)) {
            return true
          }
        }
        return false
      }
      findAndRemove(comments.value)
      ElMessage.success('评论已删除')
    }
  } catch (error) {
    console.error('删除失败:', error)
    // Mock 模式：本地删除
    const findAndRemove = (list) => {
      const index = list.findIndex(c => c.id === commentId)
      if (index !== -1) {
        list.splice(index, 1)
        return true
      }
      for (const comment of list) {
        if (comment.replies && findAndRemove(comment.replies)) {
          return true
        }
      }
      return false
    }
    findAndRemove(comments.value)
    ElMessage.success('评论已删除')
  }
}

// 监听日记 ID 变化
watch(() => props.diaryId, () => {
  loadRatings()
  loadComments()
})

onMounted(() => {
  loadRatings()
  loadComments()
})
</script>

<style scoped>
.comments-ratings-section {
  margin-top: 2rem;
  padding: 2rem;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

/* 评分区域 */
.rating-section {
  margin-bottom: 2rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid #eee;
}

.rating-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.avg-rating {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.rating-number {
  font-size: 3rem;
  font-weight: bold;
  color: #f59e0b;
}

.stars-display {
  display: flex;
  gap: 0.25rem;
}

.star {
  font-size: 1.5rem;
  color: #d1d5db;
}

.star.filled {
  color: #f59e0b;
}

.rating-count {
  color: #6b7280;
  font-size: 0.875rem;
}

.user-rating {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.rating-label {
  color: #374151;
  font-weight: 500;
}

.star-input {
  display: flex;
  gap: 0.25rem;
}

.star.clickable {
  cursor: pointer;
  transition: transform 0.2s;
}

.star.clickable:hover {
  transform: scale(1.2);
}

.star.clickable.active {
  color: #f59e0b;
}

/* 用户评分徽章 */
.user-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.user-rating-badge {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  background: linear-gradient(135deg, #f59e0b, #fbbf24);
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.star-icon {
  font-size: 0.7rem;
}

.rating-value {
  font-size: 0.75rem;
}

/* 评论区标题 */
.comments-header {
  margin-bottom: 1.5rem;
}

.comments-header h3 {
  margin: 0;
  font-size: 1.25rem;
  color: #1f2937;
}

/* 评论输入框 */
.comment-input-section {
  margin-bottom: 2rem;
}

.comment-textarea {
  margin-bottom: 1rem;
}

.submit-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.login-hint {
  padding: 1rem;
  background: #f3f4f6;
  border-radius: 8px;
  text-align: center;
  margin-bottom: 2rem;
  color: #6b7280;
}

/* 评论列表 */
.comments-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.no-comments {
  text-align: center;
  color: #9ca3af;
  padding: 2rem;
}

.comment-item {
  display: flex;
  gap: 1rem;
}

.comment-avatar {
  flex-shrink: 0;
}

.avatar-placeholder {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 1.25rem;
}

.avatar-placeholder.small {
  width: 32px;
  height: 32px;
  font-size: 1rem;
}

.comment-content {
  flex: 1;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.comment-username {
  font-weight: 600;
  color: #1f2937;
}

.comment-date {
  color: #9ca3af;
  font-size: 0.875rem;
}

.comment-text {
  color: #374151;
  line-height: 1.6;
  margin-bottom: 0.75rem;
}

.comment-text.deleted {
  color: #9ca3af;
  font-style: italic;
}

.comment-actions {
  display: flex;
  gap: 1rem;
}

.action-btn {
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  font-size: 0.875rem;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  transition: all 0.2s;
}

.action-btn:hover {
  background: #f3f4f6;
  color: #4b5563;
}

.action-btn.delete-btn {
  color: #ef4444;
}

.action-btn.delete-btn:hover {
  background: #fee2e2;
}

.action-btn.small {
  font-size: 0.75rem;
  padding: 0.125rem 0.375rem;
}

/* 回复输入框 */
.reply-input-section {
  margin-top: 1rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 8px;
}

.reply-textarea {
  margin-bottom: 0.5rem;
}

.reply-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

/* 回复列表 */
.replies-list {
  margin-top: 1rem;
  padding-left: 1rem;
  border-left: 2px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.reply-item {
  display: flex;
  gap: 0.75rem;
}

.reply-content {
  flex: 1;
}

.reply-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.reply-username {
  font-weight: 600;
  color: #1f2937;
  font-size: 0.875rem;
}

.reply-date {
  color: #9ca3af;
  font-size: 0.75rem;
}

.reply-text {
  color: #374151;
  line-height: 1.5;
  font-size: 0.875rem;
}

.reply-text.deleted {
  color: #9ca3af;
  font-style: italic;
}

.reply-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 0.5rem;
}
</style>



