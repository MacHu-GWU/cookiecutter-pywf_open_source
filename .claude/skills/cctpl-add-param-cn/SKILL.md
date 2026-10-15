---
name: cctpl-add-param-cn
description: "Add, change, rename, or remove a cookiecutter variable (parameter) in the template, updating the seed repo, the parameterization script, hooks, and presets together, then sync. Use when the user wants a new prompt or option in cookiecutter.json or to change an existing one (加一个模板变量, 加参数, 新增 cookiecutter 选项, 改默认值, 重命名变量, add a cookiecutter parameter)."
argument-hint: "[variable name and purpose]"
---
新增, 修改, 重命名或删除一个 cookiecutter 变量, 让 seed, 参数化脚本, hooks, presets 一起保持一致, 然后同步模板.

Read ../cctpl-base-cn/SKILL.md, then:

- ../cctpl-base-cn/references/01-background-and-concepts.md
- ../cctpl-base-cn/references/02-repo-layout.md
- ../cctpl-base-cn/references/03-parameterization.md
- ../cctpl-base-cn/references/04-safety-rules.md
- ../cctpl-base-cn/references/06-verification.md
- ../cctpl-base-cn/references/07-mise-task-contract.md
- ../cctpl-base-cn/references/08-versioning-and-release.md

Follow those docs to do the work.

## Steps

1. **收集定义.** 确认以下内容, 缺的向用户询问, 一次问完:
   - 变量名 (snake case), 含义.
   - 默认值, 或可选值列表 (第一个是默认值).
   - prompt 文字.
   - 它在生成的项目中出现在哪里, 以什么形态出现 (是否有 slug 等派生形态).
2. **检查冲突.** 变量名不能与 `cookiecutter.json` 中已有的变量重复. 修改, 重命名, 删除时, 找出所有引用它的地方: 参数化脚本, hooks, `presets/*.json`, seed 中的 seed value.
3. **准备 seed value.** 在 seed 中, 让这个变量的值以具体, 独特的形式出现在需要的位置 (03 的 Choosing Seed Values). 通用值必须规划 context 或 file scope.
4. **定义 parameter.** 在参数化脚本中添加或修改 parameter, 包括派生形态. 同一变量多处 context 时, 只让一个写入 `cookiecutter.json`.
5. **处理关联.** 需要时修改 hooks; 重命名或删除时同步修改 `presets/*.json`; 需要时声明合法残留.
6. **同步.** 执行 `cctpl-sync-cn`. 本次改动按 06 必须运行 L4 和 choice coverage (如果变量有可选值).

## Output

- 变量的最终定义 (名称, 默认值或可选值, prompt).
- 在 seed, 参数化脚本, hooks, presets 中各改了什么.
- 对 tpl 版本号的影响: 新增变量是 minor; 重命名, 删除, 或改变含义是 **major**, 明确提醒用户.
- 其余同 `cctpl-sync-cn` 的输出.

## Boundaries

- 不手工编辑 `cookiecutter.json`, 它由参数化脚本生成.
- 不执行任何 git 写操作, 见 04.
