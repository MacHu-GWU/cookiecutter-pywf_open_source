维护指南 (Maintainer Guide)
==============================================================================

前置条件
------------------------------------------------------------------------------
- 当 `cookiecutter_pywf_open_source_demo-project <https://github.com/MacHu-GWU/cookiecutter_pywf_open_source_demo-project>`_ 两个项目都趋于稳定之后再来修改此项目模板
- 由于 `cookiecutter_pywf_open_source_demo-project <https://github.com/MacHu-GWU/cookiecutter_pywf_open_source_demo-project>`_ 是我们的 Seed project, 而我们这个 Template 的版本是跟 Seed project 的版本保持一致的

工作流程
------------------------------------------------------------------------------

**标准工作流 (推荐)**

一次性执行完整流程:

.. code-block:: bash

    mise run all

这个命令会按顺序执行: make-template → check-seed-values → test-template → check-output → publish-template

**详细步骤说明**

1. **在 Seed 项目中进行修改**

   所有功能性的修改都应该在 Seed 项目 (``$HOME/GitHub/cookiecutter_pywf_open_source_demo-project``) 中完成并测试

2. **生成模板**

   .. code-block:: bash

       mise run make-template

   - 该脚本将 Seed 项目反向转换为 cookiecutter 模板
   - 生成的模板文件存放在 ``tmp/`` 目录下
   - 脚本会自动替换具体值为 cookiecutter 占位符 (如 ``{{ cookiecutter.package_name }}``)

3. **检查 Seed 值残留**

   .. code-block:: bash

       mise run check-seed-values

   - 检查生成的模板中是否还有未被替换的 Seed 项目具体值
   - 确保所有具体值都已被 cookiecutter 占位符替换

4. **测试模板生成**

   .. code-block:: bash

       mise run test-template

   - 使用默认值运行 cookiecutter，测试模板是否能正常生成项目
   - 输出目录: ``tmp/output/``

5. **检查输出占位符**

   .. code-block:: bash

       mise run check-output

   - 检查生成的项目中是否有未解析的 cookiecutter 占位符 (如 ``{{ cookiecutter.xxx }}``)
   - 确保所有占位符都已正确替换

6. **发布模板**

   .. code-block:: bash

       mise run publish-template

   - 自动将模板从 ``tmp/`` 目录拷贝到模板目录 (``{{ cookiecutter.package_name }}-project/``)
   - 自动 commit 并 push 到 ``main`` 分支
   - 自动 merge ``main`` 到特殊分支 (如 ``sanhe``)
   - 自动创建或更新 GitHub Release

可用的 Mise Tasks
------------------------------------------------------------------------------
运行 ``mise tasks ls`` 查看所有可用任务:

**环境管理**

- ``mise run venv-create`` - 创建 Python 虚拟环境
- ``mise run venv-remove`` - 删除虚拟环境
- ``mise run inst`` - 安装所有 Python 依赖
- ``mise run export`` - 导出依赖到 requirements.txt 文件

**模板生成与验证**

- ``mise run make-template`` - 从 Seed 项目生成 cookiecutter 模板
- ``mise run check-seed-values`` - 检查模板中是否有残留的 Seed 项目值
- ``mise run test-template`` - 测试模板生成 (用默认值运行 cookiecutter)
- ``mise run check-output`` - 检查生成的项目中是否有未解析的占位符

**发布**

- ``mise run publish-template`` - 发布模板到 GitHub (commit, push, merge, release)
- ``mise run update-github-metadata`` - 更新 GitHub 仓库描述和主页

**一键执行**

- ``mise run all`` - 一次性执行: make-template → check-seed-values → test-template → check-output → publish-template

技术架构
------------------------------------------------------------------------------
- **Template Repository**: ``cookiecutter-pywf_open_source`` (当前仓库)
- **Seed Repository**: ``cookiecutter_pywf_open_source_demo-project``
- **工具链**: mise-en-place (任务管理) + uv (包管理)
