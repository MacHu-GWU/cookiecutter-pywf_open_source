# Mise Task Contract

本文定义 tpl repo 中每个 mise task 必须满足的契约: 名称, 读什么, 写什么, 成功与失败的判定, 安全级别. `.mise/tasks/` 的实现以本文为准; 实现与本文不一致时, 修改实现. 前置阅读: `02-repo-layout.md`, `03-workflow.md`.

本文只规定 "做什么" 和 "怎样算成功", 不规定 "怎么实现". 具体实现读 `mise.toml` 和 `.mise/tasks/`.


## Safety Levels

| Level | 含义 |
| :--- | :--- |
| **A** (agent) | agent 可以直接运行. 只读写本地文件, 结果可以用 git 撤回或重新生成 |
| **U** (user only) | agent 绝不运行, 只按 `06-safety-rules.md` 的格式打印命令, 由人执行. 凡是写 git 历史, 或改动远端 (GitHub, PyPI 等) 的 task 都是 U |


## General Rules

所有 task 都必须满足:

- **从 tpl repo 根目录用 `mise run <task>` 运行.** 不依赖当前 shell 所在目录.
- **用退出码表达成败.** 成功返回 0, 失败返回非 0. 检查类 task 发现问题时 **必须** 返回非 0, 不能只打印. agent 依靠退出码判断下一步, 而不是阅读输出.
- **失败时输出可定位.** 指出问题所在的文件 (相对路径) 和行号, 以及修复方向或应该先运行的 task.
- **可重复运行.** 同样的输入重复运行得到同样的结果. 每个 task 开始时只清空自己负责的 `tmp/cctpl/` 子目录, 不碰其他位置 (见 `02-repo-layout.md` 的 workspace 规则).
- **不交互.** A 级 task 不读取 stdin. 只有 U 级 task 可以有确认提示.
- **不写死路径.** seed 位置只从 `CCTPL_SEED_DIR` 读取; tpl repo 内的路径从 repo 根目录推导. 缺少 `CCTPL_SEED_DIR` 或目录不存在时, 立即失败并说明原因.
- **前置条件不满足时立即失败.** 例如 `tmp/cctpl/template/` 不存在时, check 类 task 应失败并提示先运行 `make-template`, 而不是报告 "没有发现问题".


## Build Tasks

按 Sync 阶段的执行顺序排列.

| Task | Level | 读 | 写 | 成功条件 |
| :--- | :--- | :--- | :--- | :--- |
| `make-template` | A | seed 工作区 (`CCTPL_SEED_DIR`), 参数化脚本, `hooks/` | `tmp/cctpl/template/` (先清空) | 生成完整的 cookiecutter 模板根目录: `cookiecutter.json`, `hooks/`, template dir |
| `check-seed-values` | A | `tmp/cctpl/template/` | 无 | template dir 中 (文件名和文件内容) 不存在任何 seed value, 已声明为合法残留的除外 |
| `test-template` | A | `tmp/cctpl/template/` | `tmp/cctpl/output/` (先清空) | `cookiecutter --no-input` 用默认值成功生成一个项目 |
| `check-output` | A | `tmp/cctpl/output/`, `cookiecutter.json` 的 `_copy_without_render` | 无 | 生成的项目中 (文件名和文件内容) 不存在未解析的 `cookiecutter.` 变量引用. 不检查一般的 `{{` / `{%`: 它们可能来自 seed 原本的内容 (见 `05-parameterization.md` 的 Jinja Conflicts) |
| `check-roundtrip` | A | `tmp/cctpl/template/`, 参数化脚本中的 seed values, seed 工作区 | `tmp/cctpl/roundtrip/` (先清空) | 用 seed values 渲染模板, 结果与 seed 一致; 允许的差异只有 exclude 的文件, hooks 生成或修改的内容, 已声明的合法残留 (定义见 `05-parameterization.md` 的 Round Trip) |
| `test-output` | A | `tmp/cctpl/output/` 中生成的项目 | 该项目的 `.venv/`, 测试产物 | 在生成的项目中安装依赖并运行其测试, 全部通过 |
| `apply-template` | A | `tmp/cctpl/template/` | tpl repo 根目录的 `cookiecutter.json` 和 template dir (整体替换) | 两者 **一起** 被替换. 不改动 `hooks/` (它是 source) |
| `sync` | A | 同上 | 同上 | 按顺序运行 `make-template` → `check-seed-values` → `test-template` → `check-output` → `check-roundtrip` → `apply-template`, 任何一步失败立即停止并返回非 0 |

说明:

- **合法残留**: 某些 seed value 在 template dir 中合法出现 (例如一个通用字符串碰巧和某个 seed value 相同). 这类例外必须在参数化脚本中显式声明, 不能靠人工忽略检查结果. 声明方式见 `05-parameterization.md`.
- **`test-output` 不在 `sync` 中.** 它需要为生成的项目安装完整依赖, 耗时较长. Sync 阶段在以下情况运行它: 改动涉及依赖, 构建配置, 测试配置, 或 hooks. 具体判定见 `08-verification.md`.
- **`apply-template` 是 Sync 的最后一步**, 运行后 tpl repo 的 git diff 就是本次迭代的全部 artifact 变化, 供 Review 阶段查看.


## Release Tasks

| Task | Level | 读 | 写 | 成功条件 |
| :--- | :--- | :--- | :--- | :--- |
| `publish-template` | **U** | tpl repo 工作区, `pyproject.toml` 中的 tpl 版本号 | git 历史, GitHub | commit 并 push `main`; 把 `main` 的变化带到所有 `preset/*` 分支并 push (方式见 `07-versioning-and-release.md`); 切回 `main`; 以 tpl 版本号创建或更新 GitHub release |
| `verify-release` | A | GitHub 上已发布的模板 | `tmp/cctpl/verify/` (先清空) | 对 `main` 和每个指定的 `preset/*` 分支, 用 `cookiecutter gh:<owner>/<repo> --checkout <branch> --no-input` 生成项目, 并在其中运行测试, 全部通过 |

说明:

- `publish-template` 的分支列表通过 `git branch --list 'preset/*'` 自动发现, 不在代码中写死.
- `publish-template` 的 tag 和 release 名称使用 **tpl** 版本号, 与 seed 版本号无关 (见 `07-versioning-and-release.md`).
- `publish-template` 运行前应有确认提示. 这是 U 级 task 中唯一允许的交互.
- `verify-release` 只从 GitHub 读取, 不写入远端, 所以是 A 级. 它是否运行由人决定 (`/cctpl-verify-cn` 只能由人触发), 但运行本身是安全的.


## Environment Tasks

| Task | Level | 作用 |
| :--- | :--- | :--- |
| `venv-create` | A | 创建 tpl repo 的虚拟环境 |
| `inst` | A | 安装 tpl repo 的依赖. 其他 task 通过 `depends` 依赖它 |
| `export` | A | 导出 requirements 文件 |
| `update-github-metadata` | **U** | 修改 GitHub 仓库的描述和主页, 属于远端写入 |


## Forbidden Composite Tasks

**不允许存在把 A 级和 U 级 task 串在一起的复合 task.** 例如旧的 `all` (从 make-template 一直跑到 publish-template): agent 一旦被允许运行它, 就等于被允许发布. 需要一键执行的范围到 `sync` 为止.


## Tasks by Stage

| Stage (见 `03-workflow.md`) | 使用的 task |
| :--- | :--- |
| 2 Seed Self-Test | seed repo 自己的 task (例如测试, 构建文档), 不属于本契约 |
| 3 Sync | `sync` (或逐个运行其中的步骤), 按需 `test-output` |
| 6 Release Prep | 无 task, 只修改文件 |
| 7 Publish | `publish-template` (人执行) |
| 8 Verify | `verify-release` |
