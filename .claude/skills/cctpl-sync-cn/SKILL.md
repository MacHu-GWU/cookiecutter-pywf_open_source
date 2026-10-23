---
name: cctpl-sync-cn
description: "Regenerate the cookiecutter template from the seed repo, run all template checks (shared version, seed value residue, generation, unresolved placeholders, round trip, presets), apply the artifacts and copy the seed's version into the tpl repo, and fix parameterization problems. Use after the seed or the parameterization changed, or when the user asks to sync, rebuild, or check the template (同步模板, 重新生成模板, make template, 检查模板, 跑一下 sync)."
---
从 seed 重新生成模板, 跑完所有检查, 把 artifact 应用到 tpl repo; 检查失败时诊断并修复参数化问题. 对应 `05-workflow.md` 的阶段 3.

Read ../cctpl-base-cn/SKILL.md, then:

- ../cctpl-base-cn/references/02-repo-layout.md
- ../cctpl-base-cn/references/03-parameterization.md
- ../cctpl-base-cn/references/04-safety-rules.md
- ../cctpl-base-cn/references/05-workflow.md
- ../cctpl-base-cn/references/06-verification.md
- ../cctpl-base-cn/references/07-mise-task-contract.md
- ../cctpl-base-cn/references/08-versioning-and-release.md
- ../cctpl-base-cn/references/09-troubleshooting.md

Follow those docs to do the work.

## Steps

1. **前置检查.** `CCTPL_SEED_DIR` 已设置且目录存在. 不满足就停下说明.
2. **运行 `sync`.** 从 tpl repo 根目录运行 `mise run sync`.
3. **失败时修复.** 找出最早失败的那一层, 按 09 判断问题在哪一侧:
   - 参数化问题: 修参数化脚本 (或 `hooks/`, `presets/`), 重新运行 `sync`.
   - `check-version` 失败 (seed 的版本号或 seed changelog 有问题): 属于 seed 一侧, 按 09 的 Release Checks 告诉用户在 seed 中怎么修, 不在 tpl repo 中改版本号.
   - seed 内容问题: 停下, 告诉用户需要回到 Change 阶段, 并说明原因. 不在这里改 seed 内容.
   - 同一个失败修了 3 次仍未解决: 停下, 报告已尝试的修法和当前的输出.
4. **按需运行 L4.** 按 06 的 "Levels by Change" 判断本次改动是否需要 `test-output`, 以及 `CHOICE_COVERAGE` 是否需要更新; 需要就运行或更新, 失败按第 3 步处理.
5. **展示 artifact 变化.** 用 `git diff --stat` 展示 artifact (`cookiecutter.json`, template dir, `README.rst`) 以及版本号 (`pyproject.toml`, `uv.lock`) 的变化, 并用一两句话说明这些变化是否符合本次改动的预期. 出现预期之外的变化时明确指出.

## Output

结束时停下, 输出:

- 每一层的结果 (L1 – L3, 以及是否运行了 L4).
- 为修复问题而改过的参数化相关文件.
- artifact 的 diff 摘要.
- 推荐: 想亲眼看看生成项目的效果时, 运行 `/cctpl-try-cn` (可带 preset 名), 或直接用 `mise run e2e`.
- 下一步: 请用户 review artifact 的 diff. review 通过后, 按 04 的 Handoff Format 给出提交命令 (commit message 由你起草):
  - seed 有改动并准备发布时: 说明先在 seed 中 bump 版本号并写 seed changelog (seed 的 `pywf-oss-changelog-seed-repo`), 重新 `sync`, 再提交, push 并发布 seed (08 的 Seed Release), 之后运行 `/cctpl-release-cn`.
  - seed 有改动但暂不发布时: 提交并 push seed 的命令.
  - seed 没有改动 (只改了 tpl source) 时: 不给 seed 的命令. 模板产物没有变化时属于 "不发布" (08 的 Bump Rules), 给出提交 tpl repo 的命令即可.

## Boundaries

- 不手工编辑 artifact, 只通过 `apply-template` 更新.
- 不执行任何 git 写操作, 见 04.
