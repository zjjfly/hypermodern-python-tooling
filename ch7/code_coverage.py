# Coverage.py的原理：Python解释器可以注册一个trace函数（使用sys.settrace），它会在每一行代码执行的时候被调用
# 它还会在进入或退出函数，抛出异常的时候被调用。实际上，Python标准库带了一个统计覆盖率的工具，在trace模块中。
# python -m trace --count --summary --missing -C coverage --module pytest
# 它会对标准库，第三方库和你的代码都进行覆盖率统计，并输出到控制台和coverage文件夹中（每个模块有一个.cover文件）。
# 但实际项目中，还是使用Coverage.py比较好

# 可以在pyproject.toml中直接配置Coverage.py的行为，在tool.coverage的tab中
# 使用命令运行： uv run coverage run -m pytest，会生成一个.coverage文件，这里存储了测试覆盖率数据
# 使用命令查看报告： uv run coverage report

# 对于那些要支持多版本的代码（如ch4/random_wikipedia_article.py的7-10行），需要切换不同的环境，多次运行覆盖率分析
# Coverage.py默认是覆盖现有的覆盖率数据的，所以要要在命令中加入--append参数让后面执行的覆盖率分析数据追加到现有的数据中
# 但是，使用append模式的问题是，你需要在运行新的测试覆盖率分析之前必须使用coverage erase命令清除现有的数据
# 更好的选择是在配置中加上parallel=true，它的作用是让每次覆盖率分析产生的结果存放在不同的文件中。
# 但覆盖率报告只能从一个文件中生成，所以需要使用coverage combine命令合并多个文件为一个文件

# 如果要分析main方法和__main__模块的覆盖率，则需要在子进程中运行覆盖率分析
# 可以使用pytest-cov这个插件，它对Coverage.py进行了封装。还可以使用.pth文件，把下面这行代码放在里面，并把它安装到site-packages中
# import coverage; coverage.process_startup()
