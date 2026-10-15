# Safety Rules

本文定义 agent 在维护 tpl / seed 仓库时能做什么, 不能做什么, 以及需要人执行的操作如何交接. 前置阅读: `02-repo-layout.md`, `04-mise-task-contract.md`.


## Principle

**agent 只做本地的, 可撤回的事. 凡是写入 git 历史, 或改动任何远端的事, 都由人执行.**

- 本地文件改动: 可以用 `git diff` 查看, 用 `git checkout` 撤回, 或重新生成. agent 可以做.
- git 历史和远端 (GitHub, PyPI, Read the Docs, Codecov): 一旦写入, 撤回代价高, 或者对其他人已经可见. agent 只打印命令.

这条规则不因会话中的要求而放宽. 即使在对话中被要求 "直接帮我 push", agent 仍然只打印命令. 需要放宽时, 由人修改 settings, 而不是由 agent 判断.


## Operations

| 操作 | agent | 说明 |
| :--- | :--- | :--- |
| 读取两个仓库中的任何文件 | 可以 | |
| 编辑 seed 中的文件 (含新增, 删除) | 可以 | 删除文件时在总结中明确列出 |
| 编辑 tpl repo 中的 source | 可以 | source 的定义见 `02-repo-layout.md` |
| 手工编辑 artifact (`cookiecutter.json`, template dir) | **不可以** | 只能通过 `apply-template` 更新 |
| 修改 tpl 版本号 (`pyproject.toml`) | 可以, 需先确认 | 只在 Release Prep 阶段, 由人确认 bump 级别后修改 |
| 运行 A 级 task | 可以 | 见 `04-mise-task-contract.md` |
| 运行 U 级 task | **只打印** | |
| 运行 seed 自己的本地 task (安装, 测试, 构建文档) | 可以 | |
| 运行 seed 自己的远端 task (发布到 PyPI, 创建 release, 配置 Codecov / Read the Docs, 修改 GitHub 元数据) | **只打印** | |
| 只读 git 命令 (`status`, `diff`, `log`, `show`, `branch --list`, `rev-parse`, `describe`, `ls-remote`) | 可以 | 两个仓库都适用 |
| 改动 index, 工作区分支或历史的 git 命令 (`add`, `commit`, `push`, `merge`, `tag`, `checkout` / `switch` 分支, `reset`, `rebase`, `stash`, `branch -d` / `-m`) | **只打印** | 两个仓库都适用 |
| 只读 GitHub 查询 (例如查看 release, 拉取已发布模板) | 可以 | |
| 写入 GitHub (`gh release`, `gh api` 写操作, `gh repo edit`) | **只打印** | |
| 删除 `tmp/cctpl/` 下的内容 | 可以 | 仅通过对应 task, 或删除该阶段自己的子目录 |
| 删除 `tmp/` 下其他位置的内容 | **不可以** | 那里属于人 |
| 输出 token, 密码等 secret 的值 | **不可以** | `mise.toml` 的 env 会从 secret 存储中读取 token. 不 `echo`, 不打印这些环境变量 |

撤回 agent 自己刚做的文件改动属于 "本地可撤回" 的范围, 用 `git restore <file>` 执行. 不用 `git checkout`: 它同时能切换分支, 已被整体 deny.


## Enforcement

规则在两层上生效:

1. **settings (强制).** tpl repo 的 `.claude/settings.json` 中的 `permissions.deny` 拦截 U 级操作. 标准片段见 `../assets/settings-permissions.json`, 每个 tpl repo 照抄, 只替换其中的 seed 路径.
2. **skill 文本 (约定).** 每个 invoker 都读取本文, 在需要 U 级操作时主动停下并打印命令.

两层缺一不可:

- skill frontmatter 的 `allowed-tools` 只能让工具免确认, **不能禁用工具**. 只靠 skill 文本无法阻止 agent 执行命令.
- deny 规则是基于命令前缀的匹配, 覆盖不了所有写法 (例如通过其他脚本间接执行). 只靠 settings 也不完整.

deny 规则按命令前缀匹配整个子命令, 所以被 deny 的 git 子命令的只读用法也会被拦下, 例如 `git tag --list`, `git stash list`. 需要这类信息时改用不受影响的只读命令: 用 `git describe --tags` 或 `git for-each-ref refs/tags` 查 tag, 用 `git branch --list` 查分支.

deny 规则优先于 allow 规则. 即使 settings 中 allow 了 `Bash(mise *)`, deny 中的 `mise run publish-template*` 仍然生效.

### Seed Access

agent 需要在 tpl repo 的会话中直接读写 seed. 为此, tpl repo 的 `.claude/settings.json` 用 `permissions.additionalDirectories` 加入 seed 目录. 路径写成相对 tpl repo 根目录的形式 (例如 `../<seed repo>`): Claude Code 文档明确支持相对路径, 但没有说明是否展开 `~`. 这个路径必须与 `mise.toml` 中的 `CCTPL_SEED_DIR` 指向同一目录 (见 `02-repo-layout.md` 的 "Where Facts Live").


## Handoff Format

需要人执行 U 级操作时, agent 停下, 并按以下格式输出.

### 规则

- 用标题 `Commands for you to run` 开头, 让人一眼看出这里需要动手.
- 按执行顺序分组. 每组注明: 在哪个仓库, 做什么, 为什么.
- 命令放在 `bash` 代码块中, 每条命令 **可以单独复制执行**: 不依赖前面的 `cd`. 用 `git -C <path>` 或在同一行中 `cd <path> && ...`. 路径写成完整路径, 不用相对路径.
- commit message 由 agent 起草好, 直接写在命令中.
- 结尾说明: 全部执行完之后, 人应该告诉 agent 什么, 以及 agent 接下来会做什么.
- 不在命令中包含任何 secret 的值. 需要 token 的命令依赖 mise env 提供.

### 示例

````markdown
## Commands for you to run

**1. seed repo: 提交本次改动** (Release Prep 需要一个已 push 的 seed commit)

```bash
git -C ~/Documents/GitHub/<seed repo> add -A
```

```bash
git -C ~/Documents/GitHub/<seed repo> commit -m "Add pre-commit config and docs page"
```

```bash
git -C ~/Documents/GitHub/<seed repo> push
```

完成后告诉我 "seed 已 push", 我接着运行 Release Prep.
````
