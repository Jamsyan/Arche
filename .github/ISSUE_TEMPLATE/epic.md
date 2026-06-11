---
name: Epic 任务汇总
about: 创建一个 Epic 来汇总一组相关子任务（使用 GitHub Sub-issues）
title: '[Epic] '
labels: ''
assignees: ''

---

## 概述

<!-- 一句话说明这个 Epic 覆盖的范围 -->

## 子任务

<!-- 按类别分组，创建子 Issue 后填入编号 -->

### 类别 A

- [ ] #<编号> 子任务描述
- [ ] #<编号> 子任务描述

### 类别 B

- [ ] #<编号> 子任务描述

---

## 创建说明

1. 先为每个子任务创建独立的 Issue（使用"任务/代办"模板）
2. 记录每个子 Issue 的编号
3. 将编号填入上方的 checklist 中
4. 通过 GraphQL API 建立 sub-issue 关系：

```bash
gh api graphql -f query='
  mutation {
    addSubIssue(input: {issueId: "<epic_node_id>", subIssueId: "<child_node_id>"}) {
      subIssue { id }
    }
  }
'
```

## 建议标签

- **type**: `type: feature` / `type: enhancement`
- **priority**: `priority: high` / `priority: medium` / `priority: low`
