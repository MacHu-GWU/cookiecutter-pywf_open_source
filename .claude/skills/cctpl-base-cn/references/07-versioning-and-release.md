# Versioning and Release

本文定义 tpl 的版本号规则, Release Prep 阶段的具体做法, 以及 preset 分支如何从 `main` 派生. 前置阅读: `01-background-and-concepts.md`, `03-workflow.md`, `06-safety-rules.md`.


## Version Number

- tpl 版本号保存在 tpl repo 的 `pyproject.toml` 中, 使用 `major.minor.patch` 格式. 如果 `pyproject.toml` 注释中指出还有其他位置需要同步, 一并修改.
- tpl 版本号与 seed 版本号无关 (见 `01-background-and-concepts.md`). 判断 bump 级别时, 不参考 seed 版本号的变化.
- tag, GitHub release 名称, `release-history.rst` 中的版本条目都使用 tpl 版本号.


## Bump Rules

站在 **模板使用者** 的角度判断: 一个人用新版本模板生成项目, 和用旧版本相比有什么不同. 已经生成的项目不受影响 (cookiecutter 是一次性生成), 所以不以它们为判断依据.

| 级别 | 判定 | 例子 |
| :--- | :--- | :--- |
| major | 使用者的输入方式不兼容: 已有的调用方式, 配置, preset 可能失效; 或生成项目的核心工具链被替换 | 重命名或删除一个变量, 改变某个变量的含义, 更换包管理器 |
| minor | 向后兼容地增加能力 | 新增一个带默认值的变量, 生成项目新增一个 task, 文档章节, CI 步骤, skill |
| patch | 修复与小幅调整, 生成项目的能力不变 | 修复参数化错误, 修正文档措辞, 升级依赖版本, 调整默认值 |
| 不发布 | artifact (`cookiecutter.json`, template dir) 没有变化 | 只改了 cctpl 文档, `.mise/tasks/`, tpl repo 自身配置 |

一次发布包含多种改动时, 取最高级别. "不发布" 的改动照常由人 commit, 但不 bump 版本, 不创建 release.


## Release Prep

Release Prep 是 `03-workflow.md` 的阶段 6, 由 `cctpl-release-cn` 执行. 按以下顺序:

### 1. 前置检查

全部满足才继续, 任何一项不满足就停下并说明:

- seed 工作区干净, 当前 commit 已 push 到远端.
- tpl repo 的 artifact 是最新的: 当前 seed 状态下重新运行 Sync 不会产生新的 diff.
- tpl repo 中有待发布的 artifact 变化 (否则属于 "不发布").

### 2. 确定版本号

- 汇总本次改动: tpl repo 自上一个 tag 以来的变化, 以及 seed 自上一次发布记录的 seed commit (见下文) 以来的变化.
- 按 Bump Rules 给出建议的级别和新版本号, 附上理由 (哪些改动决定了这个级别).
- 由人确认后, 修改 `pyproject.toml`.

### 3. 更新 changelog

- 用 `/py-changelog` 更新 tpl repo 的 `release-history.rst`. 它以 tpl repo 的上一个 tag 为基线, 以 `pyproject.toml` 中的版本为目标.
- changelog 写给模板使用者看: 描述 "用新模板生成的项目有什么不同", 而不是 "改了哪些文件". seed 中的改动是 changelog 的主要来源, 因为模板内容都来自 seed.
- 在当前版本条目中记录 seed commit (见下文).

### 4. 打印发布命令

按 `06-safety-rules.md` 的格式, 打印 Publish 阶段需要人执行的全部命令. 执行完成后, 下一步是 Verify (`/cctpl-verify-cn`).


## Seed Commit Record

每个 tpl 版本都记录它由哪个 seed commit 生成, 写在 `release-history.rst` 对应版本条目的开头:

```rst
1.1.0 (2026-10-20)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Built from seed @ ``abc1234``

**Features and Improvements**
...
```

作用:

- 出问题时, 能精确找到某个模板版本对应的 seed 状态.
- 下一次 Release Prep 汇总 seed 改动时, 以上一个版本记录的 commit 为起点 (seed 没有 tag, 这是唯一可靠的基线).


## Publish

Publish 是阶段 7, 由人运行 `publish-template` 完成 (契约见 `04-mise-task-contract.md`):

1. commit tpl repo 的全部改动, push `main`.
2. 按 `presets/*.json` 从 `main` 重新生成每个 `preset/*` 分支并覆盖推送 (方式见下一节).
3. 切回 `main`.
4. 在 `main` 的最新 commit 上, 以 tpl 版本号创建或更新 tag 和 GitHub release. preset 分支不打 tag.


## Preset Branches

### 为什么不用 merge

preset 分支与 `main` 的唯一差异是 `cookiecutter.json` 中的默认值. 1.0 的做法是每次发布时把 `main` merge 进 preset 分支.

在 2.0 中, `cookiecutter.json` 是每次自动生成的 artifact (见 `02-repo-layout.md`). 只要 `main` 上的 `cookiecutter.json` 有任何变化 (新增变量, 修改 prompt, `_copy_without_render` 变化), merge 进 preset 分支时就会和 preset 修改过的默认值冲突, 而且每个 preset 都要手工解决一次. 所以 preset 分支改为从 `main` 派生.

### 定义

- 每个 preset 在 `main` 上有一个覆盖文件 `presets/<name>.json`, 是 tpl repo 的 source.
- 文件内容是一个扁平的对象: 变量名 → 该 preset 希望的默认值. 只列出与 `main` 默认值不同的变量.
- 对于 choice 变量, 覆盖值是其中一个可选值. 生成 preset 分支时, 这个值被移到列表第一位 (cookiecutter 把第一个可选值当作默认值), 其余可选值保持原有顺序.
- 覆盖文件引用的变量必须存在于 `main` 的 `cookiecutter.json` 中, choice 覆盖值必须合法. 这由 `check-presets` 在 Sync 阶段检查 (见 `04-mise-task-contract.md`).

### 生成

发布时, 对每个 `presets/<name>.json`:

1. 从 `main` 的最新 commit 出发, 创建或重置 `preset/<name>` 分支.
2. 把覆盖值写入 `cookiecutter.json`, 提交.
3. 覆盖推送到远端的 `preset/<name>`.

preset 分支完全由 `main` + 覆盖文件决定, 不接受直接修改. 想改 preset, 改 `main` 上的覆盖文件. 新增 preset 就是新增一个覆盖文件; 删除 preset 时删除覆盖文件, 远端分支由人手动删除 (发布脚本只报告, 不删除).

### 效果与代价

- 不会再有 merge 冲突.
- 新增变量时, preset 自动继承 `main` 的默认值; 只有需要不同默认值时才改覆盖文件.
- 所有 preset 的内容都在 `main` 上可见, 可以 review.
- 代价: preset 分支的历史每次发布都会被重写. 使用者通过 `--checkout preset/<name>` 拿到的始终是最新状态, 不受影响.
