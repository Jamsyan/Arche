<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import { NLayout, NLayoutHeader, NLayoutSider, NLayoutContent, NMenu, useMessage } from 'naive-ui'
import { logout } from '@/composables/useAuth'
</script>

<template>
  <NLayout has-sider>
    <NLayoutHeader bordered>
      <div class="header-content">
        <h1 class="logo">Arche</h1>
        <div class="user-area">
          <span>当前用户</span>
          <button @click="logout" class="logout-btn">登出</button>
        </div>
      </div>
    </NLayoutHeader>
    <NLayout has-sider>
      <NLayoutSider bordered>
        <NMenu mode="vertical" :default-value="'/'">
          <NMenuItem key="/">首页</NMenuItem>
          <NMenuItem key="/posts">我的帖子</NMenuItem>
          <NMenuItem key="/profile">个人资料</NMenuItem>
        </NMenu>
      </NLayoutSider>
      <NLayoutContent>
        <RouterView />
      </NLayoutContent>
    </NLayout>
  </NLayout>
</template>

<style scoped>
.header-content {
  display: flex;
  align-items: center;
  height: 100%;
  padding: 0 24px;
}

.logo {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
}

.user-area {
  margin-left: auto;
  display: flex;
  gap: 12px;
  align-items: center;
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
