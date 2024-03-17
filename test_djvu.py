import unittest
import os
import tempfile
import shutil
from homework_all import get_content_from_djvu

class TestGetContentFromDjvu(unittest.TestCase):
    def setUp(self):
        # 创建临时目录
        self.test_dir_text = tempfile.TemporaryDirectory()
        self.test_dir_image = tempfile.TemporaryDirectory()
        self.test_dir_both = tempfile.TemporaryDirectory()

        # 复制djvu文件到临时目录
        self.djvu_file_path_text = os.path.join(self.test_dir_text.name, 'test_text.djvu')
        shutil.copy('D:\\杨天宇\\硕士\\自动数据采集和处理系统\\homework1\\test\\djvu_text.djvu', self.djvu_file_path_text)

        self.djvu_file_path_image = os.path.join(self.test_dir_image.name, 'test_image.djvu')
        shutil.copy('D:\\杨天宇\\硕士\\自动数据采集和处理系统\\homework1\\test\\djvu_image.djvu', self.djvu_file_path_image)

        self.djvu_file_path_both = os.path.join(self.test_dir_both.name, 'test_both.djvu')
        shutil.copy('D:\\杨天宇\\硕士\\自动数据采集和处理系统\\homework1\\test\\djvu_all.djvu', self.djvu_file_path_both)

    def tearDown(self):
        # 删除临时目录
        self.test_dir_text.cleanup()
        self.test_dir_image.cleanup()
        self.test_dir_both.cleanup()

    def test_get_content_from_djvu_text(self):
        # 测试只有文字的djvu文件
        result = get_content_from_djvu(self.djvu_file_path_text)
        self.assertIsInstance(result, dict)
        self.assertIn('text', result)
        self.assertTrue(result['text'])  # 检查'text'的值是否非空
        self.assertFalse(result['images'])  # 检查'images'的值是否为空

    def test_get_content_from_djvu_image(self):
        # 测试只有图片的djvu文件
        result = get_content_from_djvu(self.djvu_file_path_image)
        self.assertIsInstance(result, dict)
        self.assertTrue(all(not x for x in result['text']))  # 检查'text'的值是否只包含空字符串
        self.assertFalse(result['images'])  # 检查'images'的值是否为空

    def test_get_content_from_djvu_both(self):
        # 测试既有文字又有图片的djvu文件
        result = get_content_from_djvu(self.djvu_file_path_both)
        self.assertIsInstance(result, dict)
        self.assertIn('text', result)
        self.assertIn('images', result)
        self.assertIsInstance(result['text'], list)
        self.assertIsInstance(result['images'], list)

if __name__ == '__main__':
    unittest.main()