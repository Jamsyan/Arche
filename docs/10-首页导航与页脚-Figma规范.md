# 锦年志首页导航与页脚 Figma 规范

## 1. 目标
本规范用于在 Figma 中先行搭建首页 Header/Footer 组件，确保后续代码实现与品牌调性一致，并可复用到更多页面。

## 2. 组件拆分
- Header/LogoArea：站点名、品牌副标题
- Header/NavLinks：首页、探索、关于
- Header/Actions：搜索框、登录或加入我们按钮
- Footer/BrandBlock：品牌描述与版权
- Footer/LinkGroup：快速导航、隐私条款、联系与社媒

## 3. Token 映射（来自 `frontend/src/styles/theme.css`）
- 色彩：
  - 主色 `--primary-color` = `#3b82f6`
  - 主色悬停 `--primary-hover-color` = `#60a5fa`
  - 文字主色 `--text-primary`
  - 文字次级 `--text-secondary`
  - 边框 `--border-color`
- 圆角：
  - 小圆角 `--radius-sm` = `8px`
  - 中圆角 `--radius-md` = `12px`
  - 大圆角 `--radius-lg` = `16px`
- 间距：
  - `--spacing-sm` = `8px`
  - `--spacing-md` = `16px`
  - `--spacing-lg` = `24px`
- 视觉：
  - 玻璃底 `--glass-bg`
  - 模糊 `--glass-blur`
  - 阴影 `--shadow-glass`

## 4. Header 规格建议
- 高度：桌面端 `72px`，移动端 `64px`
- 内容宽度：`min(1200px, 100%)`
- 导航项状态：默认、hover、active 三态
- 搜索框：全局搜索，支持回车跳转探索页
- 用户入口：未登录显示“加入我们”，已登录显示“创作后台”

## 5. Footer 规格建议
- 三列结构：
  - 列1：锦年志品牌描述
  - 列2：站点导航（首页、探索、关于）
  - 列3：联系与条款（联系、隐私与条款）
- 底部版权行：`© 当前年份 锦年志`

## 6. 探索页入口联动
- Header 的“探索”是一级入口。
- 探索页内部采用“双栏”：
  - 左侧：堆积式标签列表（可滚动、可搜索）
  - 右侧：按筛选结果展示日志列表

## 7. 实施建议
- 先产出低保真线框确认信息架构。
- 再替换为高保真 Token 样式。
- 最后再进入代码实现，避免视觉与交互频繁返工。
