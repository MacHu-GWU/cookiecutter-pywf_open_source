# Versioning and Release

本文定义共用版本号的规则, 两本 changelog 的格式, Seed Release 和 Release Prep 阶段的具体做法, 以及 Publish 做什么. 前置阅读: `01-background-and-concepts.md`, `02-repo-layout.md`, `04-safety-rules.md`, `05-workflow.md`, `07-mise-task-contract.md`.


## Version Number

- **seed 和 tpl 共用一个版本号, 唯一的源头是 seed 的 `pyproject.toml`**, 使用 `major.minor.patch` 格式 (见 01 的 One Shared Version).
- tpl repo 中的副本 (`pyproject.toml`, `uv.lock`, `cookiecutter.json` 的 `_template_version`, `README.rst`) 全部由 `sync` 写入, 不手工同步, 也不手改.
- 程序在三处把关, 而不是靠人记住:

  | 时机 | Task | 拦下什么 |
  | :--- | :--- | :--- |
  | 每次 Sync | `check-version` | 版本号格式不对, 比 tpl 中的版本号还低, seed changelog 缺少条目, 条目被误写进 seed 的 `release-history.rst`, `SEED_VERSION_PIN_FILES` 中指向 seed tag 的链接还是旧版本 |
  | Release Prep | `check-release` | 版本号四处不一致, artifact 不是最新, seed 未 push 或未打 tag, tpl changelog 条目缺失或开头不对, 版本号已经发布过 |
  | Publish | `publish-template` 先跑 `check-release` 的全部检查 | 同上, 在推送任何东西之前 |

- 两个仓库各打一个同名 tag: seed 的由 seed 自己的发布 task 创建, tpl 的由 `publish-template` 创建. seed 的 tag 同时就是 "模板由哪个 seed commit 生成" 的记录 (见下文 Seed Tag Record). preset 分支不打 tag (见下文 Publish).


## Bump Rules

站在 **模板使用者** 的角度判断: 一个人用新版本模板生成项目, 和用旧版本相比有什么不同. 已经生成的项目不受影响 (cookiecutter 是一次性生成), 所以不以它们为判断依据. seed 中示例包的 public API 没有使用者, 也不作为依据.

| 级别 | 判定 | 例子 |
| :--- | :--- | :--- |
| major | 使用者的输入方式不兼容: 已有的调用方式, 配置, preset 可能失效; 或生成项目的核心工具链被替换 | 重命名或删除一个变量, 改变某个变量的含义, 更换包管理器 |
| minor | 向后兼容地增加能力 | 新增一个带默认值的变量, 生成项目新增一个 task, 文档章节, CI 步骤, skill |
| patch | 修复与小幅调整, 生成项目的能力不变 | 修复参数化错误, 修正文档措辞, 升级依赖版本, 调整默认值 |
| 不发布 | 模板产物 (`cookiecutter.json`, template dir) 没有变化 | 只改了 cctpl 文档, `.mise/tasks/`, `README.rst.jinja` (因而只有 `README.rst` 变化), tpl repo 自身配置 |

一次发布包含多种改动时, 取最高级别. "不发布" 的改动照常由人 commit, 但不 bump 版本, 不创建 release.

**只改了 tpl 机制 (参数化, hooks) 的发布也要在 seed 中 bump.** 版本号只有 seed 一个源头, 所以 seed 照样 bump, seed changelog 的条目只写一句 "seed 无变化, 本版本只改动了 tpl repo".

**已发布的版本号冻结.** 已经有 tag 的版本号 (seed 或 tpl 任一边) 不再发布第二次. 发布出了问题, 修复后发一个新的 patch 版本. 新版本号必须高于两边已有的全部 tag.


## Changelogs

### seed changelog

seed 的 `release-history-seed-repo.rst` (seed-only 文件), 由 seed 的 `pywf-oss-changelog-seed-repo` 维护. 格式与 seed 中普通 Python 库的 changelog 相同 (Backlog 区块, `VERSION (YYYY-MM-DD)` 标题和 78 个 `~` 的下划线, 分类顺序). 条目描述 "新生成的项目得到或失去了什么".

### tpl changelog

tpl 的 `release-history.rst`, 由 `cctpl-changelog-cn` 维护. 每个版本条目的格式是固定的:

```rst
3.0.1 (2026-10-30)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Seed repo changes: `3.0.1 (2026-10-30) <https://github.com/<owner>/<seed repo>/blob/3.0.1/release-history-seed-repo.rst#301-2026-10-30>`__

**Bugfixes**

- (tpl repo 自身的改动: 参数化, hooks, 发布流程, 对模板使用者可见的部分)
```

规则:

- **开头一行是固定的, 由程序检查.** 它链接到 seed changelog 中同版本的条目, 链接指向 seed 的同名 tag (所以不随 seed `main` 的变化而失效). 锚点由 seed 条目的标题生成: 转小写, 去掉字母, 数字, 空格和 `-` 之外的字符, 空格换成 `-` (这是 GitHub 渲染 rst 标题时生成锚点的规则). `check-release` 计算出预期的这一行, 与文件逐字比较, 不一致时打印预期内容.
- 链接用匿名超链接 (结尾 `__`), 避免多个版本条目之间的链接名冲突.
- 标题日期是 tpl 发布的日期, 可以与 seed 条目的日期不同.
- **下面写 tpl repo 自身的改动.** seed 带来的改动已经在 seed changelog 中, 不在这里重复. 如果 tpl repo 本次没有对使用者可见的改动, 只保留开头一行.
- Backlog 区块是维护者的规划区, agent 不改它.

### Seed Tag Record

每个 tpl 版本由哪个 seed commit 生成, 记录在 **seed 的同名 tag** 上, tpl repo 中不再写 commit SHA. 原因: 版本号统一之后, tag `<version>` 在 seed 中唯一地指向一个 commit, 而且 tag 永不移动 (见上文 Bump Rules 的 "已发布的版本号冻结"), 再写一份 SHA 只是重复. `check-release` 保证 seed 工作区干净, tag 指向 seed 的 HEAD, 所以模板确实由 tag 指向的 commit 生成.

作用: 出问题时, 用 `git -C <seed> show <version>` 就能找到某个模板版本对应的 seed 状态; `cctpl-verify-cn` 用它确认本地模板确实由刚发布的 seed 生成. 3.0.0 之前的 tpl 条目中的 `Built from seed @ <sha>` 是旧格式, 保留不改.


## Seed Release

Seed Release 是 `05-workflow.md` 的阶段 5, 在 seed 中完成:

1. **bump 并写 seed changelog.** seed 的 `pywf-oss-changelog-seed-repo` 按上文 Bump Rules 建议级别, 人确认后修改 seed 的 `pyproject.toml` (并更新 seed 的 `uv.lock`), 在 `release-history-seed-repo.rst` 中写条目. seed 中有文件把链接固定在 seed 的版本 tag 上时 (参数化脚本的 `SEED_VERSION_PIN_FILES`), 把其中的 tag 和旁边的版本文字一起改成新版本. seed 的 `release-history.rst` 不动.
2. **重新 Sync.** 在 tpl repo 中运行 `mise run sync` (或 `mise run e2e`), 把新版本号复制到 tpl repo. 人 review artifact 的 diff.
3. **发布 seed.** 人在 seed 中 commit, **先 push**, 然后运行 seed 自己的发布 task: 至少要创建同名 tag 和 GitHub release; seed 发布到 PyPI 时也在这一步. 具体 task 名见 seed 的 `mise.toml`. 没 push 就打 tag, tag 会落在 GitHub 上 `main` 的旧 commit 上, `check-release` 会报 "tag 不在 HEAD 上". agent 只按 `04-safety-rules.md` 的格式打印命令.


## Release Prep

Release Prep 是阶段 6, 由 `cctpl-release-cn` 执行. 按以下顺序:

1. **前置检查.** 运行 `mise run check-release`. 此时 tpl changelog 条目通常还没写, 这一项失败是正常的; 其余任何一项失败都停下并说明. 典型情况:
   - 版本号不一致, artifact 不是最新: 运行 `mise run sync`, 让人 review 新的 diff.
   - seed 未 push, 未打 tag: 打印 Seed Release 第 3 步的命令.
   - tpl 已有这个版本的 tag: 版本号已发布过, 回到 Seed Release 第 1 步 bump.
2. **写 tpl changelog.** 用 `cctpl-changelog-cn` 写当前版本的条目 (格式见上文 tpl changelog).
3. **再次检查.** `mise run check-release` 必须全部通过.
4. **打印发布命令.** 按 `04-safety-rules.md` 的格式, 打印 Publish 阶段需要人执行的命令. 执行完成后, 下一步是 Verify (`/cctpl-verify-cn`).


## Publish

Publish 是阶段 7, 由人在 `main` 分支上运行 `publish-template` 完成 (契约见 `07-mise-task-contract.md`):

1. 运行 `check-release` 的全部检查. 有任何问题就停下, 什么都不推送.
2. commit tpl repo 的全部改动, push `main`.
3. 在刚 push 的 `main` commit 上, 用一次 API 调用同时创建 tag 和 GitHub release, release 说明中附上 tpl changelog 条目的链接.
4. 执行 `publish-presets` 的全部步骤: 按 `presets/*.json` 从已 push 的 `main` 重新生成每个 `preset/*` 分支并覆盖推送 (方式见 `02-repo-layout.md` 的 Preset Branches; 模板部分与 `main` 完全相同, 只有 `cookiecutter.json` 的默认值不同), 切回 `main`, 报告远端多余的 `preset/*` 分支.

**同一个版本只发布一次.** `publish-template` 只创建 tag, 不删除, 不移动. 版本号已有 tag 时, 第 1 步就会失败并停止, 什么都不推送. 想再发一次, 就 bump 一个新版本: 发版是廉价的, 所以要勤发, 不覆盖.

失败后怎么重来:

- 第 3 步失败 (例如 GitHub API 报错): 远端还没有这个 tag, 修好原因后直接重新运行 `publish-template`. 第 2 步可以重复执行, 不会产生副作用.
- 第 4 步失败: tag 和 release 已经创建, 不要再运行 `publish-template` (第 1 步会因为 tag 已存在而失败). 只运行 `mise run publish-presets`.

preset 分支不打 tag. 原因: preset 分支每次发布都会被重写, 打在它上面的 tag 下一次发布后就指向一个不在任何分支上的 commit. 需要某个版本的 preset 时, 用 `main` 上的 tag 加上当时的 `presets/<name>.json` 即可还原.
