---
name: cctpl-verify-cn
description: "Verify the published cookiecutter template end to end: generate projects from GitHub for main and preset branches, compare with the local result, run their tests, and report pass or fail. 验证已发布的模板."
disable-model-invocation: true
context: fork
agent: general-purpose
argument-hint: "[branch ...]"
---
验证刚发布到 GitHub 的模板: 对 `main` 和 preset 分支从 GitHub 生成项目, 与本地结果比较, 运行测试, 只报告结论. 对应 `05-workflow.md` 的阶段 8 和 `06-verification.md` 的 L5.

本 skill 在 forked context 中运行, 看不到主会话. 所需的一切都在 base 中. base 位于本 skill 的兄弟目录: `${CLAUDE_SKILL_DIR}/../cctpl-base-cn/`.

Read ../cctpl-base-cn/SKILL.md, then:

- ../cctpl-base-cn/references/02-repo-layout.md
- ../cctpl-base-cn/references/06-verification.md
- ../cctpl-base-cn/references/07-mise-task-contract.md
- ../cctpl-base-cn/references/08-versioning-and-release.md
- ../cctpl-base-cn/references/09-troubleshooting.md

Follow those docs to do the work.

## Task

要验证的分支: $ARGUMENTS

参数为空时, 验证 `main` 和 tpl repo `presets/*.json` 对应的全部 `preset/*` 分支.

1. **准备本地对照物.** L5 拿已发布的模板与本地 `tmp/cctpl/template/` 比较, 所以本地模板必须由刚发布的 seed commit 生成. 先确认两点: seed 的 HEAD (`git -C <seed> rev-parse --short HEAD`, seed 路径来自 `CCTPL_SEED_DIR`) 等于 tpl repo `release-history.rst` 最新版本条目中记录的 seed commit (08 的 Seed Commit Record); seed 工作区干净 (`git -C <seed> status --porcelain` 为空). 两点都满足时, **总是** 运行 `mise run make-template`, 不复用已有的 `template/` (它可能已被 `try-template` 或之后的 Sync 覆盖). 任何一点不满足时, 不运行验证, 直接报告原因.
2. 从 tpl repo 根目录运行 `mise run verify-release`, 有指定分支时作为参数传入 (例如 `mise run verify-release main`). 它按 06 的 L5 步骤完成拉取, 与本地比较, 安装和测试, 并用私有的 clone 缓存避开 `~/.cookiecutters`.
3. 读取它最后的 `=== Verify result` 一节, 对每个失败按 09 判断可能的原因.

## Report

按 06 的 Report 要求返回, 不附完整日志:

```markdown
## Verify Result: <PASS | FAIL>

| Branch | Fetch | Compare | Tests | Note |
| :--- | :--- | :--- | :--- | :--- |
| main | ok | ok | ok | |
| preset/<name> | ok | n/a | fail | <一句话> |

### Failures
- <branch>: <失败的步骤>, <文件:行号>, <按 09 判断的可能原因>
```

## Boundaries

- 只读写 `tmp/cctpl/verify/`, 以及 make-template 写入的 `tmp/cctpl/stage/` 和 `tmp/cctpl/template/`. 不修改任何其他文件, 不尝试修复问题: 修复从主会话的 Change 阶段重新开始.
- 不执行任何 git 写操作, 不写入 GitHub, 见 ../cctpl-base-cn/references/04-safety-rules.md.
