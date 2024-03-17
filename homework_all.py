from bs4 import BeautifulSoup
from PIL import Image
import fitz
from docx import Document
import os
from io import BytesIO
import win32com.client
from tika import parser
from urllib.parse import urljoin

def get_content_from_html(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        soup = BeautifulSoup(html_content, 'html.parser')
        text = [p.text for p in soup.find_all('p')]
        images = []
        for img in soup.find_all('img'):
            if 'src' in img.attrs:
                img_path = os.path.join(os.path.dirname(file_path), img['src'])
                with open(img_path, 'rb') as img_file:
                    img_data = Image.open(img_file)
                    images.append(img_data)
    except Exception as e:
        print(f"Error processing HTML: {e}")
        text, images = [], []
    return {'text': text, 'images': images}

def get_content_from_pdf(file_path):
    text = []
    images = []
    try:
        doc = fitz.open(file_path)
        for i in range(len(doc)):
            page = doc.load_page(i)
            text.append(page.get_text())
            image_list = page.get_images(full=True)
            for img in image_list:
                xref = img[0]
                base = os.path.splitext(os.path.basename(file_path))[0]
                pix = fitz.Pixmap(doc, xref)
                if pix.n < 5:  # this is GRAY or RGB
                    img_file_path = f"{base}_{xref}.png"
                    pix.save(img_file_path)
                    images.append(img_file_path)
                else:  # CMYK: convert to RGB first
                    pix1 = fitz.Pixmap(fitz.csRGB, pix)
                    img_file_path = f"{base}_{xref}.png"
                    pix1.save(img_file_path)
                    images.append(img_file_path)
                    pix1 = None
                pix = None
    except Exception as e:
        print(f"Error processing PDF: {e}")
    return {'text': text, 'images': images}

def get_content_from_djvu(file_path):
    text = []
    images = []
    try:
        raw = parser.from_file(file_path)
        text.append(raw['content'])
        # 注意：Tika 库不支持从 DjVu 文件中提取图像
    except Exception as e:
        print(f"Error processing DjVu: {e}")
    return {'text': text, 'images': images}

def get_content_from_doc(file_path):
    text, images = [], []
    try:
        word = win32com.client.Dispatch("Word.Application")
        word.visible = False
        doc = word.Documents.Open(file_path)
        text = [para.Range.Text for para in doc.Paragraphs]
        # 注意：win32com 库不支持从 .doc 文件中提取图像
        doc.Close()
        word.Quit()
    except Exception as e:
        print(f"Error processing DOC: {e}")
    return {'text': text, 'images': images}

def get_content_from_docx(file_path):
    text, images = [], []
    try:
        doc = Document(file_path)
        text = [para.text for para in doc.paragraphs]
        for rel in doc.part.rels.values():
            if "image" in rel.reltype:
                image_data = rel.target_part.blob
                images.append(Image.open(BytesIO(image_data)))
    except Exception as e:
        print(f"Error processing DOCX: {e}")
    return {'text': text, 'images': images}

def save_images(images, output_dir, base_filename):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    counter = 0
    for i, image in enumerate(images):
        filename = f"{base_filename}_{i}"
        while os.path.exists(os.path.join(output_dir, filename + '.png')):
            counter += 1
            filename = f"{base_filename}_{counter}"
        image_file_path = os.path.join(output_dir, filename + '.png')
        if isinstance(image, str):  # image is a file path
            os.rename(image, image_file_path)
        else:  # image is a PIL Image object
            image.save(image_file_path)

def main(dir_path, output_dir):
    # 创建一个字典，映射文件扩展名到对应的处理函数
    handlers = {
        '.html': get_content_from_html,
        '.pdf': get_content_from_pdf,
        '.docx': get_content_from_docx,
        '.doc': get_content_from_doc,
        '.djvu': get_content_from_djvu,
    }

    # 遍历文件夹中的所有文件
    for filename in os.listdir(dir_path):
        file_path = os.path.join(dir_path, filename)

        # 获取文件扩展名
        _, ext = os.path.splitext(file_path)

        # 查找对应的处理函数
        handler = handlers.get(ext)

        if handler is None:
            print(f'Unsupported file type: {ext} for file: {filename}')
            continue

        # 调用处理函数
        content = handler(file_path)

        # 获取文件名（不包括扩展名）
        base_filename = os.path.splitext(filename)[0]

        # 保存图像
        save_images(content['images'], output_dir, base_filename)

        # 打印文本和图像数量
        print(f"Extracted {len(content['text'])} paragraphs and {len(content['images'])} images from file: {filename}")

        # 打印文本内容
        # for i, paragraph in enumerate(content['text']):
        #     print(f"Paragraph {i} from file {filename}: {paragraph}")

if __name__ == "__main__":
    dir_path = input('Enter the path to the directory: ')
    output_dir = input('Enter the output directory: ')
    main(dir_path, output_dir)
