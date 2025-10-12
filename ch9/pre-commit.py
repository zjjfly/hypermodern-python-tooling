# pre-commit是一个为项目设置Git钩子的工具
# 它可以在提交代码之前自动运行一些检查和格式化工具，确保代码质量
# 通过配置pre-commit，可以在每次提交代码前运行代码风格检查、静态分析、安全扫描等任务
# 这有助于捕捉潜在的问题，减少代码审查的工作量
# pre-commit支持多种编程语言和工具，并且可以轻松集成到现有的开发工作流中

# 使用下面的脚步可以安装pre-commit：
# pipx install pre-commit

# 安装完成后，可以在项目根目录创建一个.pre-commit-config.yaml文件来配置pre-commit钩子
# 其中会有hooks的配置项，指定要运行的检查工具和它们的参数。其中会有代码的地址和版本号
# 第一次在项目中运行pre-commit的时候，它会根据配置文件下载代码并安装到一个单独的环境中
# 可以使用下面的命令手动运行pre-commit：
# pre-commit run --all-files
# --all-files参数表示对所有文件运行配置的检查工具
# 之后每次提交代码时，pre-commit会自动运行这些工具，并根据它们的结果决定是否允许提交

# hook的原理是：在hook的代码中，有一个文件.pre-commit-hooks.yaml，它定义了这个hook的元信息
# 包括id、name、description、entry（入口点）、language（使用的语言）、types（适用的文件类型）等
# pre-commit根据这些信息来识别和运行hook
# 例如，entry指定了运行hook时调用的命令或脚本
# language指定了hook使用的编程语言环境，比如python、node等
# types指定了hook适用的文件类型，比如python、javascript等
# types_or指定了更具体的文件后缀，可以用来过滤文件
# args指定了传递给entry的参数，可以在.pre-commit-config.yaml中覆盖这些参数
# 当pre-commit运行时，它会根据这些信息来设置环境并执行相应的命令
# 可以参考https://github.com/astral-sh/ruff-pre-commit/blob/main/.pre-commit-hooks.yaml

# 现代的linter是可以自动修复发现的问题的，按惯例，大多是pre-commmit的hooks默认会启用自动修复。
# 但要注意，要确保在自动修复之前要提交未保存的更改。
# Ruff的pre-commit配置中，需要在args中添加--fix参数来启用自动修复功能，并且最好加上--exit-non-zero-on-fix参数
# 这样如果Ruff修复了任何问题，pre-commit会返回非零退出代码，从而阻止提交
# 这样可以确保开发者在提交之前查看并确认自动修复的更改

# 使用pre-commit install来安装Git钩子
# 这样每次执行git commit时，pre-commit都会自动运行配置的检查工具
# 如果想更新pre-commit钩子，可以使用pre-commit autoupdate命令
# 这会根据配置文件中的版本号更新所有的hook到最新版本
# 也可以使用pre-commit clean命令来清理pre-commit的缓存
# 这会删除pre-commit下载的所有hook代码和环境
# 这样可以节省磁盘空间，但下次运行pre-commit时会重新下载hook

# Git除了pre-commit钩子外，还有其他类型的钩子，比如pre-push、commit-msg等
# 可以根据需要在.pre-commit-config.yaml中配置这些钩子
# 例如，可以配置一个commit-msg钩子来检查提交信息的格式
# 这样可以确保所有的提交信息都符合项目的规范，相关的hook可以参考gitlint和commitlint

# 如果想跳过pre-commit检查，可以使用git commit --no-verify或git commit -n命令
# 但不建议经常使用这个选项，因为它会绕过所有的检查，所以可以使用SKIP环境变量来有选择地跳过某些hook
# 例如，SKIP=ruff git commit会跳过ruff
