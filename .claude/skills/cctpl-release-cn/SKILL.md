---
name: cctpl-release-cn
description: "Prepare a release of the cookiecutter template: pre-checks, version bump suggestion, release-history.rst via /py-changelog, seed commit record, and the publish commands for the user to run. 准备发布模板."
disable-model-invocation: true
---
准备一次模板发布: 前置检查, 建议并修改 tpl 版本号, 更新 changelog, 记录 seed commit, 最后打印发布命令交给用户执行. 对应 `05-workflow.md` 的阶段 6. 本 skill 不执行发布本身.

Read ../cctpl-base-cn/SKILL.md, then:

- ../cctpl-base-cn/references/04-safety-rules.md
- ../cctpl-base-cn/references/05-workflow.md
- ../cctpl-base-cn/references/07-mise-task-contract.md
- ../cctpl-base-cn/references/08-versioning-and-release.md

Follow those docs to do the work.

## Steps

1. **前置检查** (08 的 Release Prep 第 1 步). 判断 seed 是否已 push 时, 用只读命令 (例如 `git ls-remote`) 比较本地 HEAD 和远端, 不运行 `git fetch`. 任何一项不满足:
   - seed 未提交或未 push: 按 04 的格式打印提交并 push seed 的命令, 停下.
   - artifact 不是最新: 告诉用户先运行 Sync, 停下.
   - 没有待发布的 artifact 变化: 告诉用户本次属于 "不发布", 停下.
2. **建议版本号.** 汇总 tpl repo 自上一个 tag 以来的变化, 以及 seed 自 `release-history.rst` 中上一次记录的 seed commit 以来的变化. 按 08 的 Bump Rules 给出建议级别, 新版本号, 以及决定这个级别的具体改动. **等用户确认** 后修改 `pyproject.toml`, 然后运行 `mise run sync`, 让 `_template_version` 和 `README.rst` 带上新版本号 (08 的 Release Prep). Sync 失败就停下报告.
3. **更新 changelog.** 运行 `/py-changelog`. 检查生成的条目是写给模板使用者看的 (08 的要求), 必要时改写. 在当前版本条目开头写入 seed commit 记录 (格式见 08 的 Seed Commit Record).
4. **打印发布命令.** 按 04 的 Handoff Format 打印 `publish-template` 的运行命令 (完整路径, 可单独复制). 说明它会做什么 (08 的 Publish), 以及执行完后运行 `/cctpl-verify-cn`.

## Output

结束时给出: 新版本号, bump 理由, changelog 条目, 记录的 seed commit, 发布命令. 然后停下, 等用户执行.

## Boundaries

- 不运行 `publish-template`, 不执行任何 git 写操作, 见 04.
- 版本号只在用户确认之后修改.
