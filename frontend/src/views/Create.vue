<template>
  <div class="create-page">
    <!-- 统一工具栏 -->
    <div class="editor-toolbar">
      <div class="toolbar-left">
        <button class="toolbar-back" @click="handleBack">
          <svg
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <polyline points="15 18 9 12 15 6" />
          </svg>
          返回
        </button>
      </div>

      <div class="toolbar-divider" />

      <!-- 富文本格式工具 -->
      <div class="toolbar-format">
        <button class="fmt-btn" title="加粗" @click="execFormat('bold')">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <path
              d="M15.6 10.79c.97-.67 1.65-1.77 1.65-2.79 0-2.26-1.75-4-4-4H7v14h7.04c2.09 0 3.71-1.7 3.71-3.79 0-1.52-.86-2.82-2.15-3.42zM10 6.5h3c.83 0 1.5.67 1.5 1.5s-.67 1.5-1.5 1.5h-3v-3zm3.5 9H10v-3h3.5c.83 0 1.5.67 1.5 1.5s-.67 1.5-1.5 1.5z"
            />
          </svg>
        </button>
        <button class="fmt-btn" title="斜体" @click="execFormat('italic')">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <path d="M10 4v3h2.21l-3.42 8H6v3h8v-3h-2.21l3.42-8H18V4z" />
          </svg>
        </button>
        <button class="fmt-btn" title="下划线" @click="execFormat('underline')">
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <path d="M6 3v7a6 6 0 0 0 6 6 6 6 0 0 0 6-6V3" />
            <line x1="4" y1="21" x2="20" y2="21" />
          </svg>
        </button>
        <span class="fmt-divider" />
        <button class="fmt-btn" title="二级标题" @click="execFormat('formatBlock', 'h2')">
          <span class="fmt-text">H2</span>
        </button>
        <button class="fmt-btn" title="三级标题" @click="execFormat('formatBlock', 'h3')">
          <span class="fmt-text">H3</span>
        </button>
        <button class="fmt-btn" title="正文" @click="execFormat('formatBlock', 'p')">
          <span class="fmt-text fmt-text--sm">P</span>
        </button>
        <span class="fmt-divider" />
        <button class="fmt-btn" title="引用" @click="execFormat('formatBlock', 'blockquote')">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <path d="M6 17h3l2-4V7H5v6h3zm8 0h3l2-4V7h-6v6h3z" />
          </svg>
        </button>
        <button class="fmt-btn" title="代码" @click="insertCodeFormat">
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <polyline points="16 18 22 12 16 6" />
            <polyline points="8 6 2 12 8 18" />
          </svg>
        </button>
      </div>

      <div class="toolbar-divider" />

      <!-- 元信息与操作 -->
      <div class="toolbar-meta">
        <button class="meta-btn" title="封面" @click="triggerCoverInput">
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <rect x="3" y="3" width="18" height="18" rx="2" />
            <circle cx="8.5" cy="8.5" r="1.5" />
            <polyline points="21 15 16 10 5 21" />
          </svg>
          <span class="meta-btn-label">封面</span>
        </button>
        <button class="meta-btn" title="标签" @click="showTagPopover = !showTagPopover">
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <path
              d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"
            />
            <line x1="7" y1="7" x2="7.01" y2="7" />
          </svg>
          <span class="meta-btn-label">标签</span>
        </button>
        <button class="meta-btn" title="权限" @click="showAccessPopover = !showAccessPopover">
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
            <path d="M7 11V7a5 5 0 0 1 10 0v4" />
          </svg>
          <span class="meta-btn-label">P{{ editorAccess }}</span>
        </button>
        <button class="meta-btn" title="素材库" @click="showAssetsModal = true">
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <rect x="3" y="3" width="18" height="18" rx="2" />
            <circle cx="8.5" cy="8.5" r="1.5" />
            <polyline points="21 15 16 10 5 21" />
          </svg>
          <span class="meta-btn-label">素材</span>
        </button>
      </div>

      <div class="toolbar-spacer" />

      <div class="toolbar-actions">
        <ArButton type="ghost" size="sm" :loading="saving" @click="saveDraft">存草稿</ArButton>
        <ArButton type="primary" size="sm" :loading="saving" :disabled="saving" @click="handleSave"
          >发布</ArButton
        >
      </div>

      <input
        ref="coverInputRef"
        type="file"
        accept="image/*"
        style="display: none"
        @change="handleCoverFileSelected"
      />
    </div>

    <!-- 标签弹出 -->
    <Transition name="popover">
      <div v-if="showTagPopover" class="toolbar-popover" @click.stop>
        <div class="popover-header">标签</div>
        <div class="popover-tags">
          <ArTag
            v-for="tag in editorTags"
            :key="tag"
            color="primary"
            type="light"
            size="sm"
            closable
            @close="removeEditorTag(tag)"
          >
            {{ tag }}
          </ArTag>
        </div>
        <div class="popover-tag-input-wrap">
          <input
            v-model="tagInputValue"
            class="popover-tag-input"
            placeholder="输入标签，回车添加"
            maxlength="4"
            @keydown="handleTagKeydown"
            @focus="showTagSuggestions = true"
            @blur="handleTagInputBlur"
          />
          <Transition name="tag-suggest">
            <div
              v-if="showTagSuggestions && tagSuggestions.length > 0"
              class="popover-tag-suggestions"
            >
              <button
                v-for="s in tagSuggestions"
                :key="s.name"
                class="tag-suggestion-item"
                @mousedown.prevent="selectTagSuggestion(s.name)"
              >
                <span class="suggestion-name">{{ s.name }}</span>
                <span v-if="s.count != null" class="suggestion-count">{{ s.count }}</span>
              </button>
            </div>
          </Transition>
        </div>
      </div>
    </Transition>

    <!-- 权限弹出 -->
    <Transition name="popover">
      <div v-if="showAccessPopover" class="toolbar-popover access-popover" @click.stop>
        <div class="popover-header">访问权限</div>
        <div class="popover-access-options">
          <button
            v-for="level in accessLevels"
            :key="level"
            class="access-option"
            :class="{ 'access-option--active': editorAccess === level }"
            @click="handleAccessSelect(level)"
          >
            <span class="access-level">P{{ level }}</span>
            <span class="access-desc">{{ accessDescriptions[level] }}</span>
          </button>
        </div>
      </div>
    </Transition>

    <!-- 正文区 -->
    <div class="editor-body">
      <div class="editor-paper">
        <!-- 标题区 -->
        <div class="title-section">
          <label class="title-label">标题</label>
          <input
            v-model="postTitle"
            class="title-input"
            placeholder="输入文章标题…"
            maxlength="256"
          />
        </div>

        <!-- 副标题区 -->
        <div class="subtitle-section">
          <div v-for="(sub, idx) in subtitles" :key="idx" class="subtitle-row">
            <label class="subtitle-label">副标题</label>
            <input
              v-model="sub.value"
              class="subtitle-input"
              placeholder="输入副标题…"
              maxlength="200"
              @input="onSubtitlesChange"
            />
            <button class="subtitle-remove" @click="removeSubtitle(idx)">
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>
          <button class="subtitle-add" @click="addSubtitle">
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <line x1="12" y1="5" x2="12" y2="19" />
              <line x1="5" y1="12" x2="19" y2="12" />
            </svg>
            添加副标题
          </button>
        </div>

        <!-- 引言 K:V 区 -->
        <IntroKeyValueEditor v-model="introItems" />

        <!-- 卡片列表 -->
        <div class="card-list">
          <template v-for="(card, index) in cards" :key="card.id">
            <ParagraphCard
              :card="card"
              :index="index"
              @update="handleCardUpdate"
              @move="handleCardMove"
              @insert="handleCardInsert"
              @delete="handleCardDelete"
            />
            <div class="insert-zone">
              <button class="insert-btn" @click="openInsertModal(index + 1)">
                <svg
                  width="12"
                  height="12"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <line x1="12" y1="5" x2="12" y2="19" />
                  <line x1="5" y1="12" x2="19" y2="12" />
                </svg>
                插入卡片
              </button>
            </div>
          </template>

          <div v-if="cards.length === 0" class="card-list-empty">
            <p>还没有段落卡片</p>
            <p class="card-list-empty-hint">点击上方按钮添加卡片，或上传 Markdown 文件自动拆分</p>
          </div>
        </div>

        <!-- 底部统计 -->
        <div v-if="cards.length > 0" class="editor-footer">
          <span class="footer-info">共 {{ cards.length }} 个段落</span>
          <span class="footer-info">约 {{ estimatedWords }} 字</span>
          <span class="footer-info">预计阅读 {{ readingTime }} 分钟</span>
        </div>
      </div>
    </div>

    <!-- 图片入口行（封面/MD） -->
    <div class="editor-file-actions">
      <ArButton type="secondary" size="sm" @click="handleUploadFile">
        <template #icon>
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="17 8 12 3 7 8" />
            <line x1="12" y1="3" x2="12" y2="15" />
          </svg>
        </template>
        上传 MD 文件
      </ArButton>
      <ArButton type="ghost" size="sm" @click="addBlankCard">
        <template #icon>
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
        </template>
        添加空白卡片
      </ArButton>
      <input
        ref="fileInputRef"
        type="file"
        accept=".txt,.md"
        style="display: none"
        @change="handleFileSelected"
      />
    </div>

    <!-- 卡片插入弹窗 -->
    <CardInsertModal
      :visible="showInsertModal"
      @select="onCardTypeSelected"
      @close="showInsertModal = false"
    />

    <!-- 素材弹窗 -->
    <NModal
      :show="showAssetsModal"
      @update:show="showAssetsModal = $event"
      :mask-closable="true"
      preset="card"
      title="素材库"
      class="assets-modal"
      :style="{ maxWidth: '600px' }"
      :bordered="false"
    >
      <AssetSidebar
        :staged-files="stagedFiles"
        @insert="handleAssetInsert"
        @upload="handleAssetUpload"
      />
    </NModal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage, NModal } from 'naive-ui'
import ArButton from '@/components/ui/ArButton.vue'
import ArTag from '@/components/ui/ArTag.vue'
import AssetSidebar from '@/components/blog/AssetSidebar.vue'
import CardInsertModal from '@/components/blog/CardInsertModal.vue'
import IntroKeyValueEditor from '@/components/blog/IntroKeyValueEditor.vue'
import type { IntroItem } from '@/components/blog/IntroKeyValueEditor.vue'
import ParagraphCard from '@/components/blog/paragraph-editor/ParagraphCard.vue'
import {
  createPostApi,
  getBlogTagsApi,
  uploadPostFileApi,
  type CreatePostPayload,
  type BlogTag
} from '@/services/api'
import { uploadOssFileApi } from '@/services/api/oss'
import { useLocalFiles } from '@/composables/useLocalFiles'
import { compressImage } from '@/utils/imageCompress'
import { parseMdToCards, type CardData, type CardType } from '@/utils/paragraph'
import { generateTextCover } from '@/utils/generateTextCover'
import { getCoverGradient } from '@/utils/cover'

const router = useRouter()
const message = useMessage()

// ── 状态 ──

const fileInputRef = ref<HTMLInputElement | null>(null)
const coverInputRef = ref<HTMLInputElement | null>(null)
const saving = ref(false)
const postTitle = ref('')
const cards = ref<CardData[]>([])
const tagInputValue = ref('')
const editorTags = ref<string[]>([])
const tagSuggestions = ref<{ name: string; count?: number }[]>([])
const showTagSuggestions = ref(false)
const showTagPopover = ref(false)
const showAccessPopover = ref(false)
const accessLevels = [0, 1, 2, 3, 4, 5] as const
const editorAccess = ref<number>(5)
const showAssetsModal = ref(false)
const coverUrl = ref('')
const coverFile = ref<File | null>(null)
const showInsertModal = ref(false)
const insertAfterIndex = ref<number>(0)

// 副标题
const subtitles = ref<{ value: string }[]>([])

// 引言 K:V
const introItems = ref<IntroItem[]>([])

const { stagedFiles, stageFiles, clearStaged } = useLocalFiles()

const accessDescriptions: Record<number, string> = {
  0: '仅管理员',
  1: 'P1 级',
  2: 'P2 级',
  3: 'P3 级',
  4: 'P4 级',
  5: '所有人可见'
}

const estimatedWords = computed(() => {
  let total = 0
  for (const card of cards.value) {
    const div = document.createElement('div')
    div.innerHTML = card.content
    const text = div.textContent || ''
    const cn = (text.match(/[\u4e00-\u9fff]/g) || []).length
    const en = (text.match(/[a-zA-Z]+/g) || []).length
    total += cn + en
  }
  return total
})

const readingTime = computed(() => Math.max(1, Math.round(estimatedWords.value / 300)))

// ── 富文本格式 ──

function execFormat(command: string, value?: string) {
  document.execCommand(command, false, value)
  // 确保编辑器获得焦点
  const active = document.activeElement as HTMLElement
  if (active && active.contentEditable === 'true') {
    active.dispatchEvent(new Event('input', { bubbles: true }))
  }
}

function insertCodeFormat() {
  // 检查当前选区是否在 contenteditable 内
  const sel = window.getSelection()
  if (!sel || !sel.rangeCount) return
  const node = sel.anchorNode?.parentElement
  if (!node?.closest('[contenteditable]')) return

  document.execCommand('formatBlock', false, 'pre')
  const active = document.activeElement as HTMLElement
  if (active && active.contentEditable === 'true') {
    active.dispatchEvent(new Event('input', { bubbles: true }))
  }
}

// ── 文件上传 ──

function handleUploadFile() {
  fileInputRef.value?.click()
}

async function handleFileSelected(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  try {
    const result = await uploadPostFileApi(file, { silent: true })
    const data = result as any
    if (data.title) postTitle.value = data.title
    if (data.tags) editorTags.value = data.tags
    if (data.cover_url) {
      coverUrl.value = data.cover_url
    } else if (data.title) {
      coverUrl.value = getCoverGradient({ title: data.title, tags: data.tags })
    }
    if (data.content) {
      cards.value = parseMdToCards(data.content)
    }
    message.success('文件导入成功')
  } catch {
    message.error('文件导入失败，请重试')
  } finally {
    input.value = ''
  }
}

// ── 卡片操作 ──

function addBlankCard() {
  const newCard: CardData = {
    id: `card_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
    type: 'text',
    content: ''
  }
  cards.value.push(newCard)
}

function handleCardUpdate(index: number, data: Partial<CardData>) {
  const card = cards.value[index]
  if (card) {
    Object.assign(card, data)
  }
}

function handleCardMove(from: number, to: number) {
  if (to < 0 || to >= cards.value.length) return
  const arr = cards.value
  const temp = arr[from]!
  arr[from] = arr[to]!
  arr[to] = temp
  cards.value = [...arr]
}

function handleCardInsert(afterIndex: number) {
  insertAfterIndex.value = afterIndex
  showInsertModal.value = true
}

function openInsertModal(afterIndex: number) {
  insertAfterIndex.value = afterIndex
  showInsertModal.value = true
}

function onCardTypeSelected(type: CardType) {
  showInsertModal.value = false
  const newCard: CardData = {
    id: `card_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
    type,
    content: ''
  }
  cards.value.splice(insertAfterIndex.value, 0, newCard)
  cards.value = [...cards.value]
}

function handleCardDelete(index: number) {
  cards.value.splice(index, 1)
  cards.value = [...cards.value]
}

// ── 副标题 ──

function addSubtitle() {
  subtitles.value.push({ value: '' })
}

function removeSubtitle(index: number) {
  subtitles.value.splice(index, 1)
}

function onSubtitlesChange() {
  // 触发响应式
  subtitles.value = [...subtitles.value]
}

// ── 封面 ──

function triggerCoverInput() {
  coverInputRef.value?.click()
}

function handleCoverFileSelected(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  coverFile.value = file
  coverUrl.value = URL.createObjectURL(file)
  input.value = ''
}

// ── 素材 ──

function handleAssetInsert(refStr: string) {
  cards.value.push({
    id: `card_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
    type: 'image',
    content: refStr
  })
}

function handleAssetUpload(files: File[]) {
  stageFiles(files)
}

// ── 标签 ──

function addEditorTag() {
  const t = tagInputValue.value.trim()
  if (t && !editorTags.value.includes(t)) {
    editorTags.value.push(t)
  }
  tagInputValue.value = ''
}

function removeEditorTag(tag: string) {
  editorTags.value = editorTags.value.filter((t) => t !== tag)
}

function handleTagKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' || e.key === ',') {
    e.preventDefault()
    addEditorTag()
    showTagSuggestions.value = false
  }
  if (e.key === 'Escape') {
    showTagSuggestions.value = false
  }
}

let tagSearchTimer: ReturnType<typeof setTimeout> | null = null
watch(tagInputValue, (val) => {
  if (tagSearchTimer) clearTimeout(tagSearchTimer)
  if (!val.trim()) {
    tagSuggestions.value = []
    showTagSuggestions.value = false
    return
  }
  tagSearchTimer = setTimeout(async () => {
    try {
      const res = await getBlogTagsApi({ page: 1, page_size: 10 } as any, { silent: true })
      const list = (res.list || []) as BlogTag[]
      tagSuggestions.value = list
        .filter((t) => t.name && !editorTags.value.includes(t.name) && t.name.includes(val.trim()))
        .map((t) => ({ name: t.name!, ...(t.count != null ? { count: t.count } : {}) }))
      showTagSuggestions.value = tagSuggestions.value.length > 0
    } catch {
      tagSuggestions.value = []
      showTagSuggestions.value = false
    }
  }, 200)
})

function selectTagSuggestion(name: string) {
  tagInputValue.value = name
  addEditorTag()
  showTagSuggestions.value = false
}

function handleTagInputBlur() {
  setTimeout(() => (showTagSuggestions.value = false), 150)
}

function handleAccessSelect(level: number) {
  editorAccess.value = level
  showAccessPopover.value = false
}

// ── 保存 ──

function cardsToPayload(): CreatePostPayload {
  const payload: CreatePostPayload = {
    title: postTitle.value.trim(),
    tags: editorTags.value,
    required_level: editorAccess.value
  }

  if (coverUrl.value) {
    payload.cover_url = coverUrl.value
  }

  // 构建引言 K:V
  const validItems = introItems.value.filter((item) => item.value.trim())
  if (validItems.length > 0) {
    payload.introduction = { items: validItems }
  }

  // 添加副标题
  const validSubtitles = subtitles.value.map((s) => s.value.trim()).filter(Boolean)
  if (validSubtitles.length > 0) {
    payload.introduction = {
      ...((payload.introduction as Record<string, unknown>) || {}),
      subtitles: validSubtitles
    }
  }

  // 从卡片中提取数据
  const paragraphs: NonNullable<CreatePostPayload['paragraphs']> = []

  for (const card of cards.value) {
    if (!card.content.trim()) continue

    const pType = card.type === 'quote' ? 'quote' : card.type
    const item: { content: string; type: string; heading?: string; media_url?: string } = {
      content: card.content,
      type: pType
    }
    if (card.media_url) {
      item.media_url = card.media_url
    }
    paragraphs.push(item)
  }

  if (paragraphs.length > 0) {
    payload.paragraphs = paragraphs
  }

  return payload
}

async function handleSave() {
  const title = postTitle.value.trim()
  if (!title) {
    message.warning('请输入文章标题')
    return
  }

  saving.value = true
  try {
    // 1. 上传封面
    let finalCoverUrl = coverUrl.value
    if (coverFile.value && coverUrl.value.startsWith('blob:')) {
      const compressed = await compressImage(coverFile.value)
      const resp = await uploadOssFileApi(compressed, false)
      const respData = resp as unknown as { data?: { id: string } }
      if (respData?.data?.id) {
        finalCoverUrl = `/api/oss/files/${respData.data.id}`
      }
    }

    // 2. 自动生成文字封面
    let autoCoverUrl = ''
    if (!finalCoverUrl && title) {
      const textCoverDataUrl = generateTextCover(
        { id: '', slug: '', title, tags: editorTags.value } as any,
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

    // 3. 构建 payload
    const payload = cardsToPayload()
    const cover = finalCoverUrl || autoCoverUrl
    if (cover) {
      payload.cover_url = cover
    }

    // 4. 发送
    await createPostApi(payload)
    message.success('发布成功，帖子已提交审核')
    clearStaged()
    router.push('/posts')
  } catch {
    message.error('保存失败，请重试')
  } finally {
    saving.value = false
  }
}

async function saveDraft() {
  const title = postTitle.value.trim()
  if (!title) {
    message.warning('请输入文章标题')
    return
  }

  saving.value = true
  try {
    const payload = cardsToPayload()
    if (coverUrl.value) {
      payload.cover_url = coverUrl.value
    }
    await createPostApi(payload)
    message.success('草稿已保存')
    clearStaged()
    router.push('/posts')
  } catch {
    message.error('保存草稿失败')
  } finally {
    saving.value = false
  }
}

function handleBack() {
  if (cards.value.length > 0 || postTitle.value.trim()) {
    if (!window.confirm('有未保存的内容，确定退出吗？')) return
  }
  router.push('/posts')
}
</script>

<style scoped>
.create-page {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--editor-side-bg, #f0f0f0);
  position: relative;
}

/* ── 统一工具栏 ── */

.editor-toolbar {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: var(--surface-color, #fff);
  border-bottom: 1px solid var(--border-color, #e8e6e4);
  flex-shrink: 0;
  z-index: 100;
  position: relative;
}

.toolbar-left {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.toolbar-back {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  border: none;
  background: transparent;
  color: var(--text-secondary, #666);
  font-size: 14px;
  cursor: pointer;
  padding: 6px 10px;
  border-radius: 6px;
  transition: all 0.15s;
}

.toolbar-back:hover {
  background: var(--hover-bg, #f5f5f5);
  color: var(--text-color, #333);
}

.toolbar-divider {
  width: 1px;
  height: 24px;
  background: var(--border-color, #e8e6e4);
  flex-shrink: 0;
}

.toolbar-format {
  display: flex;
  align-items: center;
  gap: 2px;
  flex-shrink: 0;
}

.fmt-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: var(--text-secondary, #666);
  cursor: pointer;
  transition: all 0.15s;
}

.fmt-btn:hover {
  background: var(--hover-bg, #f0f0f0);
  color: var(--text-color, #333);
}

.fmt-text {
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.fmt-text--sm {
  font-size: 0.65rem;
}

.fmt-divider {
  width: 1px;
  height: 16px;
  background: var(--border-color, #e8e6e4);
  margin: 0 4px;
  flex-shrink: 0;
}

.toolbar-meta {
  display: flex;
  align-items: center;
  gap: 2px;
  flex-shrink: 0;
}

.meta-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: var(--text-secondary, #666);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.15s;
}

.meta-btn:hover {
  background: var(--hover-bg, #f0f0f0);
  color: var(--text-color, #333);
}

.meta-btn-label {
  font-size: 12px;
}

.toolbar-spacer {
  flex: 1;
}

.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

/* ── 标签弹出 ── */

.toolbar-popover {
  position: absolute;
  top: calc(100% + 4px);
  right: 16px;
  background: var(--surface-color, #fff);
  border: 1px solid var(--border-color, #e8e6e4);
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  padding: 12px;
  z-index: 200;
  min-width: 240px;
}

.popover-header {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-tertiary, #999);
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.popover-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: 8px;
}

.popover-tag-input-wrap {
  position: relative;
}

.popover-tag-input {
  width: 100%;
  padding: 6px 10px;
  border: 1px solid var(--border-color, #e8e6e4);
  border-radius: 6px;
  font-size: 13px;
  outline: none;
  background: var(--bg-color, #fff);
  color: var(--text-color, #333);
  box-sizing: border-box;
}

.popover-tag-input:focus {
  border-color: var(--primary-color, #b83a2a);
}

.popover-tag-suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  z-index: 20;
  margin-top: 4px;
  background: var(--surface-color, #fff);
  border: 1px solid var(--border-color, #e8e6e4);
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  max-height: 140px;
  overflow-y: auto;
}

.tag-suggestion-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 8px 12px;
  border: none;
  background: transparent;
  color: var(--text-color, #333);
  font-size: 13px;
  cursor: pointer;
  transition: background 0.1s;
}

.tag-suggestion-item:hover {
  background: var(--hover-bg, #f5f5f5);
}

.suggestion-count {
  font-size: 11px;
  color: var(--text-muted, #aaa);
}

/* ── 权限弹出 ── */

.access-popover {
  min-width: 180px;
}

.popover-access-options {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.access-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border: none;
  border-radius: 6px;
  background: transparent;
  cursor: pointer;
  transition: background 0.1s;
}

.access-option:hover {
  background: var(--hover-bg, #f5f5f5);
}

.access-option--active {
  background: var(--primary-light-bg, var(--primary-light-color, rgba(184, 58, 42, 0.08)));
}

.access-level {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-color, #333);
  min-width: 24px;
}

.access-desc {
  font-size: 12px;
  color: var(--text-tertiary, #999);
}

/* ── 弹出过渡 ── */

.popover-enter-active,
.popover-leave-active {
  transition:
    opacity 0.15s,
    transform 0.15s;
}
.popover-enter-from,
.popover-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

/* ── 正文区 ── */

.editor-body {
  flex: 1;
  overflow-y: auto;
  display: flex;
  justify-content: center;
  padding: 32px 16px;
  scrollbar-width: none;
}

.editor-body::-webkit-scrollbar {
  display: none;
}

.editor-paper {
  width: 100%;
  max-width: 720px;
  background: var(--paper-bg, #fff);
  border-radius: 12px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
  padding: 32px;
  align-self: flex-start;
}

/* ── 标题区 ── */

.title-section {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 2px solid var(--border-color, #e8e6e4);
}

.title-label {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--text-color, #333);
  white-space: nowrap;
}

.title-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--text-color, #333);
  background: transparent;
  padding: 4px 0;
}

.title-input::placeholder {
  color: var(--placeholder-color, #bbb);
}

/* ── 副标题区 ── */

.subtitle-section {
  margin-bottom: 16px;
}

.subtitle-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 6px;
}

.subtitle-label {
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--text-secondary, #666);
  white-space: nowrap;
}

.subtitle-input {
  flex: 1;
  border: none;
  border-bottom: 1px dashed var(--border-color, #ddd);
  outline: none;
  font-size: 0.9375rem;
  color: var(--text-color, #333);
  background: transparent;
  padding: 4px 0;
}

.subtitle-input:focus {
  border-bottom-color: var(--primary-color, #b83a2a);
}

.subtitle-input::placeholder {
  color: var(--placeholder-color, #bbb);
}

.subtitle-remove {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border: none;
  border-radius: 4px;
  background: transparent;
  color: var(--text-muted, #bbb);
  cursor: pointer;
  flex-shrink: 0;
  transition: all 0.15s;
}

.subtitle-remove:hover {
  background: var(--danger-bg, #fef2f2);
  color: var(--danger-color, #ef4444);
}

.subtitle-add {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border: 1px dashed var(--border-color, #ddd);
  border-radius: 6px;
  background: transparent;
  color: var(--text-muted, #999);
  font-size: 0.8125rem;
  cursor: pointer;
  transition: all 0.15s;
}

.subtitle-add:hover {
  border-color: var(--primary-color, #b83a2a);
  color: var(--primary-color, #b83a2a);
  background: var(--primary-light-bg, var(--primary-light-color, rgba(184, 58, 42, 0.08)));
}

/* ── 卡片列表 ── */

.card-list {
  margin-top: 20px;
}

.card-list-empty {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-tertiary, #999);
}

.card-list-empty-hint {
  font-size: 13px;
  margin-top: 8px;
}

/* ── 插入按钮 ── */

.insert-zone {
  display: flex;
  justify-content: center;
  height: 12px;
  position: relative;
}

.insert-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 12px;
  border: 1px dashed var(--border-color, #ddd);
  border-radius: 12px;
  background: var(--bg-color, #fff);
  color: var(--text-muted, #aaa);
  font-size: 11px;
  cursor: pointer;
  transition: all 0.15s;
  z-index: 1;
  transform: translateY(-50%);
}

.insert-btn:hover {
  border-color: var(--primary-color, #b83a2a);
  color: var(--primary-color, #b83a2a);
  background: var(--primary-light-bg, var(--primary-light-color, rgba(184, 58, 42, 0.08)));
}

/* ── 底部 ── */

.editor-footer {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid var(--divider-color, #f0f0f0);
  display: flex;
  gap: 20px;
}

.footer-info {
  font-size: 12px;
  color: var(--text-tertiary, #999);
}

/* ── 文件操作入口 ── */

.editor-file-actions {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  background: var(--surface-color, #fff);
  border-top: 1px solid var(--border-color, #e8e6e4);
  flex-shrink: 0;
  justify-content: center;
}

/* ── 素材弹窗 ── */

.assets-modal {
  max-height: 70vh;
}

/* ── 标签建议过渡 ── */

.tag-suggest-enter-active,
.tag-suggest-leave-active {
  transition:
    opacity 0.15s,
    transform 0.15s;
}
.tag-suggest-enter-from,
.tag-suggest-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
