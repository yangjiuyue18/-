import requests
from bs4 import BeautifulSoup
from PIL import Image
import fitz
from docx import Document
import os
from io import BytesIO
import win32com.client
from tika import parser

def get_content_from_html(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises HTTPError for bad responses
        soup = BeautifulSoup(response.text, 'html.parser')
        text = [p.text for p in soup.find_all('p')]
        images = []
        for img in soup.find_all('img'):
            if 'src' in img.attrs:
                img_url = img['src']
                img_response = requests.get(img_url)
                img_response.raise_for_status()
                img_data = Image.open(BytesIO(img_response.content))
                images.append(img_data)
    except requests.RequestException as e:
        print(f"Request error: {e}")
        text, images = [], []
    return {'text': text, 'images': images}

def get_content_from_pdf(file_path):
    text = []
    images = []
    try:
        doc = fitz.open(file_path)
        for page in doc:
            text.append(page.getText())
            image_list = page.getImageList()
            for img in image_list:
                xref = img[0]
                base = os.path.splitext(os.path.basename(file_path))[0]
                pix = fitz.Pixmap(doc, xref)
                if pix.n < 5:       # this is GRAY or RGB
                    pix.writePNG(f"{base}_{xref}.png")
                    images.append(f"{base}_{xref}.png")
                else:               # CMYK: convert to RGB first
                    pix1 = fitz.Pixmap(fitz.csRGB, pix)
                    pix1.writePNG(f"{base}_{xref}.png")
                    images.append(f"{base}_{xref}.png")
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

def save_images(images, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for i, image in enumerate(images):
        base_filename = f"image_{i}"
        filename = base_filename
        counter = 0
        while os.path.exists(os.path.join(output_dir, filename + '.png')):
            counter += 1
            filename = base_filename + f"_{counter}"
        image_file_path = os.path.join(output_dir, filename + '.png')
        image.save(image_file_path)

def main(file_path, output_dir):
    # 创建一个字典，映射文件扩展名到对应的处理函数
    handlers = {
        '.html': get_content_from_html,
        '.pdf': get_content_from_pdf,
        '.docx': get_content_from_docx,
        '.doc': get_content_from_doc,
        '.djvu': get_content_from_djvu,
    }

    # 获取文件扩展名
    _, ext = os.path.splitext(file_path)

    # 查找对应的处理函数
    handler = handlers.get(ext)

    if handler is None:
        print(f'Unsupported file type: {ext}')
        return

    # 调用处理函数
    content = handler(file_path)

    # 保存图像
    save_images(content['images'], output_dir)

    # 打印文本和图像数量
    print(f"Extracted {len(content['text'])} paragraphs and {len(content['images'])} images")

if __name__ == "__main__":
    file_path = input('Enter the path to the file: ')
    output_dir = input('Enter the output directory: ')
    main(file_path, output_dir)
