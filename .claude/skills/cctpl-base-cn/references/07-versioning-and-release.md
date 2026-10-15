# Versioning and Release

本文定义 tpl 的版本号规则, Release Prep 阶段的具体做法, 以及 preset 分支如何跟随 `main`. 前置阅读: `01-background-and-concepts.md`, `03-workflow.md`, `06-safety-rules.md`.


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
2. 把 `main` 的变化带到每个 `preset/*` 分支并 push (方式见下一节).
3. 切回 `main`.
4. 在 `main` 的最新 commit 上, 以 tpl 版本号创建或更新 tag 和 GitHub release. preset 分支不打 tag.


## Preset Branches

> **待确认.** 本节描述的方案尚未与人确认, 确认前保持 1.0 的做法 (`main` merge 进每个 preset 分支).

### 问题

preset 分支与 `main` 的唯一差异是 `cookiecutter.json` 中的默认值. 1.0 的做法是每次发布时把 `main` merge 进 preset 分支.

但在 2.0 中, `cookiecutter.json` 是每次自动生成的 artifact (见 `02-repo-layout.md`). 只要 `main` 上的 `cookiecutter.json` 有任何变化 (新增变量, 修改 prompt, `_copy_without_render` 变化), merge 进 preset 分支时就会和 preset 修改过的默认值冲突. 冲突需要人手工解决, 而且每个 preset 都要解决一次.

### 方案: 从 `main` 派生 preset 分支

- 在 `main` 上保存每个 preset 的覆盖值, 例如 `presets/<name>.json`, 只列出与默认值不同的变量.
- 发布时, 每个 preset 分支都 **重新生成**: 从 `main` 的最新 commit 出发, 把覆盖值写入 `cookiecutter.json`, 提交, 覆盖推送到 `preset/<name>`.
- preset 分支不再接受直接修改, 它完全由 `main` + 覆盖值决定.

效果:

- 不会再有 merge 冲突.
- 新增变量时, preset 自动继承 `main` 的默认值; 只有需要不同默认值时才修改覆盖文件.
- 所有 preset 的内容都在 `main` 上可见, 新增或修改 preset 只需要改 `main` 上的一个文件.

代价:

- preset 分支的历史会被覆盖推送重写. 使用者通过 `--checkout preset/<name>` 拉取的始终是最新状态, 不受影响; 但不能在 preset 分支上保留独立的提交.
