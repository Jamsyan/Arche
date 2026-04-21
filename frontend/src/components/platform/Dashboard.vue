<template>
  <div class="dashboard">
    <!-- 用户信息卡片 -->
    <a-card :bordered="false" style="margin-bottom: 24px">
      <a-row :gutter="16" align="center">
        <a-col :span="16">
          <a-space direction="vertical" :size="8">
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
          <a-statistic title="我的文章" :value="0">
            <template #prefix>
              <icon-edit />
            </template>
          </a-statistic>
        </a-card>
      </a-grid-item>
      <a-grid-item>
        <a-card hoverable class="quick-card" @click="$router.push('/upload')">
          <a-statistic title="上传文件" :value="0">
            <template #prefix>
              <icon-upload />
            </template>
          </a-statistic>
        </a-card>
      </a-grid-item>
      <a-grid-item>
        <a-card hoverable class="quick-card" @click="$router.push('/storage')">
          <a-statistic title="存储管理" :value="0">
            <template #prefix>
              <icon-storage />
            </template>
          </a-statistic>
        </a-card>
      </a-grid-item>
      <a-grid-item>
        <a-card hoverable class="quick-card" @click="$router.push('/moderation')">
          <a-statistic title="审核中心" :value="0">
            <template #prefix>
              <icon-check-circle />
            </template>
          </a-statistic>
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
  max-width: 1200px;
  margin: 0 auto;
}

.quick-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.quick-card:hover {
  transform: translateY(-2px);
}
</style>
