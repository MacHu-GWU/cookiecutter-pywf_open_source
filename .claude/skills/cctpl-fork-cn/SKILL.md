---
name: cctpl-fork-cn
description: "Copy this cctpl skill family and its automation code, once, to another cookiecutter tpl repo + seed repo pair: rewrite everything bound to the current pair, migrate a 1.0 tpl repo (old make_template.py, preset branches, leftovers), and get sync passing there. After the fork the two pairs are fully independent. 把 cctpl 家族复制到另一对仓库."
disable-model-invocation: true
argument-hint: "<target tpl repo dir> <target seed repo dir>"
---
把本家族 (skill 和自动化代码) 一次性复制到另一对仓库 (下文称 "目标"), 改写其中与本仓库对绑定的内容, 并让目标的 `sync` 跑通. 复制完成后两边彻底独立, 不再同步. 目标上的进一步特化 (例如为 AWS 项目补充 cdk 相关的规则) 留给用户在目标自己的会话中, 用复制过去的家族完成.

本 skill 在 **源 tpl repo** (也就是本仓库) 的会话中运行, 读写目标的两个目录. 它不属于 `05-workflow.md` 中的任何阶段.

Read ../cctpl-base-cn/SKILL.md, then:

- ../cctpl-base-cn/references/01-background-and-concepts.md
- ../cctpl-base-cn/references/02-repo-layout.md
- ../cctpl-base-cn/references/03-parameterization.md
- ../cctpl-base-cn/references/04-safety-rules.md
- ../cctpl-base-cn/references/06-verification.md
- ../cctpl-base-cn/references/07-mise-task-contract.md
- ../cctpl-base-cn/references/09-troubleshooting.md

Follow those docs to do the work. 02 的 Where Facts Live 表是本 skill 的清单: "fork 时" 一列规定每项事实怎么处理.

## Inputs

参数: $ARGUMENTS

两个参数依次是目标 tpl repo 目录和目标 seed repo 目录, 可以是绝对路径, 也可以是相对本仓库根目录的路径. 缺少任何一个时, 先问用户.

## Steps

1. **前置检查 (只读).** 任何一项不满足就停下, 按 04 的 Handoff Format 给出需要用户执行的命令:
   - 本会话能读写两个目标目录. 不能时, 请用户把它们加入本会话.
   - 目标 seed 是 git 仓库, 并且有 GitHub remote. 原因: 参数化的输入是 seed 中 git 认可的文件 (03 的 File Filtering). 不满足时给出 `git init` 和创建 GitHub 仓库的命令.
   - 目标 tpl repo 存在, 是 git 仓库, 当前在 `main` 分支, 工作区干净. 原因: 这样 fork 结束后, 目标的 git diff 就是本次 fork 的全部改动. 不存在时给出创建或 clone 的命令.
   - 判断目标 tpl repo 属于哪种情况: **全新** (没有模板), **1.0** (有旧的 `make_template.py`, 但没有 cctpl 家族), 或 **已有 cctpl**. 已有 cctpl 时停下, 告诉用户本 skill 不覆盖已有的家族.
2. **说明计划, 等用户确认.** 列出将要拷贝, 改写, 删除的文件, 以及第 4 步对参数化声明的初步判断.
3. **拷贝通用文件 (逐字).**
   - `.claude/skills/` 下的全部 `cctpl-*-cn` (包括本 skill, 以便目标以后再 fork), 以及 `pypi-cookiecutter_maker`. 目标中有旧的 `py-changelog` 时删除它 (已被 `cctpl-changelog-cn` 取代).
   - `.mise/tasks/` 下的全部代码 (不含 `__pycache__`). 其中 `cctpl/pair.py` 和 `make_template.py` 的声明部分在第 4 步改写.
   - `mise.toml` 中 cctpl 的 task 和 `[tools]`. 目标原有 `mise.toml` 中的其他 task 是 1.0 遗留, 在第 6 步处理.
   - `.claude/settings.json`: 把 `../cctpl-base-cn/assets/settings-permissions.json` 中的 deny 规则合并进目标已有的 settings. 保留目标已有的其他键 (例如 `model`, `allow`).
   - `CLAUDE.md`: 以本仓库的 `CLAUDE.md` 为骨架, 改写第一段 (这个模板生成什么样的项目), 清空 Current Status.
   - `pyproject.toml`: 只合并 `dependencies` 和 `[tool.uv]`. 名称, URL, 作者沿用目标的值. 版本号在第 4 步统一.
   - `.gitignore`: 确认其中忽略了 `tmp/`.
   - **seed 一侧的 seed-only 文件** (02 的 seed repo): 把本仓库 seed 的 `.claude/skills/pywf-oss-changelog-seed-repo/` 拷贝到目标 seed, 第 4 步改写其中的 tpl repo 地址. 目标 seed 的 skill 前缀不是 `pywf-oss` 时, 按目标的前缀改名, 并同步修改 `make_template.py` 的 `EXCLUDE`.
4. **改写与本仓库对绑定的内容.** 按 02 的 Where Facts Live, 逐行处理 "fork 时" 为 "改写" 的项:
   - `mise.toml` 的 `CCTPL_SEED_DIR` 和 settings 的 `additionalDirectories`: 都改为指向目标 seed, 两者必须一致.
   - `.mise/tasks/cctpl/pair.py`, 逐个常量处理:
     - GitHub owner 和 tpl repo 名: 从目标 tpl repo 的 remote 读取. seed 的 GitHub 仓库名不写在这里, 由 `CCTPL_SEED_DIR` 的目录名推出 (02 的 Where Facts Live), 所以确认目标 seed 的 remote 与 tpl repo 属于同一个 owner, 并且仓库名等于本地目录名.
     - `TEMPLATE_DIR_NAME`: 与目标 seed 的目录名和包名对应.
     - `PYTHON_VERSION_VARIABLE`: 生成项目用哪个 cookiecutter 变量决定 Python 版本.
     - `INSTALL_COMMAND` 和 `TEST_COMMAND`: 按目标 seed 的测试布局决定. 例如需要云端凭证的集成测试 (`tests_int/` 之类) 不能放进 L4, `TEST_COMMAND` 只运行单元测试.
     - `PROJECT_TASKS`: 从目标 seed 的 `mise.toml` 中挑出不需要 secret, 不需要云资源的本地 task.
   - `make_template.py` 的声明部分 (从 `SeedValues` 到 `LEGAL_RESIDUES`), 按 03 编写. `EXCLUDE` 必须包含两个 seed-only 文件. 文件的其余部分 (`main`, `add_template_version`, `get_seed_context`) 保持逐字不变.
   - **统一版本号** (01 的 One Shared Version): 取目标 seed 和目标 tpl 两个版本号中较大的一个, 升一个 major (例如 `0.2.1` 和 `0.2.1` → `1.0.0`), 写入目标 seed 的 `pyproject.toml` 并在目标 seed 中运行它的安装 task 更新 lock 文件. 版本号先向用户确认. 目标 tpl 的版本号不手改, 第 7 步的 `sync` 会写入.
   - **seed changelog**: 在目标 seed 新建 `release-history-seed-repo.rst` (格式见 08 的 Changelogs), 第一个条目就是上面的新版本, 完整介绍目标 seed 当前的全部 feature, 并说明版本号为什么跳变. 目标 seed 的 `release-history.rst` 不动.
   - **tpl changelog**: 目标 tpl 的 `release-history.rst` 中已有的条目保持不变, 新版本的条目在目标第一次发布时用 `/cctpl-changelog-cn` 写.
   - 拷贝过去的 `pywf-oss-changelog-seed-repo` 中的 tpl repo GitHub 地址, 改为目标 tpl repo 的地址.
     - 目标是 1.0 时: 迁移旧 `make_template.py` 中的 parameter. 再按 03 补齐 context 或 file scope, 补齐 `UNIQUE_SEED_VALUES`, `HOOK_OUTPUTS`, `CHOICE_COVERAGE` 等声明.
     - 目标是全新时: 分析目标 seed, 列出候选的 seed value (包名的各种形态, 作者, 邮箱, GitHub 用户名, secret 字段, 云资源名称等), 交给用户确认.
   - `presets/*.json`: 目标是 1.0, 并且有 preset 分支 (`main` 以外, 改过 `cookiecutter.json` 默认值的分支) 时, 用 `git show <branch>:cookiecutter.json` (只读) 读出每个分支的默认值, 与 `main` 比较, 把差异写成覆盖文件. 选择 preset 名时向用户确认.
   - `.mise/tasks/cctpl/README.rst.jinja` 的 Overview 和 Disclaimer 两节.
   - `hooks/`: 沿用目标已有的 hooks, 不拷贝本仓库的 hooks. 目标没有 hooks 时, 按 03 的 Hooks 判断是否需要.
5. **检查残留.** 在目标 tpl repo 的 source 中搜索本仓库对的独特值: 本仓库 `make_template.py` 的 `UNIQUE_SEED_VALUES`, `pair.py` 的 `GITHUB_REPO`, 本仓库 seed 的目录名. 除了文档中作为例子出现的地方, 都不应该出现.
6. **清理目标的 1.0 遗留.** 例如 `maintainer-guide.rst`, `run_cookiecutter_*.py`, `mise run all` 这类把 A 级和 U 级串在一起的复合 task (07 的 Forbidden Composite Tasks), 没有被使用的 Python 包, 以及 tpl repo 本身没有文档时的 `.readthedocs.yml`. 删除前先列给用户确认. 1.0 的 preset 分支不删: 由用户在目标第一次 2.0 发布之后手动删除.
7. **在目标中跑通.**
   - 目标的 `mise.toml` 第一次使用前需要 `mise trust`. 它会写入 mise 的信任记录, 所以把命令交给用户执行.
   - 在目标 tpl repo 根目录运行 `mise run sync`. 失败时按 09 修复, 只改目标的参数化声明和 `pair.py`, 直到通过.
   - 再运行 `mise run test-output` 和 `mise run try-template` (或用 `mise run e2e` 同时完成 `sync` 和 `try-template`).
   - 运行 `mise run check-release`, 确认版本号一致. seed 未 push, 未打 tag, tpl changelog 缺条目这几项此时失败是正常的, 在报告中列出.
   - 目标的 `sync` 会重新生成目标的 artifact (`cookiecutter.json`, template dir, `README.rst`), 这是预期的.

## Output

- 目标的情况 (全新或 1.0).
- 在目标中拷贝, 改写, 删除的文件清单.
- 参数化声明的摘要: 每个 parameter 的名称, seed value, 限定方式. 单独列出需要用户确认的地方.
- `sync`, `test-output`, `try-template` 的结果.
- 按 04 的 Handoff Format 给出目标两个仓库的提交命令. 说明目标的第一次发布: 先在目标 seed 中发布并打 tag (08 的 Seed Release), 再在目标 tpl 中用 `/cctpl-release-cn` 完成.
- 提醒用户: 之后在目标 tpl repo 中打开新的会话, 用目标自己的家族继续特化. 两边从此不再同步, 本仓库中家族的后续改动不会带到目标.

## Boundaries

- 不修改本仓库 (源) 中的任何文件.
- 不执行任何 git 写操作, 不创建 GitHub 仓库, 见 04.
- 目标已经有 cctpl 家族时停下, 不覆盖.
