# Mise Task Contract

本文定义 tpl repo 中每个 mise task 必须满足的契约: 名称, 读什么, 写什么, 成功与失败的判定, 安全级别. `.mise/tasks/` 的实现以本文为准; 实现与本文不一致时, 修改实现. 前置阅读: `02-repo-layout.md`, `03-parameterization.md`, `04-safety-rules.md`, `05-workflow.md`, `06-verification.md`.

本文只规定 "做什么" 和 "怎样算成功", 不规定 "怎么实现". 具体实现读 `mise.toml` 和 `.mise/tasks/`.


## Safety Levels

下文每个 task 的 Level 列使用 `04-safety-rules.md` 的 Safety Levels: **A** 由 agent 直接运行, **U** 只由人运行.


## General Rules

所有 task 都必须满足:

- **从 tpl repo 根目录用 `mise run <task>` 运行.** 不依赖当前 shell 所在目录.
- **用退出码表达成败.** 成功返回 0, 失败返回非 0. 检查类 task 发现问题时 **必须** 返回非 0, 不能只打印. agent 依靠退出码判断下一步, 而不是阅读输出.
- **失败时输出可定位.** 指出问题所在的文件 (相对路径) 和行号, 以及修复方向或应该先运行的 task.
- **可重复运行.** 同样的输入重复运行得到同样的结果. 每个 task 开始时只清空自己负责的 `tmp/cctpl/` 子目录, 不碰其他位置 (见 `02-repo-layout.md` 的 workspace 规则). 每个 task 负责哪个子目录, 见下文各表的 "写" 列.
- **不交互.** A 级 task 不读取 stdin. 原因: agent 无法回答交互提示, task 会一直卡住. 只有 U 级 task 可以有确认提示, 因为它们本来就只由人运行.
- **不写死路径.** seed 位置只从 `CCTPL_SEED_DIR` 读取; tpl repo 内的路径从 repo 根目录推导. 缺少 `CCTPL_SEED_DIR` 或目录不存在时, 立即失败并说明原因.
- **前置条件不满足时立即失败.** 例如 `tmp/cctpl/template/` 不存在时, check 类 task 应失败并提示先运行 `make-template`, 而不是报告 "没有发现问题".


## Build Tasks

按 Sync 阶段的执行顺序排列.

| Task | Level | 读 | 写 | 成功条件 |
| :--- | :--- | :--- | :--- | :--- |
| `make-template` | A | seed 工作区中 git 认可的文件 (`CCTPL_SEED_DIR`, 见 `03-parameterization.md` 的 Input), 参数化脚本, `hooks/` | `tmp/cctpl/stage/`, `tmp/cctpl/template/` (先清空) | 生成完整的 cookiecutter 模板根目录: `cookiecutter.json` (含私有变量 `_template_version` = tpl 版本号), `hooks/`, template dir |
| `check-seed-values` | A | `tmp/cctpl/template/` | 无 | template dir 中 (文件名和文件内容) 不存在任何 **独特** seed value, 已声明为合法残留的除外; 每个 parameter 自己的替换结果 (`Parameter.placeholder`, 含 context) 在 template dir 中至少出现一次 (零命中说明 selector 已与 seed 脱节). 不扫描 `hooks/`: hooks 本来就引用变量, 会掩盖零命中 |
| `test-template` | A | `tmp/cctpl/template/` | `tmp/cctpl/output/` (先清空) | `cookiecutter --no-input` 用默认值成功生成一个项目; 影响 hooks 或模板分支的 choice 变量, 每个可选值至少生成一次 (见 `03-parameterization.md` 的 Choice Coverage) |
| `check-output` | A | `tmp/cctpl/output/` (含 `choices/` 下的项目) | 无 | 生成的项目中 (文件名和文件内容) 不存在未解析的 `cookiecutter.` 变量引用. 不检查一般的 `{{` / `{%`: 它们可能来自 seed 原本的内容 (见 `03-parameterization.md` 的 Jinja Conflicts) |
| `check-roundtrip` | A | `tmp/cctpl/template/`, 参数化脚本中的 seed values, seed 工作区 | `tmp/cctpl/roundtrip/` (先清空) | 用 seed values 渲染模板, 结果与 seed 一致; 允许的差异只有 `EXCLUDE` 中的文件只出现在 seed 一侧, 以及 `HOOK_OUTPUTS` 中的文件内容不同或只出现在一侧 (定义见 `03-parameterization.md` 的 Round Trip). 不比较文件权限 |
| `test-output` | A | `tmp/cctpl/output/` 中生成的项目 | 这些项目的 `.venv/`, `dist/`, 测试产物 | 默认值项目安装依赖并运行测试, 全部通过; `choices/` 下的每个项目都能构建 wheel. 不依赖任何 secret (见 `06-verification.md` 的 Secrets) |
| `check-presets` | A | `presets/*.json`, `tmp/cctpl/template/cookiecutter.json` | 无 | 每个 preset 覆盖的变量都存在于新的 `cookiecutter.json` 中; choice 变量的覆盖值是合法的可选值 |
| `apply-template` | A | `tmp/cctpl/template/` | tpl repo 根目录的 `cookiecutter.json`, template dir (整体替换) 和 `README.rst` (从 `.mise/tasks/cctpl/README.rst.jinja` 渲染) | 模板产物两者 **一起** 被替换, `README.rst` 重新渲染. 不改动 `hooks/` (它是 source) |
| `sync` | A | 同上 | 同上 | 按顺序运行 `make-template` → `check-seed-values` → `test-template` → `check-output` → `check-roundtrip` → `check-presets` → `apply-template`, 任何一步失败立即停止并返回非 0 |

说明:

- `check-seed-values` 扫描的独特值和放行的合法残留, 分别来自参数化脚本的 `UNIQUE_SEED_VALUES` 和 `LEGAL_RESIDUES` (见 `03-parameterization.md` 的 Legal Residue).
- **`test-output` 不在 `sync` 中.** 它需要为生成的项目安装完整依赖, 耗时较长. 什么时候必须运行, 见 `06-verification.md` 的 "L4: When Needed".
- **`apply-template` 是 Sync 的最后一步**, 运行后 tpl repo 的 git diff 就是本次迭代的全部 artifact 变化, 供 Review 阶段查看.


## Trial Task

| Task | Level | 读 | 写 | 成功条件 |
| :--- | :--- | :--- | :--- | :--- |
| `try-template` | A | seed 工作区, 参数化脚本, `presets/<name>.json` (可选) | `tmp/cctpl/stage/`, `tmp/cctpl/template/`, `tmp/cctpl/try/<label>/`, `tmp/cctpl/try/<label>.log` | 生成模板, 用默认值或指定 preset 渲染一个项目, 在其中通过 mise 依次运行 `try_template.py` 的 `PROJECT_TASKS`, 全部通过 |

说明:

- 用法: `mise run try-template` (默认值) 或 `mise run try-template <preset>`.
- 它是推荐的人工试用机制, 不在 `sync` 中, 不做任何检查, 也不应用 artifact. 定义见 `06-verification.md` 的 Local Trial.
- 它会覆盖 `stage/` 和 `template/`, 与 `make-template` 共用这两个子目录.
- 每一步都输出带 `[try i/n]` 前缀的关键日志, 同时写入日志文件, 供人和 agent 排查.


## Release Tasks

| Task | Level | 读 | 写 | 成功条件 |
| :--- | :--- | :--- | :--- | :--- |
| `publish-template` | **U** | tpl repo 工作区, `pyproject.toml` 中的 tpl 版本号 | git 历史, GitHub | 当前分支必须是 `main`, `GITHUB_TOKEN` 不能为空, 否则在推送任何东西之前立即失败; commit 并 push `main`; 按 `presets/*.json` 从 `main` 重新生成每个 `preset/*` 分支并覆盖推送 (方式见 `02-repo-layout.md` 的 Preset Branches); 切回 `main`; 报告远端多余的 `preset/*` 分支; 在 `main` 的最新 commit 上以 tpl 版本号创建或更新 tag 和 GitHub release |
| `verify-release` | A | GitHub 上已发布的模板 | `tmp/cctpl/verify/` (先清空) | 对 `main` 和每个指定的 `preset/*` 分支 (参数只接受这两种, 其他分支名立即失败), 用 `cookiecutter gh:<owner>/<repo> --checkout <branch> --no-input` 生成项目, 与本地结果比较, 并在其中运行测试, 全部通过 (步骤见 `06-verification.md` 的 L5) |

说明:

- `publish-template` 的 preset 列表来自 `presets/*.json`, 不在代码中写死. 远端存在但已没有对应 preset 文件的 `preset/*` 分支, 只报告, 不自动删除: 删除远端分支会影响正在使用它的人, 由人决定.
- `publish-template` 的 tag 和 release 名称使用 **tpl** 版本号, 与 seed 版本号无关 (见 `01-background-and-concepts.md` 的 Two Independent Versions).
- `publish-template` 运行前应有确认提示. 这是 U 级 task 中唯一允许的交互.
- `verify-release` 只从 GitHub 读取, 不写入远端, 所以是 A 级. 它是否运行由人决定 (`/cctpl-verify-cn` 只能由人触发), 但运行本身是安全的.


## Environment Tasks

| Task | Level | 作用 |
| :--- | :--- | :--- |
| `venv-create` | A | 创建 tpl repo 的虚拟环境 |
| `venv-remove` | A | 删除 tpl repo 的虚拟环境 |
| `inst` | A | 安装 tpl repo 的依赖. 其他 task 通过 `depends` 依赖它 |


## Forbidden Composite Tasks

**不允许存在把 A 级和 U 级 task 串在一起的复合 task.** 例如旧的 `all` (从 make-template 一直跑到 publish-template): agent 一旦被允许运行它, 就等于被允许发布. 需要一键执行的范围到 `sync` 为止.


## Tasks by Stage

| Stage (见 `05-workflow.md`) | 使用的 task |
| :--- | :--- |
| 2 Seed Self-Test | seed repo 自己的 task (例如测试, 构建文档), 不属于本契约 |
| 3 Sync | `sync` (或逐个运行其中的步骤), 按需 `test-output` |
| 任何时候 (不属于阶段) | `try-template` |
| 6 Release Prep | 修改版本号后重新运行 `sync`; 其余只修改文件 |
| 7 Publish | `publish-template` (人执行) |
| 8 Verify | `verify-release` |
