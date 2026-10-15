---
name: cctpl-base-cn
description: "Shared knowledge for the cctpl-*-cn skills that maintain a cookiecutter tpl repo + seed repo pair (seed → 参数化 → 模板 → 发布): concepts, repo layout, workflow, mise task contract, parameterization, safety rules, versioning, verification. Use to answer questions about how this template pair is maintained (模板仓库, 种子仓库, seed repo, template dir, preset 分支) or to decide which cctpl invoker fits."
---
cctpl 家族负责维护一对 cookiecutter 仓库: seed repo (可运行的具体项目) 和 tpl repo (把 seed 参数化成模板并发布). 本 skill 是家族的 base, 只存放共享规范, 不绑定任何单一动作, 也不绑定任何具体的仓库对. 具体值 (seed 路径, parameters, 版本号) 一律从仓库中读取, 位置见 `references/02-repo-layout.md` 的 "Where Facts Live".

本家族文档正文为中文, 标题, 文件名, 术语为英文. `references/` 是唯一的 source of truth: `.mise/tasks/` 的实现或 tpl repo 的 `CLAUDE.md` 与之冲突时, 以本 skill 为准, 并修正对方. `CLAUDE.md` 只指向本家族, 不重复其中的规则.

## Files

`references/` 按编号顺序阅读. 编号表示单向依赖: 后面的文件可以引用前面的, 前面的文件不引用后面的, 也不使用后面才定义的术语. 一个标识符 (task 名, 文件名) 在出现的地方附带了一句话说明, 就算已定义. 修改 references 时保持这条规则.

| File | 内容 | 状态 |
| :--- | :--- | :--- |
| `references/01-background-and-concepts.md` | 背景: 模板为什么难以持续维护, seed / tpl 设计如何解决; 术语, 命名规范, 两类改动, skill 放在哪里, 两个独立版本号 | done |
| `references/02-repo-layout.md` | tpl repo 与 seed repo 的结构, 三类文件 (source / artifact / workspace), 分支, preset 分支如何从 `main` + `presets/*.json` 派生, 每类具体值的位置 | done |
| `references/03-parameterization.md` | round trip 正确性定义, seed value 选择, selector 限定, 合法残留, exclude / no_render, Jinja 冲突, hooks, choice coverage | done |
| `references/04-safety-rules.md` | agent 不执行 git 写操作, 安全级别 A / U, 标准 deny 列表, "Commands for you to run" 输出格式 | done |
| `references/05-workflow.md` | 8 个阶段的生命周期, 执行者, 入口与产出, 失败回退, 交接规则 | done |
| `references/06-verification.md` | 五个验证层级 L1 – L5, L4 不依赖 secret, Local Trial, L5 的步骤与报告, 改动类型与所需层级 | done |
| `references/07-mise-task-contract.md` | 每个 mise task 的名称, 输入, 输出, 退出码, 安全级别 | done |
| `references/08-versioning-and-release.md` | tpl 版本号 bump 规则, Release Prep 步骤, seed commit 记录, Publish | done |
| `references/09-troubleshooting.md` | 按出错位置列出的现象, 原因, 修法 | done |
| `assets/settings-permissions.json` | 标准 `additionalDirectories` 与 deny 片段 | done |

## Invokers

| Invoker | 做什么 | 读取的 base 文件 | 触发 |
| :--- | :--- | :--- | :--- |
| `cctpl-change-cn` | 归类改动需求, 在 seed 或 tpl source 中实施, 跑 seed 自测, 接着执行 sync | 01, 02, 03, 04, 05 | agent 或用户 |
| `cctpl-sync-cn` | 生成模板, 全部检查, 应用 artifact; 诊断并修复参数化问题 | 02, 03, 04, 05, 06, 07, 08, 09 | agent 或用户 |
| `cctpl-add-param-cn` | 新增或修改一个 cookiecutter parameter, 两边联动 | 01, 02, 03, 04, 06, 07, 08 | agent 或用户 |
| `cctpl-try-cn` | 本地试用: 生成模板, 渲染项目, 通过 mise 跑项目自己的 task, 报告日志 | 02, 04, 06, 07, 09 | agent 或用户 |
| `cctpl-release-cn` | 前置检查, 版本 bump, changelog, 记录 seed SHA, 打印发布命令 | 04, 05, 07, 08 | 仅用户 |
| `cctpl-verify-cn` | 从 GitHub 拉取已发布模板, 生成项目并测试 (forked context) | 02, 06, 07, 08, 09 | 仅用户 |
| `cctpl-fork-cn` | 把本家族一次性复制到另一对仓库, 改写其中与本仓库对绑定的内容. 复制之后两边彻底独立 | 01, 02, 03, 04, 06, 07, 09 | 仅用户 |

阶段与 invoker 的对应关系见 `references/05-workflow.md`. `cctpl-fork-cn` 不属于任何阶段.

## External Skills

以下两个 skill 与本家族放在同一个 tpl repo 的 `.claude/skills/` 下, 但不属于本家族:

- `/pypi-cookiecutter_maker`: 参数化所用的 `cookiecutter_maker` 库的 API. 本家族不重复其内容.
- `/py-changelog`: 维护 `release-history.rst`. Release Prep 阶段使用.

这对仓库自己的当前状态 (未完成的事项) 不写在本 skill 中, 而是写在 tpl repo `CLAUDE.md` 的 Current Status 一节.
