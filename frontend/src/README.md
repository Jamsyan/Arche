# 前端项目目录结构说明

## 架构分层（从底层到上层）

```
┌───────────────────────────────────────────┐
│  业务层（views / layouts / plugins）     │
├───────────────────────────────────────────┤
│  组件层（components / 插件组件）         │
├───────────────────────────────────────────┤
│  工具层（hooks / composables / utils / directives）│
├───────────────────────────────────────────┤
│  核心服务层（services / store / router） │
├───────────────────────────────────────────┤
│  配置层（core / types / styles）         │
└───────────────────────────────────────────┘
```

## 目录详细说明

### 📁 core/ 核心层（最底层）

存放框架核心代码、全局初始化逻辑、基础能力封装

- `bootstrap.ts` - 应用启动初始化逻辑
- `plugin-loader.ts` - 插件加载器（和后端插件机制对齐）
- `constants.ts` - 全局常量定义
- `error-handler.ts` - 全局错误处理

### 📁 types/ 类型定义层

存放全局TypeScript类型定义

- `global.d.ts` - 全局类型
- `api.d.ts` - API接口类型
- `entity.d.ts` - 业务实体类型
- `permission.d.ts` - 权限相关类型

### 📁 styles/ 样式层

存放全局样式和设计系统

- `theme.css` - 主题变量（Design Token）
- `reset.css` - 样式重置
- `atomic.css` - 原子类工具
- `animation.css` - 全局动画定义

### 📁 services/ 服务层

存放全局服务

- `api/` - API接口统一管理（按模块划分）
- `request.ts` - 封装的请求实例
- `auth.ts` - 认证授权服务
- `storage.ts` - 本地存储服务
- `logger.ts` - 日志上报服务

### 📁 store/ 状态管理层

Pinia状态管理，按模块划分

- `modules/app.ts` - 应用全局状态
- `modules/user.ts` - 用户相关状态
- `modules/permission.ts` - 权限状态
- `plugins/` - Pinia插件

### 📁 router/ 路由层

Vue Router相关

- `index.ts` - 路由实例
- `guard.ts` - 路由守卫
- `dynamic.ts` - 动态路由注册逻辑
- `routes/` - 路由定义（按模块划分）

### 📁 utils/ 工具函数层

纯函数工具库，无副作用

- `date.ts` - 日期处理
- `string.ts` - 字符串处理
- `number.ts` - 数字处理
- `validate.ts` - 表单校验
- `file.ts` - 文件处理

### 📁 hooks/ 通用组合式函数层

可复用的Vue Composition API

- `useRequest.ts` - 请求封装
- `usePagination.ts` - 分页逻辑
- `useForm.ts` - 表单逻辑
- `usePermission.ts` - 权限判断

### 📁 composables/ 业务组合式函数层

业务相关的可复用逻辑（和hooks区别：和业务耦合）

- 按业务模块划分

### 📁 directives/ 自定义指令层

全局Vue自定义指令

- `permission.ts` - 权限指令（v-permission）
- `copy.ts` - 复制指令
- `debounce.ts` - 防抖指令
- `lazy-load.ts` - 懒加载指令

### 📁 components/ 组件层

全局通用组件

- `common/` - 基础组件（按钮、表单、弹窗等）
- `business/` - 业务通用组件
- `layout/` - 布局相关组件

### 📁 layouts/ 布局层

页面布局组件

- `BlogLayout.vue` - 公开页布局
- `PlatformLayout.vue` - 登录后布局
- `AdminLayout.vue` - 管理员布局

### 📁 views/ 页面层

业务页面，按模块划分

- 公共页面（首页、登录、404等）
- 用户模块页面
- 管理员模块页面
- 插件页面（动态加载）

### 📁 plugins/ 前端插件层

和后端插件对应，每个插件独立目录

- 插件按目录划分，每个插件自包含路由、组件、状态
- 支持动态加载/卸载

### 📁 assets/ 静态资源层

图片、字体、图标等静态资源
