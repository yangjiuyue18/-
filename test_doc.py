import unittest
import os
import tempfile
import shutil
from homework_all import get_content_from_doc

class TestGetContentFromDoc(unittest.TestCase):
    def setUp(self):
        # 创建临时目录
        self.test_dir_text = tempfile.TemporaryDirectory()
        self.test_dir_image = tempfile.TemporaryDirectory()
        self.test_dir_both = tempfile.TemporaryDirectory()

        # 复制doc文件到临时目录
        self.doc_file_path_text = os.path.join(self.test_dir_text.name, 'test_text.doc')
        shutil.copy('D:\\杨天宇\\硕士\\自动数据采集和处理系统\\homework1\\test\\doc_text.doc', self.doc_file_path_text)

        self.doc_file_path_image = os.path.join(self.test_dir_image.name, 'test_image.doc')
        shutil.copy('D:\\杨天宇\\硕士\\自动数据采集和处理系统\\homework1\\test\\doc_image.doc', self.doc_file_path_image)

        self.doc_file_path_both = os.path.join(self.test_dir_both.name, 'test_both.doc')
        shutil.copy('D:\\杨天宇\\硕士\\自动数据采集和处理系统\\homework1\\test\\doc_all.doc', self.doc_file_path_both)

    def tearDown(self):
        # 删除临时目录
        self.test_dir_text.cleanup()
        self.test_dir_image.cleanup()
        self.test_dir_both.cleanup()

    def test_get_content_from_doc_text(self):
        # 测试只有文字的doc文件
        result = get_content_from_doc(self.doc_file_path_text)
        self.assertIsInstance(result, dict)
        self.assertIn('text', result)
        self.assertTrue(result['text'])  # 检查'text'的值是否非空
        self.assertFalse(result['images'])  # 检查'images'的值是否为空

    def test_get_content_from_doc_image(self):
        # 测试只有图片的doc文件
        result = get_content_from_doc(self.doc_file_path_image)
        self.assertIsInstance(result, dict)
        self.assertTrue(all(x.isspace() or not x.isprintable() for x in result['text']))  # 检查'text'的值是否只包含空格、换行符和其他非打印字符
        self.assertFalse(result['images'])  # 检查'images'的值是否非空

    def test_get_content_from_doc_both(self):
        # 测试既有文字又有图片的doc文件
        result = get_content_from_doc(self.doc_file_path_both)
        self.assertIsInstance(result, dict)
        self.assertIn('text', result)
        self.assertIn('images', result)
        self.assertIsInstance(result['text'], list)
        self.assertIsInstance(result['images'], list)

if __name__ == '__main__':
    unittest.main()