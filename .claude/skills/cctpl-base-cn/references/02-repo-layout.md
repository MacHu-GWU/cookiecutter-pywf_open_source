# Repo Layout

本文定义 tpl repo 和 seed repo 各自必须有什么, 每个部分由谁维护, 以及每类具体值放在哪里. 前置阅读: `01-background-and-concepts.md`.


## tpl repo

```text
cookiecutter-<name>/
├── mise.toml                              # 工具版本, env (含 CCTPL_SEED_DIR), task 定义
├── .mise/tasks/                           # 自动化脚本 (参数化, 检查, 试用, 发布)
├── hooks/                                 # cookiecutter hooks, 手工维护的源头
├── presets/<name>.json                    # 每个 preset 的覆盖值, 发布时用来生成 preset/<name> 分支 (见下文 Preset Branches)
├── cookiecutter.json                      # 发布产物, 由参数化生成
├── {{ cookiecutter.package_name }}-project/   # 发布产物 (template dir), 由参数化生成
├── pyproject.toml                         # tpl 版本号所在
├── release-history.rst                    # tpl 的 changelog
├── README.rst                             # 生成产物, 从 .mise/tasks/cctpl/README.rst.jinja 渲染
├── CLAUDE.md                              # agent 的入口: 只指向本家族, 不重复规则
├── tmp/                                   # gitignored. 只有 tmp/cctpl/ 属于构建流程, 其余归人自由使用
│   └── cctpl/                             # workspace, 构建流程专属, 随时可能被清空
│       ├── stage/                         # 参数化的输入: seed 中 git 认可的文件的副本
│       ├── template/                      # 参数化的输出: 一个完整的 cookiecutter 模板根目录
│       │   ├── cookiecutter.json
│       │   ├── hooks/
│       │   └── {{ cookiecutter.package_name }}-project/
│       ├── output/                        # 用 template/ 生成的测试项目 (默认值一个, choices/ 下每个额外可选值一个)
│       ├── roundtrip/                     # 用 seed 自己的值重新渲染 template/ 得到的项目, 用来和 seed 比较
│       ├── try/                           # 本地试用: 生成的项目和日志, 默认值或每个 preset 一个子目录
│       └── verify/                        # 发布后从 GitHub 拉取已发布模板生成的项目
└── .claude/
    ├── settings.json                      # 权限: deny 规则 (拦截 git 写操作和发布), additionalDirectories (允许访问 seed)
    ├── skills/cctpl-*-cn/                 # 本家族
    └── tmp/                               # 设计笔记, 决策记录; 不属于 workspace, 构建流程不会碰它
```

### 三类文件

tpl repo 中的每个文件都属于以下三类之一. 改动前先判断类别.

| 类别 | 成员 | 规则 |
| :--- | :--- | :--- |
| source (手工维护) | `mise.toml`, `.mise/tasks/`, `hooks/`, `presets/`, `pyproject.toml`, `release-history.rst`, `CLAUDE.md`, `.claude/` | 可以直接编辑 |
| artifact (生成产物) | `cookiecutter.json`, template dir, `README.rst` | **不手改**. `cookiecutter.json` 和 template dir 只能由 seed + 参数化逻辑重新生成, 再由应用步骤 (`apply-template`) 从 `tmp/cctpl/template/` 拷贝过来; `README.rst` 由同一步骤从 `.mise/tasks/cctpl/README.rst.jinja` 渲染, 要改说明文字就改这个模板文件 |
| workspace (工作区) | `tmp/cctpl/` | 随时可能被清空, 不存放任何需要保留的东西 |

artifact 中, `cookiecutter.json` 和 template dir 合称 **模板产物**: cookiecutter 使用者拿到的就是它们. `README.rst` 只是仓库的说明页, 不影响生成的项目.

模板产物必须 **两者一起** 更新. 只更新其中一个会导致不一致: 例如 template dir 中新增了一个需要原样拷贝 (no_render, 不经 Jinja 渲染) 的文件, 但 `cookiecutter.json` 的 `_copy_without_render` 没有同步, 生成项目时这个文件会被当作 Jinja 模板渲染.

`hooks/` 是 source: 参数化时它被拷贝到 `tmp/cctpl/template/hooks/` 供测试使用, 但真正维护的位置是 tpl repo 根目录的 `hooks/`.

### workspace 规则

- 构建流程只读写 `tmp/cctpl/`, 绝不清空或改动 `tmp/` 下的其他内容. `tmp/` 下的其他位置可以放任何临时东西, 例如草稿, 对比用的副本, 调试输出.
- `tmp/cctpl/` 下的每个子目录只属于一个步骤. 每个步骤开始时只清空自己的子目录, 不碰其他子目录. 这样重新生成模板不会顺带删掉上一次发布后验证的结果.


## seed repo

seed repo 就是一个普通的, 由本模板 (或其前身) 生成的项目. 它的全部内容都是 template content, 本家族不规定其内部结构.

本家族只对 seed 提出以下约束:

- **不放任何维护逻辑.** 不放 `cctpl-*-cn`, 不放维护用的 settings, 不放参数化脚本. seed 的 `.claude/` 会进入模板.
- **不维护 changelog, 不打 tag.** seed 的 `release-history.rst` 是 template content (生成项目的 changelog 起点), 不记录 seed 自己的迭代. 原因: seed 的版本号只用来测试发布流程, 不代表模板的版本 (见 01 的 Two Independent Versions); 模板的迭代历史记在 tpl repo.
- **seed value 必须足够独特.** 每个 seed value 在 seed 中只应出现在 "需要被参数化" 的位置. 如果某个 seed value 恰好也出现在无关位置 (例如版本号字符串碰巧等于某个依赖的版本), 会被误替换. 包名, 仓库名这类值靠 `_demo` 命名空间天然独特 (见 01 的 Naming Convention); 版本号, license 这类通用值无法独特, 由参数化规则限定替换范围.
- **不参与模板的文件不从 seed 中删除.** 被 seed 的 `.gitignore` 忽略的文件 (`.venv`, 缓存, 构建产物, 本地私有配置) 天然不进入参数化, 不需要任何处理. 进了 git 但不该进模板的少数文件 (例如由 hooks 重新生成的 `LICENSE.txt`), 由 tpl repo 的参数化脚本排除. seed 需要它们才能作为真实项目运行, 所以不能删.


## Branches

| 仓库 | 分支 | 用途 |
| :--- | :--- | :--- |
| tpl repo | `main` | 面向所有人的模板. 所有开发都在这里 |
| tpl repo | `preset/<name>` | 个人特化. 完全由 `main` + `presets/<name>.json` 派生, 每次发布时重新生成并覆盖推送. 不在上面直接修改 (见下文 Preset Branches) |
| seed repo | `main` | 唯一分支 |

用户通过 `cookiecutter gh:<owner>/<tpl repo> --checkout preset/<name>` 使用某个 preset.


## Preset Branches

### 为什么不用 merge

preset 分支与 `main` 的唯一差异是 `cookiecutter.json` 中的默认值. 1.0 的做法是每次发布时把 `main` merge 进 preset 分支.

在 2.0 中, `cookiecutter.json` 是每次自动生成的 artifact (见上文 "三类文件"). 只要 `main` 上的 `cookiecutter.json` 有任何变化 (新增变量, 修改 prompt, `_copy_without_render` 变化), merge 进 preset 分支时就会和 preset 修改过的默认值冲突, 而且每个 preset 都要手工解决一次. 所以 preset 分支改为从 `main` 派生.

### 定义

- 每个 preset 在 `main` 上有一个覆盖文件 `presets/<name>.json`, 是 tpl repo 的 source.
- 文件内容是一个扁平的对象: 变量名 → 该 preset 希望的默认值. 只列出与 `main` 默认值不同的变量.
- 对于 choice 变量, 覆盖值是其中一个可选值. 生成 preset 分支时, 这个值被移到列表第一位 (cookiecutter 把第一个可选值当作默认值), 其余可选值保持原有顺序.
- 覆盖文件引用的变量必须存在于 `main` 的 `cookiecutter.json` 中, choice 覆盖值必须合法. 每次重新生成模板后, 检查步骤 `check-presets` 都会验证这两点, 不必等到发布时才发现.

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


## Where Facts Live

本家族的文档不写任何具体值, 只规定具体值放在哪里. 需要某个值时, 去对应位置读取.

"fork 时" 一列说明: 用 `cctpl-fork-cn` 把本家族复制到另一对仓库时, 这项事实怎么处理. **改写** 指换成目标仓库对的值; **沿用目标** 指保留目标仓库已有的值. 本表之外的 cctpl 文件 (`.claude/skills/` 下的 skill, `.mise/tasks/` 中的其余代码, `mise.toml` 中 cctpl 的 task, deny 规则) 对任何仓库对都适用, fork 时逐字拷贝.

| 事实 | 位置 | fork 时 |
| :--- | :--- | :--- |
| seed repo 的本地路径 | tpl repo `mise.toml` 的 `[env] CCTPL_SEED_DIR` | 改写 |
| 同上, 供 Claude Code 访问 | tpl repo `.claude/settings.json` 的 `permissions.additionalDirectories`, 写成相对 tpl repo 根目录的路径 (例如 `../<seed repo>`). **必须与 `CCTPL_SEED_DIR` 指向同一目录** | 改写 |
| seed values, parameters, 以及参数化的各类声明 (exclude, no_render, hooks 产物, 需要逐个可选值测试的变量, 独特值, 允许原样保留的位置) | tpl repo 的参数化脚本 `.mise/tasks/make_template.py` 中的模块级常量. 该文件的其余部分 (生成模板的流程) 是通用的 | 改写声明部分 |
| GitHub owner 和 tpl repo 名, template dir 的名字, 生成项目用哪个变量决定 Python 版本, 生成项目的安装和测试命令, 本地试用运行哪些 task | `.mise/tasks/cctpl/pair.py`. 通用代码只从这里读取这些值 | 改写 |
| 对 cookiecutter 输入的额外校验 (例如只接受受支持的 Python 版本) | `hooks/pre_gen_project.py` | 沿用目标, 按需新增 |
| hooks 生成的内容 (例如 license 文件) | `hooks/post_gen_project.py` | 沿用目标, 按需新增 |
| tpl repo `README.rst` 的说明文字 | `.mise/tasks/cctpl/README.rst.jinja`. 其中 Overview 和 Disclaimer 两节与仓库对相关, 其余是通用的 | 改写这两节 |
| 这对仓库的当前状态 (未完成的事项) | tpl repo `CLAUDE.md` 的 Current Status 一节 | 清空 |
| tpl 版本号 | tpl repo `pyproject.toml`. make-template 把它写入 `cookiecutter.json` 的私有变量 `_template_version`, apply-template 把它写入 `README.rst` | 沿用目标 |
| tpl 的 changelog | tpl repo `release-history.rst` | 沿用目标 |
| seed 版本号 | seed repo `pyproject.toml` (与 tpl 无关) | 不涉及 |
| 有哪些 preset, 各自覆盖了什么 | tpl repo `main` 上的 `presets/*.json` | 改写 (目标是 1.0 仓库时, 由它的 preset 分支生成) |
| 可用的 mise task | tpl repo `mise.toml`, 或运行 `mise tasks ls` | cctpl 的 task 逐字拷贝 |
