<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { NButton, NDescriptions, NDescriptionsItem, NModal, NTag, useMessage } from 'naive-ui'
import { useUserStore } from '@/store/modules/user'

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
      <NDescriptions :column="1" :bordered="false" label-style="width: 100px">
        <NDescriptionsItem label="用户ID">
          {{ userStore.userInfo?.id || '-' }}
        </NDescriptionsItem>
        <NDescriptionsItem label="用户名">
          {{ userStore.userInfo?.username || '-' }}
        </NDescriptionsItem>
        <NDescriptionsItem label="昵称">
          {{ userStore.userInfo?.nickname || '-' }}
        </NDescriptionsItem>
        <NDescriptionsItem label="角色">
          <NTag
            :type="userStore.userInfo?.role === 'admin' ? 'error' : 'primary'"
            :bordered="false"
          >
            {{
              userStore.userInfo?.role === 'admin'
                ? '管理员'
                : userStore.userInfo?.role === 'user'
                  ? '普通用户'
                  : '访客'
            }}
          </NTag>
        </NDescriptionsItem>
        <NDescriptionsItem label="权限">
          {{
            userStore.userInfo?.permissions.length
              ? `${userStore.userInfo.permissions.length} 项权限`
              : '无权限'
          }}
        </NDescriptionsItem>
        <NDescriptionsItem label="注册时间">
          {{ (userStore.userInfo as any)?.created_at || '-' }}
        </NDescriptionsItem>
      </NDescriptions>

      <div class="action-section">
        <NButton type="error" @click="showLogoutModal = true">退出登录</NButton>
      </div>
    </div>

    <NModal
      v-model:show="showLogoutModal"
      title="确认退出"
      preset="dialog"
      positive-text="确认"
      negative-text="取消"
      @positive-click="handleLogout"
    >
      <p>确定要退出当前账号吗？</p>
    </NModal>
  </div>
</template>

<style scoped>
.profile-page {
  max-width: 100%;
}

.page-heading {
  margin-bottom: 16px;
}

.page-heading h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}

.section-card {
  background: rgba(255, 248, 236, 0.72);
  border: 1px solid rgba(130, 95, 65, 0.14);
  border-radius: var(--radius-md);
  padding: 20px;
  backdrop-filter: blur(4px);
}

.action-section {
  display: flex;
  justify-content: center;
  margin-top: var(--spacing-xl);
}
</style>
