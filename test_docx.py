import unittest
import os
import tempfile
import shutil
from homework_all import get_content_from_docx

class TestGetContentFromDocx(unittest.TestCase):
    def setUp(self):
        # 创建一个临时目录
        self.test_dir = tempfile.TemporaryDirectory()

        # 复制docx文件到临时目录
        self.docx_file_path = os.path.join(self.test_dir.name, 'test.docx')
        shutil.copy('D:\\杨天宇\\硕士\\自动数据采集和处理系统\\homework1\\test\\docx_chinese.docx', self.docx_file_path)

    def tearDown(self):
        # 删除临时目录
        self.test_dir.cleanup()

    def test_get_content_from_docx(self):
        # 测试get_content_from_docx函数
        result = get_content_from_docx(self.docx_file_path)
        self.assertIsInstance(result, dict)
        self.assertIn('text', result)
        self.assertIn('images', result)
        self.assertIsInstance(result['text'], list)
        self.assertIsInstance(result['images'], list)

if __name__ == '__main__':
    unittest.main()