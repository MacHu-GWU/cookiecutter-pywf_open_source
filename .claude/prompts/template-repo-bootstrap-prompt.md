<!--
使用说明 (给人看, agent 可忽略):
每次复用时只需要编辑第 1 节 "本次任务变量". 第 2 节及之后的内容对所有 P2 都一样, 不要改.
-->

# Template Repo Bootstrap

## 1. 本次任务变量 (每次只改这一节)

### 1.1 P2: Seed Repo 已成熟, Template Repo 待完成的 Pair

- `P2-seed`: /Users/sanhehu/Documents/GitHub/cookiecutter_pywf_internal_proprietary_demo-project
- `P2-tpl`: /Users/sanhehu/Documents/GitHub/cookiecutter-pywf_internal_proprietary

### 1.2 P2 的特殊注意事项 (人工填写, 没有就写 "暂无")

- 暂无

## 2. 固定参考 (所有任务通用)

### 2.1 P1: 成熟的 Seed / Template Repo Pair

- `P1-seed`: /Users/sanhehu/Documents/GitHub/cookiecutter_pywf_open_source_demo-project
- `P1-tpl`: /Users/sanhehu/Documents/GitHub/cookiecutter-pywf_open_source

### 2.2 知识库

- `BASE`: `P1-tpl`/.claude/skills/cctpl-base-cn

下文一律用 `P1-seed`, `P1-tpl`, `P2-seed`, `P2-tpl`, `BASE` 这些简写指代上面的路径.

## 3. 读写权限

- 只能在 `P2-tpl` 下创建或修改文件.
- 其他所有目录 (`P1-seed`, `P1-tpl`, `P2-seed`) 只读.

## 4. 开工前先读

1. `BASE`/references/01-background-and-concepts.md: 理解 Seed Repo 和 Template Repo 的概念.
2. `BASE` 下的其余所有文件.
3. `P1-tpl` 的目录结构, 以及它的 `mise.toml` 和 `make_template.py`.
4. `P2-seed` 的目录结构, 用来确定 `make_template.py` 需要的参数.
5. `P2-tpl` 的现状. 它可能是以下两种之一:
   - 完全空白, 百废待兴.
   - 已有一些旧内容, 但远不如 `P1-tpl` 成熟.

## 5. 任务

参照 `P1-tpl` 的代码结构, 把 `P2-tpl` 做到和 `P1-tpl` 一样成熟.

工作方式:

1. 先对比 `P1-tpl` 和 `P2-tpl`, 列出差距和计划, 再动手.
2. `P2-tpl` 已有的旧内容: 能复用就复用, 和 `P1-tpl` 结构冲突的以 `P1-tpl` 为准, 删除前先告诉我.
3. `make_template.py` 的参数要适配 `P2-seed`. 拿不准的参数 (例如要替换成模板变量的字符串, 要排除的文件) 先问我, 不要猜.
4. 第 1.2 节的特殊注意事项优先于本文其他内容.

## 6. 验收标准

在 `P2-tpl` 下:

1. `mise run sync`: 一键从 `P2-seed` 构建 Cookiecutter Template, 存放到 `P2-tpl` 下.
2. `mise run e2e`: 一键完成 build template 和 try template, 然后进入用 template 生成的测试 repo, 运行一些 integration test. 这些命令只能在本地运行, 不能改变 GitHub, PyPI, AWS 等云端服务的状态.
3. `mise run publish-template`: 一键完成 sync, 并发布到 GitHub release.
4. `mise run publish-presets`: 一键把各个 preset branch 更新到最新并发布.

第 1, 2 条由你实际运行验证. 第 3, 4 条会改变云端状态, 只做到代码就绪, 不要运行, 除非我明确同意.
