# Troubleshooting

本文按出错的位置列出常见故障: 现象, 原因, 修法. 修法遵守 `03-parameterization.md` 和 `04-safety-rules.md`; 本文只给方向, 不重复规则. 前置阅读: `03-parameterization.md`, `06-verification.md`, `07-mise-task-contract.md`, `08-versioning-and-release.md`.

总的排查原则:

- **先判断问题在哪一侧.** seed 内容有问题 → 回到 seed 修 (Change 阶段). 参数化有问题 → 修参数化脚本 (template mechanism). 不要在 artifact 上修.
- **从最早失败的一层开始.** L1 失败时不看 L3 的结果; 前一层的问题通常是后一层失败的原因.
- **每次只改一处, 然后重跑 `sync`.**


## make-template

| 现象 | 原因 | 修法 |
| :--- | :--- | :--- |
| 找不到 seed 目录 | `CCTPL_SEED_DIR` 未设置, 或指向的目录不存在 | 检查 tpl repo `mise.toml` 的 `[env]`; 同时确认 settings 中 `additionalDirectories` 指向同一目录 |
| 报错 seed 目录名中没有任何 selector | cookiecutter 要求项目目录名中至少有一个变量 | 确认包名 parameter 的 selector 与 seed 目录名一致 |
| 报错 selector 或变量名重复 | 两个 parameter 的 selector 相同, 或两个写入 `cookiecutter.json` 的 parameter 同名 | 合并重复项; 同一变量的多处 context 只让一个写入 `cookiecutter.json` |


## L1: check-seed-values

| 现象 | 原因 | 修法 |
| :--- | :--- | :--- |
| 新文件中出现 seed value | seed 新增的文件中有 seed value, 而该文件是 no_render | 能 render 就移出 no_render; 确实需要原样拷贝时, 声明为合法残留 |
| 某种形态的名字没被替换 | seed value 的新形态没有对应 parameter (例如 CamelCase, 标题形式, URL 中的形式) | 为该形态新增 parameter, 派生形态用 custom placeholder |
| 报告某个 parameter 零命中 | 带 context 的 selector 与 seed 中的写法不再匹配 (例如格式化改变了空格或引号); 或 seed 已经不再使用这个值 | 更新 selector 的 context, 使之与 seed 当前写法一致; seed 不再需要时删除该 parameter (删除变量是 major) |
| seed value 出现在文件名或目录名中 | 文件名总会被参数化; 出现残留说明名字中的形态没有 parameter | 同 "某种形态的名字没被替换" |


## L2: test-template, check-output

| 现象 | 原因 | 修法 |
| :--- | :--- | :--- |
| cookiecutter 报 Jinja 语法错误 | seed 中的 Jinja 风格语法没有被转义 | 确认参数化库版本支持自动转义; 不在 seed 中手工转义 (见 `03-parameterization.md`) |
| hooks 报错 | hooks 逻辑与新变量或新文件不匹配 | 修 tpl repo 的 `hooks/`; 对相关 choice 做 choice coverage |
| 生成结果中有未解析的 `cookiecutter.` 引用 | custom placeholder 引用了不存在的变量, 或拼写错误 | 修 parameter 的 custom placeholder, 确认引用的变量在 `cookiecutter.json` 中 |
| 某个文件内容原样保留了 `{{ cookiecutter.xxx }}` | 该文件是 no_render, 但它又需要被渲染 | 移出 no_render |


## L3: check-roundtrip

过度替换 (不该替换的被替换了) 不会让 round trip 失败, 见 `03-parameterization.md` 的 What Round Trip Cannot See. 它的现象和修法列在本文的 Review 一节.

| 现象 | 原因 | 修法 |
| :--- | :--- | :--- |
| 派生形态与 seed 不一致 | 派生计算 (例如 slugify) 的结果与 seed 中的实际写法不同 | 修 custom placeholder 的计算方式, 或调整 seed 中的写法使之可推导 |
| 文件缺失 | 文件被 exclude 规则误伤 | 收窄 exclude 规则 |
| 文件多出 | seed 中的临时文件或本地文件没有被 exclude | 补充 exclude 规则, 或把文件从 seed 中清理掉 |
| 只有换行符或文件末尾换行不同 | 参数化统一写成 LF, 而 seed 中的文件是 CRLF | 统一 seed 中的换行符 (seed 的 `.gitattributes`) |


## L4: test-output

| 现象 | 原因 | 修法 |
| :--- | :--- | :--- |
| seed 自测通过, 生成项目测试失败 | 项目中写死了只对 seed 成立的东西 (例如 seed 的仓库地址, 文档站点名), 或默认值本身不合法 | 让该内容也参数化; 或修改默认值 |
| `choices/` 下某个项目构建 wheel 失败 | 某个可选值渲染出的配置不合法 (例如 `license` 不是合法的 SPDX 表达式) | 用 custom placeholder 在出问题的位置换算这个值 (见 `03-parameterization.md` 的 Choosing Seed Values), 或修 hooks |
| 依赖安装失败 | 生成项目没有 lock 文件, 全新 resolve 时某个依赖的最新版本不兼容 | 在 seed 的依赖声明中收紧版本范围, 在 seed 中验证后重新 Sync |


## Local Trial: try-template

先看输出最后的 `=== Try result`, 找到第一个 FAIL 的 task, 再看日志文件中这一步的 `[try i/n]` 日志块.

| 现象 | 原因 | 修法 |
| :--- | :--- | :--- |
| 第 1 步 (生成模板) 失败 | 与 make-template 相同 | 见上文 make-template 一节 |
| 安装类 task 失败 | 与 L4 的 "依赖安装失败" 相同; 或本机无法下载 mise 指定的 Python 版本 | 依赖问题在 seed 中收紧版本范围; 网络或工具问题与模板无关, 告诉用户 |
| 测试或覆盖率 task 失败, seed 自测通过 | 与 L4 的 "seed 自测通过, 生成项目测试失败" 相同 | 同 L4 |
| 文档构建 task 失败, seed 能构建文档 | 文档中写死了只对 seed 成立的内容 (例如包名出现在没有被参数化的形态中), 或文档依赖与默认值不兼容 | 先判断是 seed 内容问题还是参数化问题: 用 round trip 的输出对照; seed 内容问题回到 Change 阶段 |
| 默认值通过, 某个 preset 失败 | 该 preset 的 token 字段在本机的 secret 存储中不存在, 读取得到空值, 依赖 token 的 task 失败 | 不是模板问题. 确认本机的 secret 配置, 或换用默认值试用 |
| 手工进入项目后, mise 报配置不受信任 | `try-template` 只在本次运行中临时信任, 不写入 mise 的信任记录 | 在项目目录中运行一次 `mise trust` |


## Review: apply-template 之后

| 现象 | 原因 | 修法 |
| :--- | :--- | :--- |
| 用默认值生成的项目中, 某处无关内容变成了别的值; 或 template dir 的 diff 中, 某个通用变量的占位符出现在意料之外的文件 | 过度替换: 通用值被当作裸字符串替换 (例如依赖的版本号等于项目版本号) | 给该 parameter 加 context 或 file scope |
| artifact 的 diff 远大于预期 | seed 中的大文件 (导出的 requirements 文件等) 被重新生成; 或换行符变化 | 确认是否为预期变化; 不是则退回 seed 排查 |
| `cookiecutter.json` 中变量顺序或 prompt 意外变化 | parameter 的定义顺序或 prompt 被改动 | 检查参数化脚本的改动 |
| 只有 template dir 变了, `cookiecutter.json` 没变 (或相反) | apply-template 没有同时替换两者 | 修 apply-template, 两者必须一起替换 (见 `02-repo-layout.md`) |


## Publish

| 现象 | 原因 | 修法 |
| :--- | :--- | :--- |
| 生成 preset 分支失败 | preset 覆盖了一个已不存在的变量, 或给 choice 变量设了非法值 | 修改 `presets/*.json`; Sync 阶段的 `check-presets` 应已提前发现 |
| 一开始就报 `GITHUB_TOKEN is empty` | tpl repo `mise.toml` 读取 secret 失败 (读取命令带 `\|\| true`, 失败时得到空字符串) | 确认本机的 secret 存储能读到 token; 其他 task 不需要它 |
| push 和 preset 分支都成功了, 但没有 tag 或 GitHub release | 最后一步创建 release 失败 (例如 `GITHUB_TOKEN` 读取失败或权限不足, 或 GitHub API 报错). 之前的步骤已经完成, 所以表面上看发布成功了 | 查看 `publish-template` 的完整输出. 不 bump 版本号, 修好原因后重新运行 `publish-template`: 前面的步骤可以重复执行, 不会产生副作用 |
| 已发布的 `README.rst` 或 `cookiecutter.json` 的 `_template_version` 还是旧版本号 | bump 版本号之后没有重新运行 Sync | 重新运行 `sync`, 然后重新发布 |
| release 指向的版本号不对 | 发布脚本读取了 seed 的版本号 | 改为读取 tpl repo `pyproject.toml` (见 `08-versioning-and-release.md`) |


## L5: verify-release

| 现象 | 原因 | 修法 |
| :--- | :--- | :--- |
| 生成的是旧版本的内容 | 发布命令尚未全部执行, 或 push 失败 (`verify-release` 使用私有的克隆缓存, 不会读到 `~/.cookiecutters` 中的旧克隆) | 用 `git ls-remote` 确认远端分支已经指向刚发布的 commit |
| 已发布版本与本地生成的结果不一致, 但发布过程没有报错 | 本地 `tmp/cctpl/template/` 不是由刚发布的 seed commit 生成的 (例如之后运行过 `try-template`, 或 seed 有了新的改动) | 确认 seed 的 HEAD 等于 `release-history.rst` 中记录的 seed commit, 并且工作区干净, 然后重新运行 `make-template` 和 `verify-release` |
| 已发布版本与本地生成的结果不一致 | 发布时漏拷贝或多拷贝了文件 | 比较差异, 修 apply-template 或发布脚本, 作为 patch 重新发布 |
| preset 分支生成的值不是 preset 的值 | preset 分支的 `cookiecutter.json` 没有正确更新 | 检查 `presets/<name>.json` 和 preset 分支的生成过程 |
