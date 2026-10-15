# Versioning and Release

本文定义 tpl 的版本号规则, Release Prep 阶段的具体做法, 以及 Publish 做什么. 前置阅读: `01-background-and-concepts.md`, `02-repo-layout.md`, `04-safety-rules.md`, `05-workflow.md`, `07-mise-task-contract.md`.


## Version Number

- tpl 版本号只保存在 tpl repo 的 `pyproject.toml` 一处, 使用 `major.minor.patch` 格式. 其他用到它的地方 (`cookiecutter.json` 的 `_template_version`, `README.rst`) 都由 `sync` 从这里生成, 不手工同步.
- tpl 版本号与 seed 版本号无关 (见 `01-background-and-concepts.md`). 判断 bump 级别时, 不参考 seed 版本号的变化.
- tag, GitHub release 名称, `release-history.rst` 中的版本条目都使用 tpl 版本号.


## Bump Rules

站在 **模板使用者** 的角度判断: 一个人用新版本模板生成项目, 和用旧版本相比有什么不同. 已经生成的项目不受影响 (cookiecutter 是一次性生成), 所以不以它们为判断依据.

| 级别 | 判定 | 例子 |
| :--- | :--- | :--- |
| major | 使用者的输入方式不兼容: 已有的调用方式, 配置, preset 可能失效; 或生成项目的核心工具链被替换 | 重命名或删除一个变量, 改变某个变量的含义, 更换包管理器 |
| minor | 向后兼容地增加能力 | 新增一个带默认值的变量, 生成项目新增一个 task, 文档章节, CI 步骤, skill |
| patch | 修复与小幅调整, 生成项目的能力不变 | 修复参数化错误, 修正文档措辞, 升级依赖版本, 调整默认值 |
| 不发布 | 模板产物 (`cookiecutter.json`, template dir) 没有变化 | 只改了 cctpl 文档, `.mise/tasks/`, `README.rst.jinja` (因而只有 `README.rst` 变化), tpl repo 自身配置 |

一次发布包含多种改动时, 取最高级别. "不发布" 的改动照常由人 commit, 但不 bump 版本, 不创建 release.


## Release Prep

Release Prep 是 `05-workflow.md` 的阶段 6, 由 `cctpl-release-cn` 执行. 按以下顺序:

### 1. 前置检查

全部满足才继续, 任何一项不满足就停下并说明:

- seed 工作区干净, 当前 commit 已 push 到远端.
- tpl repo 的 artifact 是最新的. 判断方法: 运行 `mise run sync`, 如果它在 artifact 上产生了新的 diff, 说明之前的 artifact 不是最新的. 此时停下, 先让人 review 这份新的 diff.
- tpl repo 中有待发布的模板产物变化 (否则属于 "不发布").
- 上一次发布已经完成. 如果 `pyproject.toml` 中的版本号已经有 `release-history.rst` 条目, 但远端没有同名 tag 或 GitHub release, 说明上一次 Publish 中途失败了. 此时不 bump 版本号: 先查清失败原因, 修好后重新执行 Publish.

### 2. 确定版本号

- 汇总本次改动: tpl repo 自上一个 tag 以来的变化, 以及 seed 自上一次发布记录的 seed commit (见下文) 以来的变化.
- 按 Bump Rules 给出建议的级别和新版本号, 附上理由 (哪些改动决定了这个级别).
- 由人确认后, 修改 `pyproject.toml`.
- 然后 **重新运行 `sync`**. 版本号会出现在两个 artifact 中: `cookiecutter.json` 的私有变量 `_template_version`, 以及 `README.rst` 中的版本示例. 只改 `pyproject.toml` 而不重新 Sync, 发布出去的这两处都还是旧版本号.

### 3. 更新 changelog

- 用 `/py-changelog` 更新 tpl repo 的 `release-history.rst`. 它以 tpl repo 的上一个 tag 为基线, 以 `pyproject.toml` 中的版本为目标.
- changelog 写给模板使用者看: 描述 "用新模板生成的项目有什么不同", 而不是 "改了哪些文件". seed 中的改动是 changelog 的主要来源, 因为模板内容都来自 seed.
- 在当前版本条目中记录 seed commit (见下文).

### 4. 打印发布命令

按 `04-safety-rules.md` 的格式, 打印 Publish 阶段需要人执行的全部命令. 执行完成后, 下一步是 Verify (`/cctpl-verify-cn`).


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

Publish 是阶段 7, 由人在 `main` 分支上运行 `publish-template` 完成 (契约见 `07-mise-task-contract.md`):

1. commit tpl repo 的全部改动, push `main`.
2. 按 `presets/*.json` 从 `main` 重新生成每个 `preset/*` 分支并覆盖推送 (方式见 `02-repo-layout.md` 的 Preset Branches).
3. 切回 `main`.
4. 报告远端存在, 但已经没有对应 `presets/*.json` 的 `preset/*` 分支, 由人决定是否删除.
5. 在 `main` 的最新 commit 上, 以 tpl 版本号创建或更新 tag 和 GitHub release.

preset 分支不打 tag. 原因: preset 分支每次发布都会被重写, 打在它上面的 tag 下一次发布后就指向一个不在任何分支上的 commit. 需要某个版本的 preset 时, 用 `main` 上的 tag 加上当时的 `presets/<name>.json` 即可还原.
