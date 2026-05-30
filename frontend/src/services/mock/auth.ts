import type { MockAuthData } from './types'

export const authMockData: MockAuthData = {
  users: {
    user: {
      id: '1',
      username: 'user',
      nickname: '普通用户',
      role: 'user',
      permissions: ['auth:me', 'blog:posts:read', 'blog:posts:write']
    },
    admin: {
      id: '2',
      username: 'admin',
      nickname: '管理员',
      role: 'admin',
      permissions: ['*']
    },
    guest: {
      id: '3',
      username: 'guest',
      nickname: '访客',
      role: 'guest',
      permissions: []
    }
  }
}
