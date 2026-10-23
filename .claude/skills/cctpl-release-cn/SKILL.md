---
name: cctpl-release-cn
description: "Prepare a release of the cookiecutter template: confirm the shared version from the seed is bumped, tagged and in sync (mise run check-release), write the tpl changelog section via /cctpl-changelog-cn, and print the publish command for the user to run. Never bumps the version here. 准备发布模板."
disable-model-invocation: true
---
准备一次模板发布: 用 `check-release` 做前置检查, 写 tpl changelog, 最后打印发布命令交给用户执行. 对应 `05-workflow.md` 的阶段 6. 本 skill 不 bump 版本号 (版本号只在 seed 中 bump, 是阶段 5 的事), 也不执行发布本身.

Read ../cctpl-base-cn/SKILL.md, then:

- ../cctpl-base-cn/references/04-safety-rules.md
- ../cctpl-base-cn/references/05-workflow.md
- ../cctpl-base-cn/references/07-mise-task-contract.md
- ../cctpl-base-cn/references/08-versioning-and-release.md

Follow those docs to do the work.

## Steps

1. **前置检查** (08 的 Release Prep 第 1 步). 运行 `mise run check-release`, 逐项看输出. tpl changelog 那一项此时失败是正常的. 其余项失败时:
   - 版本号不一致, 或模板产物与 seed 生成的不一致: 运行 `mise run sync`. 它在 artifact 上产生了新的 diff 时停下, 请用户先 review.
   - seed 版本号没有 bump (tpl 已有这个版本的 tag), 或 seed changelog 缺少条目: 停下, 告诉用户先在 seed 中完成 Seed Release 第 1 步 (seed 的 `pywf-oss-changelog-seed-repo`).
   - seed 未提交, 未 push, 或远端没有这个版本的 tag: 按 04 的格式打印 Seed Release 第 3 步的命令 (seed 中 commit, push, 然后运行 seed 自己的发布 task, 例如 `mise run release`; seed 发布到 PyPI 时还有 `mise run publish`. 以 seed 的 `mise.toml` 为准), 停下.
   - 没有待发布的模板产物变化: 告诉用户本次属于 "不发布" (08 的 Bump Rules), 停下.
2. **写 tpl changelog.** 运行 `/cctpl-changelog-cn`. 检查条目是写给模板使用者看的, 开头一行 (seed 链接) 与 `check-release` 打印的预期内容一致.
3. **再次检查.** `mise run check-release` 必须全部通过. 不通过就停下报告.
4. **打印发布命令.** 按 04 的 Handoff Format 打印 `publish-template` 的运行命令 (完整路径, 可单独复制). 说明它会做什么 (08 的 Publish: 先重跑检查, 只创建 tag, 不覆盖, 最后更新 preset 分支), preset 推送失败时只重跑 `mise run publish-presets`, 以及执行完后运行 `/cctpl-verify-cn`.

## Output

结束时给出: 版本号, changelog 条目, seed tag 指向的 commit, `check-release` 的结果, 发布命令. 然后停下, 等用户执行.

## Boundaries

- 不运行 `publish-template`, 不运行 seed 的发布 task, 不执行任何 git 写操作, 见 04.
- 不修改任何版本号. tpl repo 中的版本号只由 `sync` 从 seed 复制.
