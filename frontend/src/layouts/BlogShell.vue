<script setup lang="ts">
import { RouterView, useRouter } from 'vue-router'
import { NLayout, NLayoutHeader, NLayoutContent, NMenu } from 'naive-ui'
import { useUserStore } from '@/store/modules/user'

const router = useRouter()
const userStore = useUserStore()

const handleLogout = async () => {
  await userStore.logout()
  await router.push('/login')
}
</script>

<template>
  <NLayout has-sider>
    <NLayoutHeader bordered>
      <div class="header-content">
        <h1 class="logo">Arche</h1>
        <NMenu mode="horizontal" value="/" class="nav-menu">
          <NMenuItem key="/">首页</NMenuItem>
        </NMenu>
        <div class="user-area">
          <button @click="handleLogout" class="logout-btn">登出</button>
        </div>
      </div>
    </NLayoutHeader>
    <NLayoutContent>
      <RouterView />
    </NLayoutContent>
  </NLayout>
</template>

<style scoped>
.header-content {
  display: flex;
  align-items: center;
  height: 100%;
  padding: 0 24px;
  gap: 32px;
}

.logo {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
}

.nav-menu {
  flex: 1;
  border: none;
}

.user-area {
  display: flex;
  gap: 12px;
}

.logout-btn {
  padding: 8px 16px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  background: white;
  cursor: pointer;
}

.logout-btn:hover {
  border-color: #1890ff;
  color: #1890ff;
}
</style>
