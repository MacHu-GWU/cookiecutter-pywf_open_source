<!--
使用说明 (给人看, agent 可忽略):
1. 用对应的 cookiecutter 模板生成新项目骨架, 放到旧 repo 的 tmp/ 下 (或别的目录, 改 SKELETON 即可).
2. 在旧 repo 的根目录打开 agent 会话.
3. 只编辑第 1 节 "本次任务变量": 开源项目 BASE_SKILL 填 pywf-oss-base, 内部私有项目填 pywf-priv-base; 1.1 写这个 repo 特有的要求.
4. 把整份文件作为第一条消息发给 agent. 第 2 节及之后对所有旧 repo 都一样, 不要改.
5. 完成后记得删除骨架目录, 不要把它提交进 repo.
-->

# Upgrade Old Repo to Template Conventions

## 1. 本次任务变量 (每次只改这一节)

- `BASE_SKILL`: pywf-oss-base
- `SKELETON`: `<repo-root>`/tmp
- `GOAL_CMD`: `mise run cov`, `mise build-doc`

### 1.1 个性化指导 (人工填写, 没有就写 "暂无")

- 我印象中这个 repo 的单元测试不会用到真实的 AWS 环境, 你顺便确认一下.

---

下文用 `<repo-root>` 指当前 repo 的根目录, 用 `BASE_SKILL`, `SKELETON`, `GOAL_CMD` 指第 1 节的值.

## 2. 背景

- 当前 repo 是一个很旧的 setup, 已经有业务代码.
- 我用 `BASE_SKILL` 对应的规范模板生成了一个新项目的骨架, 放在 `SKELETON`. 骨架有规范, 没有业务逻辑.

## 3. 开工前先做

1. 用 Skill 工具加载 `BASE_SKILL`, 读和本任务相关的 reference.
2. 对比 `<repo-root>` 和 `SKELETON` 的目录结构和配置文件, 列出差异和合并计划, 再动手.

## 4. 任务

把 `SKELETON` 下的规范合并进 `<repo-root>`. 规范冲突时尽可能以 `SKELETON` 为准.

## 5. 边界

- 业务代码只做为了符合规范和跑通 `GOAL_CMD` 必需的改动, 不改业务逻辑.
- 文档暂时不动, 我最后会单独改.
- 删除 `<repo-root>` 中已有的文件前先告诉我.
- 不运行任何会改变云端服务 (GitHub, PyPI, AWS 等) 状态的命令.
- 第 1.1 节的个性化指导优先于本文其他内容.

## 6. 验收标准

- 在 `<repo-root>` 下 `GOAL_CMD` 能跑通.
- 第 1.1 节里每一条都有明确的回答或处理结果.
