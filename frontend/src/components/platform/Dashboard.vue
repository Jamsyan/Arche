<template>
  <div class="dashboard">
    <!-- 用户信息卡片 -->
    <a-card :bordered="false" class="profile-card">
      <a-row :gutter="24" align="center">
        <a-col :span="16">
          <a-space direction="vertical" :size="12">
            <a-typography-title :heading="4" style="margin: 0">
              {{ userInfo?.username ?? '加载中...' }}
            </a-typography-title>
            <a-descriptions :column="2" size="small">
              <a-descriptions-item label="用户等级">
                <LevelBadge :level="userInfo?.level ?? 5" />
              </a-descriptions-item>
              <a-descriptions-item label="角色">
                {{ roleLabel }}
              </a-descriptions-item>
              <a-descriptions-item label="注册时间">
                {{ formatDate(userInfo?.created_at) }}
              </a-descriptions-item>
              <a-descriptions-item label="邮箱">
                {{ userInfo?.email ?? '未设置' }}
              </a-descriptions-item>
            </a-descriptions>
          </a-space>
        </a-col>
        <a-col :span="8" style="text-align: center">
          <a-statistic title="存储空间" :value="storageUsed" suffix="MB">
            <template #prefix>
              <icon-storage />
            </template>
          </a-statistic>
        </a-col>
      </a-row>
    </a-card>

    <!-- 快捷入口 -->
    <a-grid :cols="4" :col-gap="16" :row-gap="16">
      <a-grid-item>
        <a-card hoverable class="quick-card" @click="$router.push('/editor')">
          <icon-edit class="quick-icon" />
          <div class="quick-title">我的文章</div>
          <div class="quick-desc">撰写和管理博客文章</div>
        </a-card>
      </a-grid-item>
      <a-grid-item>
        <a-card hoverable class="quick-card" @click="$router.push('/upload')">
          <icon-upload class="quick-icon" />
          <div class="quick-title">上传文件</div>
          <div class="quick-desc">拖拽或点击上传文件</div>
        </a-card>
      </a-grid-item>
      <a-grid-item>
        <a-card hoverable class="quick-card" @click="$router.push('/storage')">
          <icon-storage class="quick-icon" />
          <div class="quick-title">存储管理</div>
          <div class="quick-desc">查看和管理存储空间</div>
        </a-card>
      </a-grid-item>
      <a-grid-item>
        <a-card hoverable class="quick-card" @click="$router.push('/moderation')">
          <icon-check-circle class="quick-icon" />
          <div class="quick-title">审核中心</div>
          <div class="quick-desc">审批待发布的内容</div>
        </a-card>
      </a-grid-item>
    </a-grid>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  IconEdit,
  IconUpload,
  IconStorage,
  IconCheckCircle,
} from '@arco-design/web-vue/es/icon'
import LevelBadge from '../LevelBadge.vue'
import { useAuth } from '../../router/auth.js'

const { getToken, loadUser, user } = useAuth()

const userInfo = ref(null)
const storageUsed = ref(0)

const ROLE_LABELS = {
  0: '管理员',
  1: '高级用户',
  2: '中级用户',
  3: '初级用户',
  4: '注册用户',
  5: '访客',
}

const roleLabel = computed(() => ROLE_LABELS[userInfo.value?.level ?? 5] ?? '未知')

function formatDate(dateStr) {
  if (!dateStr) return '未知'
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

onMounted(async () => {
  await loadUser()
  if (user.value) {
    userInfo.value = user.value
  }
})
</script>

<style scoped>
.dashboard {
  max-width: 1000px;
  margin: 0 auto;
}

.profile-card {
  margin-bottom: 24px;
  border-radius: var(--border-radius-large);
  padding: 24px;
}

.quick-card {
  cursor: pointer;
  border-radius: var(--border-radius-large);
  padding: 24px 16px;
  text-align: center;
  transition: transform 0.2s, box-shadow 0.2s;
}
.quick-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
.quick-icon {
  font-size: 28px;
  color: var(--color-primary);
  margin-bottom: 8px;
}
.quick-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-1);
  margin-bottom: 4px;
}
.quick-desc {
  font-size: 12px;
  color: var(--color-text-3);
}
</style>
