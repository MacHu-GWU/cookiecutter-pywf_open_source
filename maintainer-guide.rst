维护指南 (Maintainer Guide)
==============================================================================

前置条件
------------------------------------------------------------------------------
- 当 `cookiecutter_pywf_open_source_demo-project <https://github.com/MacHu-GWU/cookiecutter_pywf_open_source_demo-project>`_ 两个项目都趋于稳定之后再来修改此项目模板
- 由于 `cookiecutter_pywf_open_source_demo-project <https://github.com/MacHu-GWU/cookiecutter_pywf_open_source_demo-project>`_ 是我们的 Seed project, 而我们这个 Template 的版本是跟 Seed project 的版本保持一致的

工作流程
------------------------------------------------------------------------------
1. **在 Seed 项目中进行修改**: 所有功能性的修改都应该在 Seed 项目 (``$HOME/GitHub/cookiecutter_pywf_open_source_demo-project``) 中完成并测试

2. **生成模板**: 运行 ``mise run make-template``

   - 该脚本将 Seed 项目反向转换为 cookiecutter 模板
   - 生成的模板文件存放在 ``tmp/`` 目录下
   - 脚本会自动替换具体值为 cookiecutter 占位符 (如 ``{{ cookiecutter.package_name }}``)

3. **发布模板**: 运行 ``mise run publish-template``

   - 自动将模板从 ``tmp/`` 目录拷贝到模板目录 (``{{ cookiecutter.package_name }}-project/``)
   - 自动 commit 并 push 到 ``main`` 分支
   - 自动 merge ``main`` 到特殊分支 (如 ``sanhe``)
   - 自动创建或更新 GitHub Release

可用的 Mise Tasks
------------------------------------------------------------------------------
运行 ``mise tasks ls`` 查看所有可用任务:

- ``mise run make-template`` - 从 Seed 项目生成模板
- ``mise run publish-template`` - 发布模板到 GitHub
- ``mise run check-seed-values`` - 检查 Seed 项目的值是否正确
- ``mise run check-template`` - 检查生成的模板是否正确

技术架构
------------------------------------------------------------------------------
- **Template Repository**: ``cookiecutter-pywf_open_source`` (当前仓库)
- **Seed Repository**: ``cookiecutter_pywf_open_source_demo-project``
- **Automation Library**: ``pywf_open_source-project``
- **工具链**: mise-en-place (任务管理) + uv (包管理)
