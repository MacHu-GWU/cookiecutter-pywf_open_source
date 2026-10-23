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
   - 每个 preset 是否需要不同的默认值 (列出 `presets/*.json` 让用户逐个确认; 不需要的 preset 自动继承新默认值).
2. **检查冲突.** 变量名不能与 `cookiecutter.json` 中已有的变量重复. 修改, 重命名, 删除时, 找出所有引用它的地方: 参数化脚本, hooks, `presets/*.json`, seed 中的 seed value.
3. **准备 seed value.** 在 seed 中, 让这个变量的值以具体, 独特的形式出现在需要的位置 (03 的 Choosing Seed Values). 通用值必须规划 context 或 file scope.
4. **定义 parameter.** 在参数化脚本中添加或修改 parameter, 包括派生形态. 同一变量多处 context 时, 只让一个写入 `cookiecutter.json`. 在 `SeedValues` 中加入与 parameter `name` **同名** 的属性, 否则 round trip 无法运行 (03 的 Round Trip).
5. **逐项检查声明.** 按 03 的 Declarations 表逐行判断: 独特的值加入 `UNIQUE_SEED_VALUES`; 影响 hooks 或模板分支的 choice 变量加入 `CHOICE_COVERAGE`; 需要保留原值的位置在 `LEGAL_RESIDUES` 中声明. 重命名或删除时, 同时删改这些声明中的旧名字.
6. **处理关联.** 需要时修改 hooks; 按第 1 步的结论修改 `presets/*.json` (重命名或删除时必须同步修改, 否则 `check-presets` 失败). `README.rst` 中的 prompt 列表由 `sync` 自动更新, 不用手改.
7. **同步.** 执行 `cctpl-sync-cn`. 本次改动按 06 的 Levels by Change 必须运行 L4.

## Output

- 变量的最终定义 (名称, 默认值或可选值, prompt).
- 在 seed, 参数化脚本, hooks, presets 中各改了什么.
- 对共用版本号的影响 (按 08 的 Bump Rules; 版本号在 seed 中 bump). 结果是 major 时明确提醒用户.
- 其余同 `cctpl-sync-cn` 的输出, 合在同一份报告中, 不分两次输出.

## Boundaries

- 不手工编辑 `cookiecutter.json`, 它由参数化脚本生成.
- 不执行任何 git 写操作, 见 04.
