import unittest
import os
import tempfile
import shutil
from homework_all import get_content_from_pdf

class TestGetContentFromPdf(unittest.TestCase):
    def setUp(self):
        # 创建临时目录
        self.test_dir_text = tempfile.TemporaryDirectory()
        self.test_dir_image = tempfile.TemporaryDirectory()
        self.test_dir_both = tempfile.TemporaryDirectory()

        # 复制PDF文件到临时目录
        self.pdf_file_path_text = os.path.join(self.test_dir_text.name, 'test_text.pdf')
        shutil.copy('D:\\杨天宇\\硕士\\自动数据采集和处理系统\\homework1\\test\\pdf_text.pdf', self.pdf_file_path_text)

        self.pdf_file_path_image = os.path.join(self.test_dir_image.name, 'test_image.pdf')
        shutil.copy('D:\\杨天宇\\硕士\\自动数据采集和处理系统\\homework1\\test\\pdf_image.pdf', self.pdf_file_path_image)

        self.pdf_file_path_both = os.path.join(self.test_dir_both.name, 'test_both.pdf')
        shutil.copy('D:\\杨天宇\\硕士\\自动数据采集和处理系统\\homework1\\test\\pdf_all.pdf', self.pdf_file_path_both)

    def tearDown(self):
        # 删除临时目录
        self.test_dir_text.cleanup()
        self.test_dir_image.cleanup()
        self.test_dir_both.cleanup()

        # 删除生成的图片
        for file_name in os.listdir('.'):
            if file_name.endswith('.png'):
                os.remove(file_name)

    def test_get_content_from_pdf_text(self):
        # 测试只有文字的PDF文件
        result = get_content_from_pdf(self.pdf_file_path_text)
        self.assertIsInstance(result, dict)
        self.assertIn('text', result)
        self.assertTrue(result['text'])  # 检查'text'的值是否非空
        self.assertFalse(result['images'])  # 检查'images'的值是否为空

    def test_get_content_from_pdf_image(self):
        # 测试只有图片的PDF文件
        result = get_content_from_pdf(self.pdf_file_path_image)
        self.assertIsInstance(result, dict)
        self.assertTrue(all(x.isspace() for x in result['text']))  # 检查'text'的值是否只包含空格和换行符
        self.assertTrue(result['images'])  # 检查'images'的值是否非空
    def test_get_content_from_pdf_both(self):
        # 测试既有文字又有图片的PDF文件
        result = get_content_from_pdf(self.pdf_file_path_both)
        self.assertIsInstance(result, dict)
        self.assertIn('text', result)
        self.assertIn('images', result)
        self.assertIsInstance(result['text'], list)
        self.assertIsInstance(result['images'], list)

if __name__ == '__main__':
    unittest.main()