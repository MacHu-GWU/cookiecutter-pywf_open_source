# Workflow

本文定义一次模板迭代的完整生命周期: 有哪些阶段, 每个阶段由谁执行, 进入和离开的条件, 失败时退回哪里. 前置阅读: `01-background-and-concepts.md`, `02-repo-layout.md`, `03-parameterization.md`, `04-safety-rules.md`.


## Overview

```mermaid
flowchart TD
    S1["1 Change"] --> S2["2 Seed Self-Test"]
    S2 --> S3["3 Sync"]
    S3 -- "参数化问题: 修 mechanism 后重跑" --> S3
    S3 -- "seed 内容问题" --> S1
    S3 --> S4["4 Review"]
    S4 -- "diff 有意外变化" --> S3
    S4 --> S5["5 Commit Seed"]
    S5 --> S6["6 Release Prep"]
    S6 --> S7["7 Publish"]
    S7 --> S8["8 Verify"]
    S8 -- "失败: 作为下一个 patch 修复" --> S1

    classDef agent fill:#e8f1fb,stroke:#3b6ea8,color:#1a2b40
    classDef human fill:#fdf0e1,stroke:#c07a2c,color:#40290f
    class S1,S2,S3,S6,S8 agent
    class S4,S5,S7 human
```

蓝色阶段由 agent 执行, 橙色阶段由人执行. agent 在每个由人执行的阶段之前停下, 交出控制权.


## Stages

| # | Stage | 执行者 | 入口条件 | 产出 | Skill |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | Change | agent | 一个改动需求 | seed 或 tpl source 中的改动 | `cctpl-change-cn`, `cctpl-add-param-cn` |
| 2 | Seed Self-Test | agent | seed 有改动 | seed 自己的测试 (及文档构建, 如相关) 通过 | `cctpl-change-cn` |
| 3 | Sync | agent | 阶段 1, 2 完成 | 新的 artifact 已从 `tmp/cctpl/template/` 应用到 tpl repo, 所有检查通过 | `cctpl-sync-cn` |
| 4 | Review | 你 | 阶段 3 通过 | 你认可 tpl repo 中 artifact 的 diff | — |
| 5 | Commit Seed | 你 | 阶段 4 通过 | seed 工作区干净, 已 push | — (agent 打印命令) |
| 6 | Release Prep | agent | seed 干净且已 push | tpl 版本号已 bump, `release-history.rst` 已更新并记录 seed SHA, 发布命令已打印 | `cctpl-release-cn` |
| 7 | Publish | 你 | 阶段 6 完成 | tpl commit + push, `preset/*` 已重新生成并推送, GitHub release 已创建 | — (执行打印的命令) |
| 8 | Verify | agent | 阶段 7 完成 | 从 GitHub 拉取已发布模板生成项目, 测试通过 | `cctpl-verify-cn` |

### 1 Change

先按 `01-background-and-concepts.md` 的 "Two Kinds of Change" 归类:

- template content → 改 seed.
- template mechanism → 改 tpl repo 的 source (参数化脚本, `hooks/` 等).
- 新增或修改 parameter → 两边都改, 用 `cctpl-add-param-cn`.

**不改 artifact.** 如果需求表述为 "改 template dir 中的某个文件", 翻译成 "改 seed 中对应的文件".

### 2 Seed Self-Test

在 seed 中运行它自己的测试 task; 改动涉及文档时, 也运行它的文档构建 task. 具体 task 名见 seed 的 `mise.toml`, 不同的仓库对各不相同. 只运行本地 task, 不运行发布类 task (见 `04-safety-rules.md`). 目的是保证进入参数化的素材本身是对的, 把 "seed 本身有 bug" 和 "参数化有 bug" 两类问题分开.

只改了 template mechanism 时跳过本阶段.

### 3 Sync

在 tpl repo 中运行 `mise run sync`, 它依次执行: 生成模板 → 检查 seed value 残留 → 用模板生成测试项目 (含 choice coverage) → 检查未解析占位符 → round trip 比较 → 检查 presets → 把 artifact 应用到 tpl repo. 任何一步失败立即停止. 这些步骤只读写本地文件, 速度快, 每次都全部运行.

改动涉及依赖, 构建, 测试配置, hooks 或 parameter 时, 本阶段还要在生成的项目中安装依赖并运行测试. 这一步较慢, 不包含在 `sync` 中, 按需单独运行.

任何一步失败:

- seed value 残留, 占位符未解析, Jinja 冲突 → 修参数化逻辑 (template mechanism), 从本阶段开头重跑.
- 问题出在 seed 内容本身 → 退回阶段 1.

本阶段结束后 agent 停下, 告诉你可以 review.

### 4 Review

你查看 tpl repo 中 artifact (`cookiecutter.json`, template dir, `README.rst`) 的 git diff. diff 应该只包含本次改动预期的变化. 出现意外变化 (例如大量无关文件被重新渲染) 时退回阶段 3 排查.

### 5 Commit Seed

你提交并 push seed 的改动. agent 只负责打印建议的命令.

之所以在 Release Prep 之前, 是因为 Release Prep 要记录 seed 的 commit SHA, 这个 SHA 必须是一个已经 push 的, 别人也能找到的 commit.

### 6 Release Prep

agent 确认 seed 已提交并 push, 并且模板产物 (`cookiecutter.json` + template dir) 确实有待发布的变化; 然后建议新的 tpl 版本号, 由你确认; 改完版本号后重新运行 `sync` (版本号也写在 artifact 里, 不重新生成, 发布出去的仍是旧版本号); 更新 tpl 的 `release-history.rst` 并记录 seed commit; 最后打印阶段 7 需要你执行的全部命令.

只改了 tpl repo 自身 (cctpl 文档, `.mise/tasks/` 等) 而模板产物没有变化时, 不进入本阶段: 改动照常由你 commit, 但不发布.

### 7 Publish

你执行阶段 6 打印的发布命令. 它会提交并推送 tpl repo, 重新生成 preset 分支, 创建 tag 和 GitHub release. agent 不执行其中任何一步, 见 `04-safety-rules.md`.

### 8 Verify

从 GitHub 拉取刚发布的模板 (包括 `main` 和需要验证的 `preset/*`), 生成项目到 `tmp/cctpl/verify/`, 与本地模板生成的结果逐字节比较, 再在生成的项目中安装依赖并运行测试. 这是唯一一个验证 "用户实际拿到的东西" 的阶段: 前面所有检查用的都是本地 `tmp/cctpl/template/` 中的模板.

失败时, 修复从阶段 1 重新开始, 作为下一个 patch 版本发布.


## Handoff Rules

- **agent 自动串联的范围:** 阶段 1 → 2 → 3 可以在同一会话中连续执行. 阶段 3 结束后必须停下. 原因: Review 是你的质量关口. 你必须在 seed 提交之前看到 artifact 的 diff, 否则问题会被一起提交, 甚至进入发布.
- **只能由你触发的阶段:** 6 (`/cctpl-release-cn`) 和 8 (`/cctpl-verify-cn`). agent 不自动进入. 原因: 阶段 6 决定 "发不发布, 发哪个版本", 发布之后无法撤回; 阶段 8 必须在你执行完阶段 7 之后才有意义, 只有你知道发布是否已经完成.
- **每次停下时**, agent 说清楚三件事: 当前完成到哪个阶段, 结果如何, 下一步由谁做什么 (需要你执行命令时, 按 `04-safety-rules.md` 的格式给出).
- **一次迭代可以包含多次 Change.** 阶段 1 → 3 可以反复循环, 攒够一批改动再进入阶段 4.


## Outside the Stages: Local Trial

`mise run try-template` (或 `mise run try-template <preset>`) 从 seed 当前的工作区生成模板, 用默认值或某个 preset 渲染一个项目, 再在项目中运行它自己的 mise task (安装, 测试覆盖率, 文档构建). 它不检查也不应用 artifact, 不属于任何阶段, 随时可用. 最常见的用途是 Review 之前亲眼看看生成项目的效果.
