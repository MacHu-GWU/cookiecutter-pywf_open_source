# Background and Concepts

本文先讲这套设计要解决的问题, 再定义 cctpl 家族的核心概念和命名规范. 其他所有文档都以本文的术语为准.


## Background

### 脚手架: cookiecutter 是最好的选择

当很多个项目共用同一套工具链 (依赖管理, 测试, 文档, CI/CD, 代码覆盖率, coding agent 配置等) 时, 每次新建项目都手工拷贝, 改名, 配置, 既慢又容易出错. 需要一个脚手架: 输入项目名等少量参数, 一条命令生成一个完整, 立即可用的项目.

cookiecutter 是做这件事最合适的工具: 模板就是一个普通的 git 仓库, 用户执行 `cookiecutter gh:<owner>/<repo>` 即可生成项目; 变量, 默认值, 可选值, prompt 都声明在 `cookiecutter.json` 中; 生成前后还可以运行 hooks 做额外处理.

### 问题: 模板不是一锤子买卖

工具链一直在演进: 新工具出现, 依赖升级, CI action 换版本, coding agent 的配置方式变化. 模板必须跟着持续迭代, 而且每次迭代都要回答三个问题:

1. **在哪里改?** 模板文件里到处是 `{{ cookiecutter.xxx }}` 占位符. 带占位符的 `pyproject.toml`, YAML, Python 文件都不是合法的源码, IDE 无法正常分析, 工具无法直接运行. 直接改模板等于盲改.
2. **怎么测试和验证?** 模板本身跑不起来. 唯一的办法是先用它生成一个项目, 再在生成的项目里测试. 反馈链长, 而且测试的是生成结果, 出了问题还要反推回模板的哪一行. 很多问题 (CI, 文档托管, 发布到 PyPI) 只有在一个真实的 GitHub 仓库里才会暴露.
3. **怎么发布?** 发布之后, 用户拿到的是 GitHub 上的版本, 而不是本地那份. 本地验证通过不代表发布出去的模板没问题 (例如有文件漏拷贝), 还要用已发布的版本再验证一次.

如果直接维护模板, 这三个问题都没有好答案, 错误最终由使用模板的人发现.

### 解法: 先做一个真实项目, 再逆向成模板

把方向反过来: 不直接维护模板, 而是维护一个真实, 可运行的项目, 再用程序把它机械地 "参数化" 成模板. 于是每个模板都由两个 git 仓库组成:

- **seed repo**: 一个真实, 可运行的项目. 所有参数都是具体值, 可以直接跑测试, 构建文档, 发布到 PyPI, 在 GitHub 上跑 CI. 所有 "生成的项目里应该有什么" 的工作都在这里完成和验证.
- **tpl repo**: 把 seed 逆向参数化成 cookiecutter 模板, 机械地验证, 然后对外发布. 所有 "怎么把 seed 变成模板, 怎么发布" 的工作都在这里.

三个问题因此都有了答案:

| 问题 | seed / tpl 设计中的答案 |
| :--- | :--- |
| 在哪里改? | 模板内容在 seed 中改. seed 是合法的源码, 用正常的开发方式编辑 |
| 怎么测试和验证? | seed 自己就能跑测试, 构建文档, 跑 CI. 参数化之后再机械检查: 没有残留的 seed value, 没有未解析的占位符, 生成的项目能通过测试 |
| 怎么发布? | tpl repo 负责发布, 发布后再从 GitHub 拉取已发布的模板, 生成项目验证一次 |

信息只有一个流向: **seed → tpl**. 模板内容永远先在 seed 中改, 再通过参数化流入 tpl.

### 代价, 以及 cctpl 的角色

这套设计的代价是流程变长: 两个仓库, 一套必须持续维护的参数化规则, 多个检查步骤, 以及横跨两个仓库的 git 操作. 每次迭代都完整, 正确地走一遍并不轻松.

cctpl 家族的作用就是让 AI agent 承担这部分成本: 把流程写成规范 (本 skill 的 `references/`), 由 agent 按规范执行改动, 参数化, 检查和发布准备, 人只负责 review 和执行 git 写操作.


## Terminology

| Term | 定义 |
| :--- | :--- |
| tpl repo | 模板仓库. 持有参数化逻辑, 发布流程, 以及本家族的 skill. 对外发布的就是它 |
| seed repo | 种子仓库. 一个可运行的具体项目, 是参数化的素材. 不承载任何维护逻辑 |
| template dir | tpl repo 中由参数化生成的模板目录, 通常是 `{{ cookiecutter.package_name }}-project/`. 只能由脚本生成, 不手改 |
| seed value | seed 中需要被替换成 cookiecutter 变量的具体字符串, 例如包名, 作者, GitHub 用户名, token 字段名 |
| parameter | 一个 cookiecutter 变量的完整定义: 名称, 匹配 seed value 的 selector, 默认值, 可选值, prompt |
| `cookiecutter.json` | cookiecutter 读取的变量声明文件. 由参数化生成, 和 template dir 一起构成发布产物 |
| hooks | cookiecutter 在生成项目前后执行的脚本 (例如生成 license 文件). 在 tpl repo 中手工维护 |
| preset | 一套个人特化的 `cookiecutter.json` 默认值. 在 `main` 上定义为 `presets/<name>.json`, 发布时生成同名的 `preset/<name>` 分支供使用者 checkout |
| generated project | 用模板生成出来的项目. 用于验证模板, 也是最终用户拿到的东西 |


## Naming Convention

| 对象 | 命名 | 例子 |
| :--- | :--- | :--- |
| tpl repo | `cookiecutter-<name>` | `cookiecutter-pywf_open_source` |
| seed repo | `cookiecutter_<name>_demo-project` 或 `cookiecutter_<name>_template-project` | `cookiecutter_pywf_open_source_demo-project` |
| seed 的包名 | seed repo 去掉 `-project` 后缀 | `cookiecutter_pywf_open_source_demo` |
| preset 分支 | `preset/<name>` | `preset/sanhe` |

seed 的包名, 仓库名都有独立的命名空间, 所以它们作为 seed value 被替换时不会和项目中的其他字符串冲突. 这是选择这种命名的主要原因.


## Two Kinds of Change

任何对模板的改动, 都先归入以下两类之一. 归类决定了在哪个仓库动手.

| 类型 | 含义 | 在哪里改 | 例子 |
| :--- | :--- | :--- | :--- |
| template content | 生成的项目里应该有什么 | seed repo | 新增一个 mise task, 改 CI 配置, 加一个文档页, 升级依赖 |
| template mechanism | seed 怎么变成模板, 模板怎么生成项目 | tpl repo | 新增或修改 parameter, 调整哪些文件不进入模板 (exclude) 或原样拷贝不做替换 (no_render), 改 hooks, 改 `cookiecutter.json` 的 prompt |

有些改动同时涉及两类. 例如新增一个 parameter: 先在 seed 中写入新的 seed value (content), 再在 tpl 中声明对应的 parameter (mechanism).

**template dir 永远不属于任何一类.** 它是产物, 不是源头. 想改 template dir 中的某个文件, 应该去改 seed 中对应的文件.


## Where Skills Live

与模板相关的 skill 有两个位置, 不能混淆:

| 位置 | 放什么 | 影响范围 |
| :--- | :--- | :--- |
| seed repo `.claude/skills/` | 每个生成的项目都应该有的 skill | 会被参数化进模板, 进入所有生成的项目 |
| tpl repo `.claude/skills/` | 维护 seed → tpl → 发布这套流程的 skill: 本家族 `cctpl-*-cn`, 以及它依赖的工具 skill (`/pypi-cookiecutter_maker`, `/py-changelog`) | 只在 tpl repo 中生效, 不进入模板 |

**维护用的东西绝不放进 seed.** seed 的 `.claude/` 是模板内容的一部分, 放进去的任何东西都会被分发到每一个生成的项目.


## Two Independent Versions

seed repo 和 tpl repo 各有一个版本号, 二者互不相关:

- **seed 版本号**: 只用于把 seed 发布到 PyPI, 测试发布流程本身是否工作. seed 可能结构大改但版本号不变.
- **tpl 版本号**: 模板自己的版本, 决定 tpl repo 的 tag, GitHub release, `release-history.rst` 条目.

两个版本号之间的唯一联系是: 每个 tpl 版本在 tpl 的 `release-history.rst` 对应条目中记录它是由哪个 seed commit 生成的. seed 不打 tag, 这条记录是追溯 "某个模板版本对应哪个 seed 状态" 的唯一依据.
