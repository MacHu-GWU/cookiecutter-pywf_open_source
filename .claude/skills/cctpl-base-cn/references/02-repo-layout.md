# Repo Layout

本文定义 tpl repo 和 seed repo 各自必须有什么, 每个部分由谁维护, 以及每类具体值放在哪里. 前置阅读: `01-background-and-concepts.md`.


## tpl repo

```text
cookiecutter-<name>/
├── mise.toml                              # 工具版本, env (含 CCTPL_SEED_DIR), task 定义
├── .mise/tasks/                           # 自动化脚本, 契约见 04-mise-task-contract.md
├── hooks/                                 # cookiecutter hooks, 手工维护的源头
├── cookiecutter.json                      # 发布产物, 由参数化生成
├── {{ cookiecutter.package_name }}-project/   # 发布产物 (template dir), 由参数化生成
├── pyproject.toml                         # tpl 版本号所在
├── release-history.rst                    # tpl 的 changelog
├── <python package>/                      # tpl repo 自身的辅助代码 (路径定义等)
├── tmp/                                   # gitignored. 只有 tmp/cctpl/ 属于构建流程, 其余归人自由使用
│   └── cctpl/                             # workspace, 构建流程专属, 随时可能被清空
│       ├── template/                      # make-template 的输出: 一个完整的 cookiecutter 模板根目录
│       │   ├── cookiecutter.json
│       │   ├── hooks/
│       │   └── {{ cookiecutter.package_name }}-project/
│       ├── output/                        # test-template 用 template/ 生成的测试项目
│       ├── roundtrip/                     # check-roundtrip 用 seed values 渲染的项目
│       └── verify/                        # Verify 阶段从 GitHub 拉取已发布模板生成的项目
└── .claude/
    ├── settings.json                      # deny 规则, additionalDirectories (见 06-safety-rules.md)
    ├── skills/cctpl-*-cn/                 # 本家族
    └── tmp/                               # 设计笔记, 决策记录; 不会被 make-template 清空
```

### 三类文件

tpl repo 中的每个文件都属于以下三类之一. 改动前先判断类别.

| 类别 | 成员 | 规则 |
| :--- | :--- | :--- |
| source (手工维护) | `mise.toml`, `.mise/tasks/`, `hooks/`, `pyproject.toml`, `release-history.rst`, `.claude/` | 可以直接编辑 |
| artifact (生成产物) | `cookiecutter.json`, template dir | **不手改**. 只能由 seed + 参数化逻辑重新生成, 再由 apply-template 从 `tmp/cctpl/template/` 拷贝过来 |
| workspace (工作区) | `tmp/cctpl/` | 随时可能被清空, 不存放任何需要保留的东西 |

发布产物是 `cookiecutter.json` 和 template dir **两者一起**. 只更新其中一个会导致不一致: 例如 template dir 中新增了 `uv.lock`, 但 `cookiecutter.json` 的 `_copy_without_render` 没有同步, 生成项目时 `uv.lock` 会被当作 Jinja 模板渲染.

`hooks/` 是 source: make-template 把它拷贝到 `tmp/cctpl/template/hooks/` 供测试使用, 但真正维护的位置是 tpl repo 根目录的 `hooks/`.

### workspace 规则

- 构建流程只读写 `tmp/cctpl/`, 绝不清空或改动 `tmp/` 下的其他内容. `tmp/` 下的其他位置可以放任何临时东西, 例如草稿, 对比用的副本, 调试输出.
- `tmp/cctpl/` 下的每个子目录只属于一个阶段. 每个阶段开始时只清空自己的子目录: make-template 清空 `template/`, test-template 清空 `output/`, check-roundtrip 清空 `roundtrip/`, Verify 清空 `verify/`. 这样重新生成模板不会顺带删掉上一次的 Verify 结果.


## seed repo

seed repo 就是一个普通的, 由本模板 (或其前身) 生成的项目. 它的全部内容都是 template content, 本家族不规定其内部结构.

本家族只对 seed 提出以下约束:

- **不放任何维护逻辑.** 不放 `cctpl-*-cn`, 不放维护用的 settings, 不放参数化脚本. seed 的 `.claude/` 会进入模板.
- **不维护 changelog, 不打 tag.** seed 的 `release-history.rst` 是 template content (生成项目的 changelog 起点), 不记录 seed 自己的迭代.
- **seed value 必须足够独特.** 每个 seed value 在 seed 中只应出现在 "需要被参数化" 的位置. 如果某个 seed value 恰好也出现在无关位置 (例如版本号字符串碰巧等于某个依赖的版本), 会被误替换. 详见 `05-parameterization.md`.
- **不参与模板的文件**由 tpl repo 的参数化配置中的 exclude 规则排除 (例如 `.git`, `.venv`, 构建产物, `.claude/settings.local.json`), 而不是从 seed 中删除.


## Branches

| 仓库 | 分支 | 用途 |
| :--- | :--- | :--- |
| tpl repo | `main` | 面向所有人的模板. 所有开发都在这里 |
| tpl repo | `preset/<name>` | 个人特化. 与 `main` 的差异只应在 `cookiecutter.json` 的默认值. 发布时由 `main` merge 进来, 不在上面直接开发 |
| seed repo | `main` | 唯一分支 |

用户通过 `cookiecutter gh:<owner>/<tpl repo> --checkout preset/<name>` 使用某个 preset.


## Where Facts Live

本家族的文档不写任何具体值, 只规定具体值放在哪里. 需要某个值时, 去对应位置读取.

| 事实 | 位置 |
| :--- | :--- |
| seed repo 的本地路径 | tpl repo `mise.toml` 的 `[env] CCTPL_SEED_DIR` |
| 同上, 供 Claude Code 访问 | tpl repo `.claude/settings.json` 的 `permissions.additionalDirectories`. **必须与 `CCTPL_SEED_DIR` 指向同一目录** |
| seed values 和 parameters | tpl repo `.mise/tasks/` 中的参数化脚本 (`make_template.py`) |
| exclude / no_render 规则 | 同上 |
| tpl 版本号 | tpl repo `pyproject.toml` |
| seed 版本号 | seed repo `pyproject.toml` (与 tpl 无关) |
| GitHub owner 和 tpl repo 名 | tpl repo 的发布脚本 |
| 有哪些 preset | tpl repo 中所有 `preset/*` 分支 |
| 可用的 mise task | tpl repo `mise.toml`, 或运行 `mise tasks ls` |
