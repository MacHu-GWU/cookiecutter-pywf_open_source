---
name: cctpl-changelog-cn
description: "Write the section for the current shared version in the tpl repo's release-history.rst: the fixed opening line (link to the seed changelog section at the seed tag), then the tpl repo's own changes since the last tag, checked by mise run check-release. Use when preparing a template release or when the tpl changelog must be updated. 维护 tpl repo 的 release-history.rst."
---
写 tpl repo `release-history.rst` 中当前版本的条目. 对应 `05-workflow.md` 阶段 6 的 changelog 步骤, 通常由 `/cctpl-release-cn` 调用, 也可以单独使用. 本 skill 只改 tpl 的 `release-history.rst`, 不改版本号, 不碰 seed.

Read ../cctpl-base-cn/SKILL.md, then:

- ../cctpl-base-cn/references/01-background-and-concepts.md
- ../cctpl-base-cn/references/02-repo-layout.md
- ../cctpl-base-cn/references/05-workflow.md
- ../cctpl-base-cn/references/08-versioning-and-release.md

Follow those docs to do the work.

## Steps

1. **确定版本号.** 版本号就是 seed `pyproject.toml` 中的共用版本号 (01 的 One Shared Version). 先运行 `mise run check-version`: 它失败时 (seed 版本号不合法, 或 seed changelog 没有这个版本的条目) 停下, 让用户先在 seed 中用 `pywf-oss-changelog-seed-repo` 处理. 不在 tpl repo 中改版本号.
2. **拿到固定开头.** 运行 `mise run check-release`. 条目还没写或开头不对时, 它会在 `release-history.rst` 那一项打印 **预期的开头一行** (seed 链接). 原样使用这一行, 不手工拼接链接或锚点. 不写 seed commit: seed 的同名 tag 就是记录 (08 的 Seed Tag Record).
3. **收集 tpl repo 自身的改动.** 基线是 tpl repo 的上一个 tag (`git describe --tags --abbrev=0`). 用只读 git 命令查看:

   ```bash
   git log <last_tag>..HEAD --oneline
   git diff <last_tag>..HEAD --stat
   git diff <last_tag>..HEAD -- .mise/tasks hooks presets mise.toml
   git status --short
   ```

   未 commit 的改动也算 (发布时 `publish-template` 会一起 commit). 只记录 **tpl repo 自身** 的改动: 参数化 (parameter, exclude, no_render), hooks, preset, 发布与检查流程, `README.rst` 的说明. seed 带来的改动已经在 seed changelog 中, 不重复. template dir 和 `cookiecutter.json` 的 diff 只用来判断改动是否对模板使用者可见.
4. **写条目.**
   - 条目不存在: 在 Backlog 区块下方插入 `VERSION (YYYY-MM-DD)` (今天的日期) 和 78 个 `~` 的下划线, 紧接第 2 步的那一行和一个空行, 再写各分类. 条目已存在: 按 git 历史修正, 开头一行以第 2 步为准.
   - 分类顺序: **Breaking Changes**, **Features and Improvements**, **Minor Improvements**, **Bugfixes**, **Miscellaneous**. 省略空的分类. 条目写给模板使用者看, 用纯文本, 代码用 rst 行内字面量.
   - tpl repo 本次没有对使用者可见的改动时, 条目只保留开头一行.
   - 不改 Backlog 区块的任何内容.
5. **检查.** 再运行 `mise run check-release`, 确认 `release-history.rst` 那一项不再报错. 其他项 (seed 未 push, 未打 tag 等) 不归本 skill 处理, 只报告.

## Output

结束时给出: 版本号, 写入的条目全文, `check-release` 中仍未通过的项目 (如有) 以及谁来处理.

## Boundaries

- 只改 tpl repo 的 `release-history.rst`. 不改版本号, 不改 seed 中的任何文件, 不执行 git 写操作 (见 04).
- 不手工拼接 seed 链接: 链接和锚点的规则只在 `.mise/tasks/cctpl/__init__.py` 中实现一次, 用 `check-release` 打印的结果.
