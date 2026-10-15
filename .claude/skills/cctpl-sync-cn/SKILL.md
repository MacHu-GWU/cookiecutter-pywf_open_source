---
name: cctpl-sync-cn
description: "Regenerate the cookiecutter template from the seed repo, run all template checks (seed value residue, generation, unresolved placeholders, round trip, presets), apply the artifacts, and fix parameterization problems. Use after the seed or the parameterization changed, or when the user asks to sync, rebuild, or check the template (同步模板, 重新生成模板, make template, 检查模板, 跑一下 sync)."
---
从 seed 重新生成模板, 跑完所有检查, 把 artifact 应用到 tpl repo; 检查失败时诊断并修复参数化问题. 对应 `03-workflow.md` 的阶段 3.

Read ../cctpl-base-cn/SKILL.md, then:

- ../cctpl-base-cn/references/02-repo-layout.md
- ../cctpl-base-cn/references/04-mise-task-contract.md
- ../cctpl-base-cn/references/05-parameterization.md
- ../cctpl-base-cn/references/06-safety-rules.md
- ../cctpl-base-cn/references/08-verification.md
- ../cctpl-base-cn/references/09-troubleshooting.md

Follow those docs to do the work.

## Steps

1. **前置检查.** `CCTPL_SEED_DIR` 已设置且目录存在. 不满足就停下说明.
2. **运行 `sync`.** 从 tpl repo 根目录运行 `mise run sync`.
3. **失败时修复.** 找出最早失败的那一层, 按 09 判断问题在哪一侧:
   - 参数化问题: 修参数化脚本 (或 `hooks/`, `presets/`), 重新运行 `sync`.
   - seed 内容问题: 停下, 告诉用户需要回到 Change 阶段, 并说明原因. 不在这里改 seed 内容.
   - 同一个失败修了 3 次仍未解决: 停下, 报告已尝试的修法和当前的输出.
4. **按需运行 L4.** 按 08 的 "Levels by Change" 判断本次改动是否需要 `test-output` 和 choice coverage; 需要就运行, 失败按第 3 步处理.
5. **展示 artifact 变化.** 用 `git diff --stat` 展示 `cookiecutter.json` 和 template dir 的变化, 并用一两句话说明这些变化是否符合本次改动的预期. 出现预期之外的变化时明确指出.

## Output

结束时停下, 输出:

- 每一层的结果 (L1 – L3, 以及是否运行了 L4).
- 为修复问题而改过的参数化相关文件.
- artifact 的 diff 摘要.
- 下一步: 请用户 review artifact 的 diff. review 通过后, 按 06 的 Handoff Format 给出提交并 push seed 的命令 (commit message 由你起草), 并说明之后运行 `/cctpl-release-cn`.

seed 没有改动 (只改了 tpl source) 时, 不给出 seed 的提交命令.

## Migration Note

base 的 Implementation Status 中列出的 task 尚未全部实现时 (例如还没有 `sync`, `check-roundtrip`), 逐个运行现有的等价 task, 并在输出中列出缺失的 task. 1.0 的 `check-seed-values` 不以退出码表达失败, 此时需要读取它的输出判断.

## Boundaries

- 不手工编辑 artifact, 只通过 `apply-template` 更新.
- 不执行任何 git 写操作, 见 06.
