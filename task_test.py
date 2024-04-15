import unittest
from unittest.mock import patch
from task import is_internal, add_subdomain, is_document, crawl, start_crawl, stats, internal_subdomains, visited_urls, to_visit_urls, domain, headers
from urllib.parse import urlparse, urljoin
import time

class TestWebCrawler(unittest.TestCase):

    def setUp(self):
        # 测试开始前的初始化工作
        # Инициализация до начала тестирования
        self.start_url = "https://example.com"
        self.domain = urlparse(self.start_url).netloc
        global domain
        domain = self.domain
        visited_urls.clear()
        to_visit_urls.clear()
        internal_subdomains.clear()
        stats.clear()
        stats.update({
            "total_pages": 0,
            "all_links": 0,
            "internal_links": 0,
            "external_links": 0,
            "broken_links": 0,
            "internal_subdomains": 0,
            "external_resources_links": 0,
            "unique_external_resources": 0,
            "unique_documents_links": 0,
            "subdomains": set(),
            "external_domains": set(),
        })
    def test_is_internal_subdomain(self):
        # 测试 is_internal 函数是否能正确识别同一域名的子域名
        # Проверьте, правильно ли функция is_internal идентифицирует поддомены с одинаковым доменным именем
        add_subdomain("https://blog.example.com")
        url = "https://blog.example.com"
        self.assertTrue(is_internal(url))

    def test_is_document_pdf(self):
        # 测试 is_document 函数是否能正确识别 PDF 文档链接
        # Проверьте, правильно ли функция is_document распознает ссылки на PDF-документы
        url = "https://example.com/document.pdf"
        self.assertTrue(is_document(url))

    def test_safe_request_with_mock(self):
        # 测试 crawl 函数是否能正确地发送 HTTP 请求
        # Проверьте функцию crawl, чтобы убедиться, что она правильно отправляет HTTP-запросы
        url = "https://example.com"
        with patch('task.requests.get') as mocked_get:
            mocked_get.return_value.status_code = 200
            mocked_get.return_value.text = '<html></html>'
            crawl(url, 0)
            mocked_get.assert_called_once_with(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
            }, timeout=5)

    def test_crawl_updates_stats_correctly(self):
        # 测试 crawl 函数是否能正确地更新统计数据
        # Проверьте правильность обновления статистики функцией crawl
        with patch('task.requests.get') as mocked_get:
            mocked_get.return_value.status_code = 200
            mocked_get.return_value.text = '<a href="https://example.com/page1">Page 1</a>'
            crawl(self.start_url, 0)
            self.assertEqual(stats["total_pages"], 1)
            self.assertEqual(stats["all_links"], 1)
            self.assertEqual(stats["internal_links"], 0)
            self.assertEqual(stats["external_links"], 1)

    def test_crawl_ignores_visited_urls(self):
        # 测试 crawl 函数是否能正确地忽略已访问过的链接
        # Проверьте, корректно ли функция ползания игнорирует посещенные ссылки
        visited_urls.add("https://example.com/page1")
        crawl("https://example.com/page1", 0)
        self.assertEqual(stats["total_pages"], 0)  # URL 已被访问，因此不应再次抓取

    def test_add_subdomain_effectively(self):
        # 测试 add_subdomain 函数是否能正确地添加子域名
        # Проверьте, что функция add_subdomain корректно добавляет субдомен
        add_subdomain("https://blog.example.com")
        self.assertIn("blog.example.com", internal_subdomains)

    def test_is_internal_same_domain(self):
        # 测试 is_internal 函数是否能正确地识别同一域名的链接
        # Проверьте, правильно ли функция is_internal идентифицирует ссылки на одно и то же доменное имя
        url = "https://example.com/page"
        self.assertTrue(is_internal(url))


    def test_external_link_detected(self):
        # 测试 is_internal 函数是否能正确地识别外部链接
        # Проверьте, что функция is_internal правильно распознает внешние ссылки
        url = "https://external.com"
        self.assertFalse(is_internal(url))

    def test_start_crawl_with_depth_control(self):
        # 测试 start_crawl 函数是否能正确地控制爬取深度
        # Проверьте, что функция start_crawl правильно контролирует глубину проползания
        with patch('task.crawl') as mocked_crawl:
            start_crawl(self.start_url)
            mocked_crawl.assert_called()

    def test_unique_document_links_tracking(self):
        # 测试爬虫是否能正确地跟踪唯一的文档链接
        # Проверьте, может ли краулер правильно переходить по уникальным ссылкам на документы
        with patch('task.requests.get') as mocked_get:
            mocked_get.return_value.status_code = 200
            mocked_get.return_value.text = '<a href="https://example.com/unique_document.pdf">Unique Document</a>'
            crawl("https://example.com", 0)
            self.assertEqual(stats["unique_documents_links"], 0)

    def test_link_deduplication_efficiency(self):
        # 测试爬虫是否能有效地去除重复的链接
        # Проверьте, эффективно ли краулер удаляет дубликаты ссылок
        with patch('task.requests.get') as mocked_get:
            mocked_get.return_value.status_code = 200
            mocked_get.return_value.text = '<a href="https://example.com/page1">Page 1</a>' * 1000  # 生成1000个重复链接
            start_time = time.time()
            crawl("https://example.com", 0)
            duration = time.time() - start_time
            self.assertTrue(duration < 15)  
            self.assertEqual(len(visited_urls), 1) 
    def test_user_agent_sent_correctly(self):
        # 测试爬虫是否能正确地发送 User-Agent
        # Проверьте, правильно ли краулер отправляет User-Agent
        with patch('task.requests.get') as mocked_get:
            mocked_get.return_value.status_code = 200
            mocked_get.return_value.text = '<html></html>'
            crawl("https://example.com", 0)
            args, kwargs = mocked_get.call_args
            self.assertEqual(kwargs['headers']['User-Agent'], headers['User-Agent'])

    def test_ignore_non_html_content(self):
        # 测试爬虫是否能正确地忽略非 HTML 内容
        # Проверьте, правильно ли краулер игнорирует не-HTML-контент
        with patch('task.requests.get') as mocked_get:
            mocked_response = unittest.mock.Mock()
            mocked_response.status_code = 200
            mocked_response.headers = {'Content-Type': 'image/jpeg'}
            mocked_response.text = ''  # 设置返回空字符串
            mocked_get.return_value = mocked_response
            crawl("https://example.com/image.jpg", 0)
            self.assertEqual(len(visited_urls), 1) # 只有初始页面被访问


    def test_depth_limitation(self):
        # 测试爬虫是否能正确地限制爬取深度
        # Проверьте, правильно ли краулер ограничивает глубину проползания
        to_visit_urls.append(("https://example.com/level1", 1))
        to_visit_urls.append(("https://example.com/level2", 2))  # 应该不被访问
        start_crawl("https://example.com")
        self.assertNotIn("https://example.com/level2", visited_urls)

    def test_ignore_invalid_links(self):
        # 测试爬虫是否能正确地忽略无效的链接
        # Проверьте, правильно ли краулер игнорирует недействительные ссылки
        with patch('task.requests.get') as mocked_get:
            mocked_get.return_value.status_code = 200
            mocked_get.return_value.text = '<a href="http://%gz">Invalid Link</a>'
            crawl("https://example.com", 0)
            self.assertEqual(len(visited_urls), 1)  # 只有初始页面被访问

    def test_ignore_empty_links(self):
        # 测试爬虫是否能正确地忽略空的链接
        # Проверьте, правильно ли краулер игнорирует пустые ссылки
        with patch('task.requests.get') as mocked_get:
            mocked_get.return_value.status_code = 200
            mocked_get.return_value.text = '<a href="">Empty Link</a>'
            crawl("https://example.com", 0)
            self.assertEqual(len(visited_urls), 1)  # 只有初始页面被访问

if __name__ == '__main__':
    unittest.main()
