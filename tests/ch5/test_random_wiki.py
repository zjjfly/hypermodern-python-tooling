import io

import pytest

from ch6.random_wikipedia_article import Article, show, fetch


# 为python代码编写单元测试首选pytest
# pytest会自动识别测试方法，即以test开头的python源文件中的test开头的方法
# 它还会重写其中的assert，让assert失败的时候输出的信息更多


# 使用fixture来向测试方法传入参数
@pytest.fixture
def file():
    return io.StringIO()


articles = [
    Article(),
    Article("test"),
    Article("Lorem Ipsum", "Lorem ipsum dolor sit amet."),
    Article(
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
        "Nulla mattis volutpat sapien, at dapibus ipsum accumsan eu.",
    ),
]


@pytest.mark.parametrize("article", articles)
def test_final_newline(article, file):
    show(article, file)
    assert file.getvalue().endswith("\n")


# 如果有很多测试方法都要使用articles，可以把fixture参数化
@pytest.fixture(params=articles)
def article2(request):
    return request.param


def test_final_newline2(article2, file):
    show(article2, file)
    assert file.getvalue().endswith("\n")


# 还可以直接定义一个类型为pytest.fixture的变量，它可以直接传入测试方法
def parametrized_fixture(*params):
    return pytest.fixture(params=params)(lambda request: request.param)


article3 = parametrized_fixture(
    Article(),
    Article("test"),
    Article("Lorem Ipsum", "Lorem ipsum dolor sit amet."),
    Article(
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
        "Nulla mattis volutpat sapien, at dapibus ipsum accumsan eu.",
    ),
)


def test_final_newline3(article3, file):
    show(article3, file)
    assert file.getvalue().endswith("\n")


# 也可以使用python标准库中的unittest包写单元测试
import unittest


# unittest的测试方法放在测试类中，这个类需要继承unittest.TestCase，方法名需要以test开头
class TestShow(unittest.TestCase):
    def setUp(self):
        self.article = Article("Lorem Ipsum", "Lorem ipsum dolor sit amet.")
        self.file = io.StringIO()

    def test_final_newline(self):
        show(self.article, self.file)
        self.assertEqual("\n", self.file.getvalue()[-1])


# 测试fetch方法，需要启动一个真正的HTTP服务器，首先使用contextmanager来实现

from contextlib import contextmanager
import http.server
import json
import threading


# 带contextmanager装饰器的方法，它的返回和with一起使用，其中使用yield返回一个变量
# 并会在退出with的时候执行yield后面的代码
@contextmanager
def serve(article):
    data = {"title": article.title, "extract": article.summary}
    body = json.dumps(data).encode()

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    with http.server.HTTPServer(("localhost", 0), Handler) as server:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        yield f"http://localhost:{server.server_port}"
        server.shutdown()
        thread.join()


def test_fetch(article2):
    with serve(article2) as url:
        assert article2 == fetch(url)


# 使用contextmanager的缺点是，如果要测试的方法很多，每次启停服务器比较耗时
# 解决这个问题的方法是使用fixture来实现，因为fixture可以是一个generator，这使得我们可以把关闭服务器的代码写在yield后面
# 首先把fixture的scope改成session，这样服务器就只会启停一次
@pytest.fixture(scope="session")
def http_server():
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            article = self.server.article
            data = {"title": article.title, "extract": article.summary}
            body = json.dumps(data).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    with http.server.HTTPServer(("localhost", 0), Handler) as server:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        yield server
        server.shutdown()
        thread.join()


# fixture也可以使用其他fixture，所以定义一个serve的fixture
@pytest.fixture
def serve2(http_server):
    def f(article):
        http_server.article = article
        return f"http://localhost:{http_server.server_port}"

    return f


def test_fetch2(article2, serve2):
    assert article2 == fetch(serve2(article2))


# 但相比自己实现，使用现有的pytest插件是更好的选择
# pytest-httpserver这个插件就提供了比httpserver更加强大的功能，且它是久经考验的
from pytest_httpserver import HTTPServer


# pytest-httpserver自带一个名为httpserver的fixture，还可以添加自定义的请求处理器，且支持基于HTTPS通信
@pytest.fixture
def serve3(httpserver: HTTPServer):
    def f(article):
        json_str = {"title": article.title, "extract": article.summary}
        httpserver.expect_request("/").respond_with_json(json_str)
        return httpserver.url_for("/")

    return f


def test_fetch3(article2, serve3):
    assert article2 == fetch(serve3(article2))


# 下面几个插件也很实用：
# pytest-xdist：可以在指定的数量的CPU上绑定worker线程，pytest之后会把测试随机分发到这些worker中执行，这可以加快执行测试的速度
# factory-boy：可以随机生成测试用的数据，这样就不需要像articles那样手写了，类似的还有hypothesis
# pytest-icdiff：可以高亮显示导致测试失败的不同的地方
# pytest-cov：使用coverage.py生产测试覆盖率报告
# typeguard：在运行时进行类型检查

from factory import Factory, Faker


class ArticleFactory(Factory):
    class Meta:
        model = Article

    title = Faker("sentence")
    summary = Faker("paragraph")


article4 = parametrized_fixture(*ArticleFactory.build_batch(10))


def test_trailing_blank_lines(article4, file):
    show(article4, file)
    assert not file.getvalue().endswith("\n\n")
