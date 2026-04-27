# 前端目录与基建约定

## 当前目录职责

- `services/`：接口定义与请求封装，所有 API 必须通过 `request.ts` 统一走拦截器。
- `store/`：全局状态中心，`app/user/permission` 三个核心 Store 统一管理外壳、身份与权限。
- `router/`：路由定义、守卫与菜单构建逻辑，角色路由统一放在 `router/modules`。
- `layouts/`：应用壳布局，侧边栏菜单从动态路由生成，不在页面中硬编码。
- `views/`：业务页面；页面内复用组件放在 `views/<module>/components`。
- `components/`：全局可复用基础组件，例如 `ProTable`、`ProForm`。
- `composables/`：可复用业务逻辑钩子，例如 `useTable`、`useForm`。
- `styles/`：设计 token、主题与动画；颜色和圆角统一从 CSS 变量读取。
- `directives/`：全局指令，例如 `v-permission`。
- `constants/`、`types/`、`utils/`：常量、类型和纯工具函数。

## 统一开发规则

1. **请求层统一**：禁止在页面里直接创建 axios 实例。
2. **权限统一**：页面权限用路由 `meta.permission`，按钮权限用 `v-permission`。
3. **菜单统一**：新增页面只改路由，不再单独维护侧边栏配置。
4. **状态统一**：登出或 token 失效时走统一 reset，避免残留状态污染。
5. **样式统一**：优先使用 token 和基础组件，减少页面重复样式代码。

## 推荐新增模块流程

1. 在 `services/api` 增加模块接口定义。
2. 在 `router/modules` 增加路由并补全 `meta`（`title/layout/permission/icon`）。
3. 在 `views` 新建页面；复用逻辑抽到 `composables`。
4. 如有可复用 UI 结构，优先沉淀到 `components`（Pro 系列）。

## API 对照与调用规范

- API 合同台账：`frontend/docs/api-contract.md`
- 错误处理与 silent 约定：`frontend/docs/api-call-policy.md`
