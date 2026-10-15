---
name: cctpl-change-cn
description: "Apply a change request to the cookiecutter template: classify it, implement it in the seed repo or the tpl repo source, run the seed's own tests, then sync the template. Use when the user wants to add, change, or remove something in the template or its generated projects (改模板, 模板里加一个 X, 给生成的项目加 Y, update the template, change the cookiecutter template, edit the seed repo)."
---
把一个模板改动需求落地: 归类, 在正确的仓库中实施, 跑 seed 自测, 然后同步到模板. 对应 `03-workflow.md` 的阶段 1, 2, 并接着执行阶段 3.

Read ../cctpl-base-cn/SKILL.md, then:

- ../cctpl-base-cn/references/01-background-and-concepts.md
- ../cctpl-base-cn/references/02-repo-layout.md
- ../cctpl-base-cn/references/03-workflow.md
- ../cctpl-base-cn/references/05-parameterization.md
- ../cctpl-base-cn/references/06-safety-rules.md

Follow those docs to do the work.

## Steps

1. **归类.** 按 01 的 "Two Kinds of Change" 判断: template content (改 seed), template mechanism (改 tpl source), 还是两者都有. 涉及新增或修改 parameter 时, 改用 `cctpl-add-param-cn`. 需求被表述为 "改 template dir 中的某个文件" 时, 翻译成 seed 中的对应文件.
2. **说明计划.** 改动跨两个仓库, 或要删除文件时, 先用几行说明打算改哪些文件, 等用户确认. 只改一两个文件的简单改动直接做.
3. **实施.** seed 的位置从 tpl repo `mise.toml` 的 `CCTPL_SEED_DIR` 读取. 只改 seed 和 tpl source, 不碰 artifact. 新增文件时, 按 05 的 File Filtering 判断它在模板中的命运.
4. **seed 自测.** 改了 seed 时, 在 seed 中运行它自己的测试; 改动涉及文档时也构建文档. 只运行本地 task. 失败就在 seed 中修复, 直到通过. 只改了 mechanism 时跳过.
5. **同步.** 在同一会话中接着执行 `cctpl-sync-cn`, 不需要再问用户.

## Output

`cctpl-sync-cn` 结束后, 给出一份总结:

- 本次改动的归类.
- 两个仓库中各改了哪些文件 (删除的文件单独列出).
- seed 自测和 Sync 的结果.
- 下一步: 由用户 review artifact 的 diff, 然后提交 seed (命令由 `cctpl-sync-cn` 按 06 的格式给出).

## Boundaries

- 不执行任何 git 写操作, 见 06.
- 需求含糊, 无法归类时, 先问用户, 不要猜.
