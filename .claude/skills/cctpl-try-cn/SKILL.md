---
name: cctpl-try-cn
description: "Try the cookiecutter template locally the way a human would: make it from the seed, render a project with default values or a preset, and run the project's own mise tasks (such as install, test coverage, docs build) with step-by-step logs. Use when the user wants to test or see the generated project locally (本地测一测, 本地试用模板, 生成一个项目看看效果, 跑一下 cov 和 build-doc, try the template)."
argument-hint: "[preset name]"
---
本地试用模板: 从 seed 生成模板, 用默认值或指定 preset 渲染一个项目, 再在项目里通过 mise 运行 `.mise/tasks/cctpl/pair.py` 的 `PROJECT_TASKS` 中列出的 task, 并报告每一步的结果. 这是 `06-verification.md` 中推荐的 Local Trial 机制, 不属于 8 个阶段中的任何一个, 可以随时使用.

Read ../cctpl-base-cn/SKILL.md, then:

- ../cctpl-base-cn/references/02-repo-layout.md
- ../cctpl-base-cn/references/04-safety-rules.md
- ../cctpl-base-cn/references/06-verification.md
- ../cctpl-base-cn/references/07-mise-task-contract.md
- ../cctpl-base-cn/references/09-troubleshooting.md

Follow those docs to do the work.

## Steps

1. **确定 preset.** 用户给了 preset 名就用它, 否则用默认值. 用户说的名字不在 `presets/*.json` 中时, 列出可用的 preset 并询问.
2. **运行.** 从 tpl repo 根目录运行 `mise run try-template` 或 `mise run try-template <preset>`. 它耗时较长 (安装依赖, 构建文档), 耐心等待, 不要中途重试.
3. **读结果.** 读取输出最后的 `=== Try result` 一节. 有失败时, 只看失败那一步的 `[try i/n]` 日志块 (日志文件路径在输出末尾), 按 09 判断问题出在 seed 内容还是参数化.

## Output

- 每个 task 的 PASS / FAIL / SKIP 和耗时.
- 生成项目的路径和日志文件路径.
- 有失败时: 失败的 task, 关键的错误行, 初步判断的原因和建议的下一步 (回到 Change 修 seed, 或修参数化).
- 用户想接着手工操作时, 按 04 的 Handoff Format 给出进入项目目录, 运行 `mise trust`, 再运行 task 的命令. `mise trust` 会写入 mise 的信任记录, 由用户自己执行.

## Boundaries

- 不修改 seed 或 tpl repo 的任何文件; 只写 `tmp/cctpl/`. 注意它会覆盖 `tmp/cctpl/stage/` 和 `tmp/cctpl/template/` (见 06 的 Local Trial): 之后要运行 `test-output` 或 `verify-release` 时, 先确认 `template/` 对应的 seed 状态是对的.
- 不打印任何环境变量的值. 用 preset 试用时, 项目的 mise 会读取真实 secret.
- 不执行任何 git 写操作, 见 04.
