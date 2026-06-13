<template>
  <Transition name="mode" mode="out-in">
    <!-- Browse mode -->
    <div v-if="!isEditorOpen" key="browse" class="create-page">
      <div class="page-header">
        <div class="page-header-text">
          <h1>创作</h1>
          <p class="page-desc">写文章、管理内容，记录你的所思所想</p>
        </div>
        <div class="page-header-actions">
          <ArButton type="primary" size="lg" @click="handleNewPost">
            <template #icon>
              <NIcon size="18"><CreateOutline /></NIcon>
            </template>
            写文章
          </ArButton>
          <ArButton type="secondary" size="lg" @click="handleUploadFile">
            <template #icon>
              <NIcon size="18"><CloudUploadOutline /></NIcon>
            </template>
            上传文件
          </ArButton>
          <input
            ref="fileInputRef"
            type="file"
            accept=".txt,.md"
            style="display: none"
            @change="handleFileSelected"
          />
        </div>
      </div>

      <div class="stats-grid">
        <div v-for="card in statCards" :key="card.label" class="stat-card">
          <div class="stat-icon" :style="{ background: card.color + '14', color: card.color }">
            <NIcon :size="20"><component :is="card.icon" /></NIcon>
          </div>
          <div class="stat-body">
            <span class="stat-value">{{ card.value }}</span>
            <span class="stat-label">{{ card.label }}</span>
          </div>
        </div>
      </div>

      <div class="post-section">
        <div class="tab-bar">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            class="tab-btn"
            :class="{ active: activeTab === tab.key }"
            @click="activeTab = tab.key"
          >
            {{ tab.label }}
          </button>
          <span class="tab-count">{{ filteredPosts.length }}</span>
        </div>

        <div class="post-list">
          <div v-if="loading" class="empty-state">加载中…</div>
          <div v-else-if="filteredPosts.length === 0" class="empty-state">
            <p v-if="activeTab === 'all'">还没有文章，开始你的第一篇创作吧</p>
            <p v-else-if="activeTab === 'published'">还没有已发布的文章</p>
            <p v-else>草稿箱是空的</p>
          </div>
          <div v-else class="post-items">
            <div v-for="post in filteredPosts" :key="post.id" class="post-row">
              <div class="post-info" @click="handleOpenPost(post)">
                <span class="post-title">{{ post.title || '无标题' }}</span>
                <div class="post-meta">
                  <ArTag :color="getStatus(post).color" type="light" size="sm">
                    {{ getStatus(post).label }}
                  </ArTag>
                  <span class="post-date">{{ post.created_at?.slice(0, 10) || '—' }}</span>
                </div>
              </div>
              <div class="post-actions">
                <div
                  class="action-btn-wrap"
                  @mouseenter="hoveredPost = post"
                  @mouseleave="hoveredPost = null"
                >
                  <button
                    class="action-btn"
                    title="数据"
                    @click="handleViewStats(post)"
                    @mouseenter="hoveredPost = post"
                  >
                    <NIcon size="16"><EyeOutline /></NIcon>
                  </button>
                  <Transition name="tip">
                    <div
                      v-if="hoveredPost?.id === post.id && (!statsPost || statsPost.id !== post.id)"
                      class="stats-tip"
                      @mouseenter="hoveredPost = post"
                    >
                      <div class="tip-row">
                        <span class="tip-label">阅读</span>
                        <span class="tip-value">{{ post.views || 0 }}</span>
                      </div>
                      <div class="tip-row">
                        <span class="tip-label">点赞</span>
                        <span class="tip-value">{{ post.likes || 0 }}</span>
                      </div>
                    </div>
                  </Transition>
                </div>
                <button class="action-btn" title="编辑" @click="handleEditPost(post)">
                  <NIcon size="16"><CreateOutline /></NIcon>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <NModal
        :show="showStatsModal"
        :on-update:show="(val) => !val && handleCloseStats()"
        :mask-closable="true"
        preset="card"
        class="stats-modal"
        :style="{ maxWidth: '420px' }"
        :title="statsPost?.title || '文章数据'"
        :bordered="false"
        :segmented="false"
      >
        <div v-if="statsPost" class="stats-detail">
          <div class="stats-detail-row">
            <div class="stats-detail-item">
              <NIcon size="18" color="var(--text-tertiary)"><EyeOutline /></NIcon>
              <div class="stats-detail-body">
                <span class="stats-detail-value">{{ statsPost.views || 0 }}</span>
                <span class="stats-detail-label">阅读量</span>
              </div>
            </div>
            <div class="stats-detail-item">
              <NIcon size="18" color="var(--text-tertiary)"><HeartOutline /></NIcon>
              <div class="stats-detail-body">
                <span class="stats-detail-value">{{ statsPost.likes || 0 }}</span>
                <span class="stats-detail-label">点赞</span>
              </div>
            </div>
          </div>
          <div class="stats-detail-row">
            <div class="stats-detail-item">
              <NIcon size="18" color="var(--text-tertiary)"><BookmarkOutline /></NIcon>
              <div class="stats-detail-body">
                <span class="stats-detail-value">{{
                  Math.round((statsPost.likes || 0) * 0.65)
                }}</span>
                <span class="stats-detail-label">收藏</span>
              </div>
            </div>
            <div class="stats-detail-item">
              <NIcon size="18" color="var(--text-tertiary)"><TimeOutline /></NIcon>
              <div class="stats-detail-body">
                <span class="stats-detail-value">{{
                  statsPost.created_at?.slice(0, 10) || '—'
                }}</span>
                <span class="stats-detail-label">发布时间</span>
              </div>
            </div>
          </div>
        </div>
      </NModal>
    </div>

    <!-- Edit mode -->
    <div v-else key="edit" class="edit-layout">
      <aside class="edit-sidebar">
        <button class="sidebar-back" @click="exitEdit">← 返回</button>
        <div class="sidebar-items">
          <button
            v-for="p in filteredPosts"
            :key="p.id"
            class="sidebar-item"
            :class="{ active: !isCreatingNew && p.id === editingPost?.id }"
            @click="switchEditPost(p)"
          >
            <div class="sidebar-item-title">{{ p.title || '无标题' }}</div>
            <div class="sidebar-item-meta">
              <span class="sidebar-item-status" :class="p.status || 'draft'"></span>
              <span>{{ p.created_at?.slice(0, 10) || '' }}</span>
            </div>
          </button>
        </div>
      </aside>

      <main class="edit-main">
        <div class="edit-topbar">
          <div class="edit-topbar-left">
            <template v-if="isCreatingNew">
              <span class="topbar-label">新建文章</span>
            </template>
            <ArTag v-else :color="getStatus(editingPost!).color" type="light">
              {{ getStatus(editingPost!).label }}
            </ArTag>
            <ArWheelPicker
              :options="accessLevels.map(String)"
              :model-value="String(editorAccess)"
              @update:model-value="editorAccess = Number($event)"
              title="帖子可见权限：P0=仅管理员 · P5=所有人可见"
            />
          </div>
          <div class="edit-topbar-tags">
            <TransitionGroup name="tag-enter" tag="div" class="topbar-tag-list">
              <ArTag
                v-for="tag in editorTags"
                :key="tag"
                color="primary"
                type="light"
                closable
                @close="removeEditorTag(tag)"
              >
                {{ tag }}
              </ArTag>
            </TransitionGroup>
            <input
              v-model="tagInputValue"
              class="tag-input-inline"
              placeholder="标签"
              @keydown="handleTagKeydown"
            />
          </div>
          <div class="edit-topbar-actions">
            <ArButton type="ghost" @click="exitEdit">取消</ArButton>
            <ArButton type="primary" :loading="saving" :disabled="saving" @click="saveCurrent">
              {{ isCreatingNew ? '发布' : '保存' }}
            </ArButton>
          </div>
        </div>
        <div class="edit-body">
          <div class="edit-editor">
            <PostEditor
              ref="editorRef"
              :post="isCreatingNew ? null : editingPost"
              :cover-url="coverUrl"
              :loading="saving"
              hide-footer
              @cancel="exitEdit"
            />
          </div>
          <div class="sidebar-inner">
            <div class="sidebar-section">
              <h3 class="sidebar-section-title">封面</h3>
              <CoverUploader v-model:cover-url="coverUrl" @cover-file="handleCoverFile" />
            </div>
            <AssetSidebar
              :staged-files="stagedFiles"
              @insert="handleInsertRef"
              @upload="handleAssetUpload"
            />
          </div>
        </div>
      </main>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { NModal, NIcon, useMessage } from 'naive-ui'
import {
  CreateOutline,
  DocumentTextOutline,
  EyeOutline,
  HeartOutline,
  BookmarkOutline,
  TimeOutline,
  CloudUploadOutline
} from '@vicons/ionicons5'
import ArButton from '@/components/ui/ArButton.vue'
import ArTag from '@/components/ui/ArTag.vue'
import ArWheelPicker from '@/components/ui/ArWheelPicker.vue'
import PostEditor from '@/components/blog/PostEditor.vue'
import AssetSidebar from '@/components/blog/AssetSidebar.vue'
import CoverUploader from '@/components/blog/CoverUploader.vue'
import {
  getMyPostsApi,
  uploadPostFileApi,
  createPostApi,
  updatePostApi,
  type BlogPost,
  type CreatePostPayload
} from '@/services/api'
import { uploadOssFileApi } from '@/services/api/oss'
import { useLocalFiles } from '@/composables/useLocalFiles'
import { marked } from 'marked'
import { getCoverGradient } from '@/utils/cover'
import { generateTextCover } from '@/utils/generateTextCover'
import { parseHtmlToParagraphs } from '@/utils/paragraph'
import { computeIntroduction } from '@/composables/useAutoIntroduction'
import { ensurePostsCovers } from '@/composables/useCoverLazyGenerator'

type PostTab = 'all' | 'published' | 'draft'

const router = useRouter()
const message = useMessage()
const editorRef = ref<InstanceType<typeof PostEditor> | null>(null)
const fileInputRef = ref<HTMLInputElement | null>(null)
const loading = ref(false)
const saving = ref(false)
const posts = ref<BlogPost[]>([])
const activeTab = ref<PostTab>('all')
const isEditorOpen = ref(false)
const isCreatingNew = ref(false)
const editingPost = ref<BlogPost | null>(null)
const tagInputValue = ref('')
const editorTags = ref<string[]>([])
const accessLevels = [0, 1, 2, 3, 4, 5] as const
const editorAccess = ref<number>(5)

const coverUrl = ref('')
const coverFile = ref<File | null>(null) // 用户通过 CoverUploader 选择的本地文件
const { stagedFiles, stageFiles, getReferencedFiles, clearStaged } = useLocalFiles()
const pendingImport = ref<any>(null) // 文件导入后待填充到编辑器的数据
const statsPost = ref<BlogPost | null>(null)
const showStatsModal = ref(false)
const hoveredPost = ref<BlogPost | null>(null)

const statusMap: Record<string, { label: string; color: 'green' | 'yellow' | 'blue' | 'default' }> =
  {
    published: { label: '已发布', color: 'green' },
    pending: { label: '审核中', color: 'yellow' },
    draft: { label: '草稿', color: 'blue' }
  }

const getStatus = (post: BlogPost) => {
  const s = post.status || 'draft'
  return statusMap[s] || { label: s, color: 'default' as const }
}

const totalPosts = computed(() => posts.value.length)
const draftCount = computed(
  () => posts.value.filter((p) => (p.status || 'draft') === 'draft').length
)
const publishedCount = computed(() => posts.value.filter((p) => p.status === 'published').length)
const totalViews = computed(() => posts.value.reduce((sum, p) => sum + (p.views || 0), 0))

const statCards = computed(() => [
  {
    label: '全部文章',
    value: totalPosts.value,
    icon: DocumentTextOutline,
    color: 'var(--primary-color)'
  },
  { label: '已发布', value: publishedCount.value, icon: EyeOutline, color: 'var(--success-color)' },
  { label: '草稿', value: draftCount.value, icon: CreateOutline, color: 'var(--accent-yellow)' },
  { label: '总阅读', value: totalViews.value, icon: HeartOutline, color: 'var(--accent-color)' }
])

const filteredPosts = computed(() => {
  if (activeTab.value === 'all') return posts.value
  return posts.value.filter((p) => {
    if (activeTab.value === 'published') return p.status === 'published'
    return (p.status || 'draft') === 'draft'
  })
})

const tabs: { key: PostTab; label: string }[] = [
  { key: 'all', label: '全部' },
  { key: 'published', label: '已发布' },
  { key: 'draft', label: '草稿' }
]

// Browse actions
const handleNewPost = () => {
  isCreatingNew.value = true
  editingPost.value = null
  editorTags.value = []
  editorAccess.value = 5
  coverUrl.value = ''
  coverFile.value = null
  clearStaged()
  isEditorOpen.value = true
}

const handleUploadFile = () => {
  fileInputRef.value?.click()
}

const handleFileSelected = async (e: Event) => {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  try {
    const result = await uploadPostFileApi(file, { silent: true })
    isCreatingNew.value = true
    editingPost.value = null
    editorTags.value = (result as any)?.tags || []
    editorAccess.value = 5
    isEditorOpen.value = true
    // 存储导入数据，由 watch(editorRef) 在编辑器挂载后自动填充
    pendingImport.value = result
    message.success('文件导入成功')
  } catch {
    message.error('文件导入失败，请重试')
  } finally {
    input.value = ''
  }
}

// 编辑器挂载后填充导入的 MD 文件内容
watch(editorRef, (editor) => {
  if (editor && pendingImport.value) {
    const data = pendingImport.value as any
    editor.title = data.title || ''
    const rawContent = data.content || ''
    editor.content = rawContent ? (marked.parse(rawContent, { gfm: true }) as string) : ''
    if (data.cover_url) {
      coverUrl.value = data.cover_url
    } else {
      coverUrl.value = getCoverGradient({
        title: data.title,
        tags: data.tags
      })
    }
    pendingImport.value = null
  }
})

const handleOpenPost = (post: BlogPost) => router.push(`/blog/${post.slug}`)

const handleViewStats = (post: BlogPost) => {
  if (statsPost.value?.id === post.id) {
    handleCloseStats()
    return
  }
  statsPost.value = post
  showStatsModal.value = true
}

const handleCloseStats = () => {
  showStatsModal.value = false
  statsPost.value = null
}

// Edit actions
const handleEditPost = (post: BlogPost) => {
  isCreatingNew.value = false
  editingPost.value = post
  editorTags.value = [...(post.tags || [])]
  editorAccess.value = (post.required_level as number) ?? 5
  coverUrl.value = post.cover_url || ''
  isEditorOpen.value = true
}

const handleInsertRef = (refStr: string) => {
  if (editorRef.value) {
    editorRef.value.content += refStr
  }
}

const handleAssetUpload = (files: File[]) => {
  stageFiles(files)
}

const handleCoverFile = (file: File) => {
  coverFile.value = file
}

const exitEdit = () => {
  isEditorOpen.value = false
  isCreatingNew.value = false
  editingPost.value = null
  editorTags.value = []
  coverUrl.value = ''
  coverFile.value = null
  clearStaged()
}

const switchEditPost = (post: BlogPost) => {
  isCreatingNew.value = false
  editingPost.value = post
  editorTags.value = [...(post.tags || [])]
  editorAccess.value = (post.required_level as number) ?? 5
}

const saveCurrent = async () => {
  if (!editorRef.value) return
  const title = editorRef.value.title.trim()
  const content = editorRef.value.content.trim()
  if (!title || !content) return

  saving.value = true
  try {
    // 1. 上传所有被正文引用的暂存文件
    const refFiles = getReferencedFiles(content)
    const refMap = new Map<number, string>() // index → OSS URL
    for (const sf of refFiles) {
      const resp = await uploadOssFileApi(sf.file, false)
      const respData = resp as unknown as { data?: { id: string } }
      const fileId = respData?.data?.id
      if (fileId) {
        refMap.set(sf.index, `/api/oss/files/${fileId}`)
      }
    }

    // 2. 上传封面（如果是本地 blob）
    let finalCoverUrl = coverUrl.value
    if (coverFile.value && coverUrl.value.startsWith('blob:')) {
      const resp = await uploadOssFileApi(coverFile.value, false)
      const respData = resp as unknown as { data?: { id: string } }
      const fileId = respData?.data?.id
      if (fileId) {
        finalCoverUrl = `/api/oss/files/${fileId}`
      }
    }

    // 2.5 没有封面 → 自动生成文字封面并上传 OSS（后续直接引用，无需实时计算）
    let autoCoverUrl = ''
    if (!finalCoverUrl && title) {
      const textCoverDataUrl = generateTextCover(
        {
          id: '',
          slug: '',
          title,
          intro: editorRef.value?.intro || undefined,
          content,
          tags: editorTags.value
        } as BlogPost,
        true
      )
      const blob = await fetch(textCoverDataUrl).then((r) => r.blob())
      const file = new File([blob], 'text-cover.jpg', { type: 'image/jpeg' })
      const resp = await uploadOssFileApi(file, false)
      const respData = resp as unknown as { data?: { id: string } }
      if (respData?.data?.id) {
        autoCoverUrl = `/api/oss/files/${respData.data.id}`
      }
    }

    // 3. 替换正文中的 [#N] 为实际 OSS URL
    let finalContent = content
    for (const [index, ossUrl] of refMap) {
      finalContent = finalContent.replace(new RegExp(`\\[#${index}\\]`, 'g'), `![图片](${ossUrl})`)
    }

    // 4. 发送保存请求
    const isEdit = !!editingPost.value

    // 4.1 解析正文为结构化段落
    const paragraphs = parseHtmlToParagraphs(finalContent)

    // 4.2 引言为空时自动生成
    const editorIntro = editorRef.value?.intro.trim()
    const introduction = editorIntro
      ? { abstract: editorIntro }
      : (computeIntroduction(paragraphs) as Record<string, unknown>)

    const payload: CreatePostPayload = {
      title,
      content: finalContent,
      ...(paragraphs.length > 0 ? { paragraphs } : {}),
      ...(Object.keys(introduction).length > 0 ? { introduction } : {}),
      ...(finalCoverUrl ? { cover_url: finalCoverUrl } : {}),
      ...(autoCoverUrl ? { auto_cover_url: autoCoverUrl } : {}),
      tags: editorTags.value,
      required_level: editorAccess.value
    }

    if (isEdit) {
      await updatePostApi(editingPost.value!.id, payload)
      message.success('保存成功')
      await fetchData()
      // 编辑已有帖子：保存后保持编辑器打开，方便连续编辑下一篇
    } else {
      await createPostApi(payload)
      message.success('发布成功，帖子已提交审核')
      await fetchData()
      exitEdit()
    }
  } catch {
    message.error('保存失败，请重试')
  } finally {
    saving.value = false
  }
}

// ── Tag helpers ──
const addEditorTag = () => {
  const t = tagInputValue.value.trim()
  if (t && !editorTags.value.includes(t)) {
    editorTags.value.push(t)
  }
  tagInputValue.value = ''
}

const removeEditorTag = (tag: string) => {
  editorTags.value = editorTags.value.filter((t) => t !== tag)
}

const handleTagKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Enter' || e.key === ',') {
    e.preventDefault()
    addEditorTag()
  }
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getMyPostsApi(
      { page: 1, page_size: 50, sort_by: 'created_at' },
      { silent: true, skipAuthLogout: true }
    )
    posts.value = res.list || []
    // 对缺少封面的旧帖子按需生成文字封面并持久化
    ensurePostsCovers(posts.value)
  } catch {
    posts.value = []
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)
</script>

<style scoped>
.create-page {
  max-width: 100%;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--spacing-md);
}

.page-header-text h1 {
  margin: 0 0 4px;
  font-size: 26px;
  font-weight: var(--font-weight-bold);
}

.page-desc {
  margin: 0;
  font-size: 14px;
  color: var(--text-tertiary);
}

.page-header-actions {
  display: flex;
  gap: var(--spacing-sm);
  flex-shrink: 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: var(--spacing-lg);
}

.stat-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-body {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-value {
  font-size: 22px;
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
  line-height: 1;
}

.stat-label {
  font-size: 12px;
  color: var(--text-tertiary);
}

.post-section {
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.tab-bar {
  display: flex;
  align-items: center;
  gap: 2px;
  padding: var(--spacing-md) var(--spacing-lg);
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-inset-color);
}

.tab-btn {
  border: 0;
  background: transparent;
  color: var(--text-tertiary);
  font-size: 13px;
  font-family: var(--font-sans);
  padding: 5px 14px;
  border-radius: var(--radius-full);
  cursor: pointer;
  transition: all var(--transition-fast);
  font-weight: var(--font-weight-medium);
}

.tab-btn:hover {
  color: var(--text-primary);
  background: var(--surface-strong-color);
}

.tab-btn.active {
  color: var(--primary-color);
  background: var(--primary-light-color);
}

.tab-count {
  margin-left: auto;
  font-size: 12px;
  color: var(--text-tertiary);
}

.post-items {
  padding: 0;
}

.post-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: var(--spacing-md) var(--spacing-lg);
  border-bottom: 1px solid var(--divider-color);
  transition: background var(--transition-fast);
}

.post-row:last-child {
  border-bottom: none;
}

.post-row:hover {
  background: var(--surface-strong-color);
}

.post-info {
  flex: 1;
  min-width: 0;
  cursor: pointer;
}

.post-title {
  display: block;
  font-size: 15px;
  font-weight: var(--font-weight-medium);
  color: var(--text-primary);
  line-height: 1.4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.post-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
}

.post-date {
  font-size: 12px;
  color: var(--text-tertiary);
}

.post-actions {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}

.action-btn-wrap {
  position: relative;
}

.action-btn {
  width: 32px;
  height: 32px;
  border: 0;
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--text-tertiary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}

.action-btn:hover {
  background: var(--surface-hover-color);
  color: var(--text-primary);
}

.stats-tip {
  position: absolute;
  bottom: calc(100% + 6px);
  right: 0;
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  padding: 8px 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  white-space: nowrap;
  z-index: 50;
  min-width: 100px;
}

.tip-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  font-size: 12px;
}

.tip-label {
  color: var(--text-tertiary);
}

.tip-value {
  color: var(--text-primary);
  font-weight: var(--font-weight-semibold);
  font-variant-numeric: tabular-nums;
}

.tip-enter-active,
.tip-leave-active {
  transition: all 0.15s ease;
}

.tip-enter-from,
.tip-leave-to {
  opacity: 0;
  transform: translateY(4px);
}

.empty-state {
  text-align: center;
  padding: 48px 0;
  color: var(--text-tertiary);
  font-size: 14px;
}

.empty-state p {
  margin: 0;
}

.stats-modal :deep(.n-card-header) {
  padding: var(--spacing-lg) var(--spacing-lg) 0;
}

.stats-modal :deep(.n-card-header__title) {
  font-size: 16px;
}

.stats-modal :deep(.n-card__content) {
  padding: var(--spacing-lg);
}

.stats-detail {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.stats-detail-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-md);
}

.stats-detail-item {
  display: flex;
  align-items: center;
  gap: 10px;
  background: var(--bg-inset-color);
  border-radius: var(--radius-md);
  padding: 12px;
}

.stats-detail-body {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.stats-detail-value {
  font-size: 16px;
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
  line-height: 1;
}

.stats-detail-label {
  font-size: 11px;
  color: var(--text-tertiary);
}

/* Edit mode */
.mode-enter-active,
.mode-leave-active {
  transition: all 0.22s ease;
}

.mode-enter-from {
  opacity: 0;
  transform: translateY(6px);
}

.mode-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

.topbar-label {
  font-size: 14px;
  font-weight: var(--font-weight-medium);
  color: var(--text-primary);
}

.edit-layout {
  display: flex;
  gap: 0;
  height: calc(100vh - 56px - var(--content-padding) * 2);
  margin: calc(-1 * var(--content-padding));
  background: var(--surface-color);
  overflow: hidden;
}

/* ── 隐藏滚动条（全局统一后面单独做，先隐藏） ── */
.edit-body,
.edit-editor,
.sidebar-inner,
.sidebar-items {
  scrollbar-width: none;
}
.edit-body::-webkit-scrollbar,
.edit-editor::-webkit-scrollbar,
.sidebar-inner::-webkit-scrollbar,
.sidebar-items::-webkit-scrollbar {
  display: none;
}

.edit-sidebar {
  width: 220px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--border-color);
  background: var(--surface-inset-color);
}

.sidebar-back {
  border: 0;
  border-bottom: 1px solid var(--border-color);
  background: transparent;
  padding: 14px 16px;
  font-size: 14px;
  font-family: var(--font-sans);
  color: var(--text-primary);
  cursor: pointer;
  text-align: left;
  font-weight: var(--font-weight-medium);
  transition: background var(--transition-fast);
  flex-shrink: 0;
}

.sidebar-back:hover {
  background: var(--surface-strong-color);
}

.sidebar-items {
  flex: 1;
  overflow-y: auto;
  padding: 4px 0;
}

.sidebar-item {
  display: block;
  width: 100%;
  border: 0;
  border-left: 3px solid transparent;
  background: transparent;
  padding: 12px 16px;
  text-align: left;
  cursor: pointer;
  transition: all var(--transition-fast);
  font-family: var(--font-sans);
}

.sidebar-item:hover {
  background: var(--surface-hover-color);
  border-left-color: var(--border-color);
}

.sidebar-item.active {
  background: var(--primary-light-color);
  border-left-color: var(--primary-color);
}

.sidebar-item-title {
  font-size: 14px;
  color: var(--text-primary);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
  font-weight: var(--font-weight-medium);
}

.sidebar-item.active .sidebar-item-title {
  color: var(--primary-color);
}

.sidebar-item-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 4px;
  font-size: 12px;
  color: var(--text-tertiary);
}

.sidebar-item-status {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.sidebar-item-status.published {
  background: var(--success-color);
}

.sidebar-item-status.draft {
  background: var(--accent-yellow);
}

.sidebar-item-status.pending {
  background: var(--accent-orange, #e8a817);
}

.edit-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.edit-topbar {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 10px 20px;
  border-bottom: 1px solid var(--border-color);
  background: var(--surface-color);
  flex-shrink: 0;
  flex-wrap: wrap;
}

.edit-topbar-left {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.edit-topbar-tags {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 140px;
}

.topbar-tag-list {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.tag-input-inline {
  border: none;
  border-bottom: 1px solid var(--border-color);
  outline: none;
  background: transparent;
  color: var(--text-primary);
  font-family: var(--font-sans);
  font-size: 13px;
  padding: 4px 0;
  min-width: 70px;
  flex: 1;
  transition: border-color var(--transition-fast);
}

.tag-input-inline:focus {
  border-bottom-color: var(--primary-color);
}

.tag-input-inline::placeholder {
  color: var(--text-tertiary);
}

.tag-enter-enter-active {
  transition: all 0.25s var(--ease-out-smooth);
}
.tag-enter-leave-active {
  transition: all 0.2s ease-in;
}
.tag-enter-enter-from {
  opacity: 0;
  transform: scale(0.7);
}
.tag-enter-leave-to {
  opacity: 0;
  transform: scale(0.7);
}

.edit-topbar-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.edit-editor {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-lg);
}

.edit-body {
  display: flex;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.sidebar-inner {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
  height: 100%;
  overflow-y: auto;
}

.sidebar-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.sidebar-section-title {
  margin: 0;
  font-size: 14px;
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .page-header {
    flex-direction: column;
  }

  .edit-sidebar {
    width: 160px;
  }
}
</style>
