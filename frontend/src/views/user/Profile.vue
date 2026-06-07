<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { useUserStore } from '@/store/modules/user'
import ArButton from '@/components/ui/ArButton.vue'
import ArTag from '@/components/ui/ArTag.vue'

const router = useRouter()
const message = useMessage()
const userStore = useUserStore()

const showLogoutModal = ref(false)

const handleLogout = async () => {
  try {
    await userStore.logout()
    message.success('退出登录成功')
    await router.push('/login')
  } catch {
    message.error('退出登录失败')
  } finally {
    showLogoutModal.value = false
  }
}
</script>

<template>
  <div class="profile-page">
    <div class="page-heading">
      <h2>个人资料</h2>
    </div>

    <div class="section-card">
      <div class="info-grid">
        <div class="info-row">
          <span class="info-label">用户名</span>
          <span class="info-value">{{ userStore.userInfo?.username || '-' }}</span>
        </div>
        <div class="info-row">
          <span class="info-label">昵称</span>
          <span class="info-value">{{ userStore.userInfo?.nickname || '-' }}</span>
        </div>
        <div class="info-row">
          <span class="info-label">角色</span>
          <span class="info-value">
            <ArTag
              :color="(userStore.userInfo?.level ?? 5) === 0 ? 'red' : 'primary'"
              type="light"
              size="sm"
            >
              {{ (userStore.userInfo?.level ?? 5) === 0 ? '管理员' : '普通用户' }}
            </ArTag>
          </span>
        </div>
        <div class="info-row">
          <span class="info-label">权限</span>
          <span class="info-value">
            {{
              userStore.userInfo?.permissions.length
                ? `${userStore.userInfo.permissions.length} 项权限`
                : '无权限'
            }}
          </span>
        </div>
        <div class="info-row">
          <span class="info-label">注册时间</span>
          <span class="info-value">{{ userStore.userInfo?.created_at?.slice(0, 10) || '-' }}</span>
        </div>
      </div>

      <div class="action-section">
        <ArButton type="danger" @click="showLogoutModal = true">退出登录</ArButton>
      </div>
    </div>

    <!-- 退出确认弹窗 -->
    <Teleport to="body">
      <div v-if="showLogoutModal" class="modal-overlay" @click.self="showLogoutModal = false">
        <div class="modal-card">
          <div class="modal-header">
            <span class="modal-title">确认退出</span>
          </div>
          <div class="modal-body">
            <p>确定要退出当前账号吗？</p>
          </div>
          <div class="modal-footer">
            <ArButton type="ghost" @click="showLogoutModal = false">取消</ArButton>
            <ArButton type="danger" @click="handleLogout">确认</ArButton>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.profile-page {
  max-width: 100%;
}

.page-heading {
  margin-bottom: var(--spacing-lg);
}

.page-heading h2 {
  margin: 0;
  font-size: 24px;
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
}

.section-card {
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: var(--spacing-lg);
  backdrop-filter: blur(4px);
}

.info-grid {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.info-row {
  display: flex;
  align-items: center;
  padding: var(--spacing-sm) 0;
  border-bottom: 1px solid var(--divider-color);
}

.info-row:last-child {
  border-bottom: none;
}

.info-label {
  width: 100px;
  flex-shrink: 0;
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: var(--font-weight-medium);
}

.info-value {
  font-size: 14px;
  color: var(--text-primary);
}

.action-section {
  display: flex;
  justify-content: center;
  margin-top: var(--spacing-xl);
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--divider-color);
}

/* 模态框 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(26, 24, 23, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-card {
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xl);
  width: 400px;
  max-width: 90vw;
}

.modal-header {
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--divider-color);
}

.modal-title {
  font-size: 16px;
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}

.modal-body {
  padding: var(--spacing-lg);
}

.modal-body p {
  margin: 0;
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-sm);
  padding: var(--spacing-md) var(--spacing-lg);
  border-top: 1px solid var(--divider-color);
}
</style>
