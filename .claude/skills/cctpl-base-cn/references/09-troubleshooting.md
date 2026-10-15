# Troubleshooting

本文按出错的位置列出常见故障: 现象, 原因, 修法. 修法遵守 `05-parameterization.md` 和 `06-safety-rules.md`; 本文只给方向, 不重复规则. 前置阅读: `04-mise-task-contract.md`, `05-parameterization.md`, `08-verification.md`.

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
| cookiecutter 报 Jinja 语法错误 | seed 中的 Jinja 风格语法没有被转义 | 确认参数化库版本支持自动转义; 不在 seed 中手工转义 (见 `05-parameterization.md`) |
| hooks 报错 | hooks 逻辑与新变量或新文件不匹配 | 修 tpl repo 的 `hooks/`; 对相关 choice 做 choice coverage |
| 生成结果中有未解析的 `cookiecutter.` 引用 | custom placeholder 引用了不存在的变量, 或拼写错误 | 修 parameter 的 custom placeholder, 确认引用的变量在 `cookiecutter.json` 中 |
| 某个文件内容原样保留了 `{{ cookiecutter.xxx }}` | 该文件是 no_render, 但它又需要被渲染 | 移出 no_render |


## L3: check-roundtrip

过度替换 (不该替换的被替换了) 不会让 round trip 失败, 见 `05-parameterization.md` 的 What Round Trip Cannot See. 它的现象和修法列在本文的 Review 一节.

| 现象 | 原因 | 修法 |
| :--- | :--- | :--- |
| 派生形态与 seed 不一致 | 派生计算 (例如 slugify) 的结果与 seed 中的实际写法不同 | 修 custom placeholder 的计算方式, 或调整 seed 中的写法使之可推导 |
| 文件缺失 | 文件被 exclude 规则误伤 | 收窄 exclude 规则 |
| 文件多出 | seed 中的临时文件或本地文件没有被 exclude | 补充 exclude 规则, 或把文件从 seed 中清理掉 |
| 只有换行符或文件末尾换行不同 | 参数化统一写成 LF, 而 seed 中的文件是 CRLF | 统一 seed 中的换行符 (seed 的 `.gitattributes`) |
| 文件内容相同但权限不同 | 可执行权限在生成过程中丢失 | 用 hooks 恢复权限, 或在 round trip 比较中声明该差异 |


## L4: test-output

| 现象 | 原因 | 修法 |
| :--- | :--- | :--- |
| 任何 mise 命令都失败, 报 secret 或 token 相关错误 | 生成项目的 `[env]` 用占位的 token 字段名读取 secret | 按 `08-verification.md` 的 Secrets 规则, 绕过 mise 直接调用工具链 |
| seed 自测通过, 生成项目测试失败 | 项目中写死了只对 seed 成立的东西 (例如 seed 的仓库地址, 文档站点名), 或默认值本身不合法 | 让该内容也参数化; 或修改默认值 |
| 依赖安装失败 | 生成项目没有 lock 文件, 全新 resolve 时某个依赖的最新版本不兼容 | 在 seed 的依赖声明中收紧版本范围, 在 seed 中验证后重新 Sync |


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
| 已发布的 `README.rst` 或 `cookiecutter.json` 的 `_template_version` 还是旧版本号 | bump 版本号之后没有重新运行 Sync | 重新运行 `sync`, 然后重新发布 |
| release 指向的版本号不对 | 发布脚本读取了 seed 的版本号 | 改为读取 tpl repo `pyproject.toml` (见 `07-versioning-and-release.md`) |


## L5: verify-release

| 现象 | 原因 | 修法 |
| :--- | :--- | :--- |
| 生成的是旧版本的内容 | cookiecutter 使用了本地缓存的旧克隆, 或发布命令尚未全部执行 | 确认清除了缓存, 确认 push 已完成 |
| 已发布版本与本地生成的结果不一致 | 发布时漏拷贝或多拷贝了文件 | 比较差异, 修 apply-template 或发布脚本, 作为 patch 重新发布 |
| preset 分支生成的值不是 preset 的值 | preset 分支的 `cookiecutter.json` 没有正确更新 | 检查 `presets/<name>.json` 和 preset 分支的生成过程 |
