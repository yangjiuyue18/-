import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import PyPDF2
from pdf2image import convert_from_path
from docx import Document
import os

def get_content_from_html(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = [p.text for p in soup.find_all('p')]
        images = []
        for img in soup.find_all('img'):
            if 'src' in img.attrs:
                img_url = img['src']
                try:
                    img_response = requests.get(img_url)
                    img_data = Image.open(BytesIO(img_response.content))
                    images.append(img_data)
                except Exception as e:
                    print(f"Error downloading image {img_url}: {e}")
        return {'text': text, 'images': images}
    except Exception as e:
        print(f"Error processing HTML content from {url}: {e}")
        return {'text': [], 'images': []}

def get_content_from_pdf(file_path):
    try:
        with open(file_path, 'rb') as pdf_file_obj:
            pdf_reader = PyPDF2.PdfFileReader(pdf_file_obj)
            text = [pdf_reader.getPage(page_num).extractText() for page_num in range(pdf_reader.numPages)]
        images = convert_from_path(file_path)
        return {'text': text, 'images': images}
    except Exception as e:
        print(f"Error processing PDF content from {file_path}: {e}")
        return {'text': [], 'images': []}

def get_content_from_docx(file_path):
    try:
        doc = Document(file_path)
        text = [para.text for para in doc.paragraphs]
        images = []
        for rel in doc.part.rels.values():
            if "image" in rel.reltype:
                image_data = rel.target_part.blob
                images.append(Image.open(BytesIO(image_data)))
        return {'text': text, 'images': images}
    except Exception as e:
        print(f"Error processing DOCX content from {file_path}: {e}")
        return {'text': [], 'images': []}

def save_images(images, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for i, image in enumerate(images):
        image_file_path = os.path.join(output_dir, f'image_{i}.png')
        image.save(image_file_path)

def main(file_path, output_dir):
    _, ext = os.path.splitext(file_path)
    function_map = {
        '.html': get_content_from_html,
        '.pdf': get_content_from_pdf,
        '.docx': get_content_from_docx
    }

    if ext.lower() in function_map:
        content = function_map[ext.lower()](file_path)
        print('Text:', content['text'])
        print('Images:', len(content['images']))
        save_images(content['images'], output_dir)
    else:
        print(f'Unsupported file type: {ext}')

if __name__ == "__main__":
    file_path = input('Enter the path to the file: ')
    output_dir = input('Enter the output directory: ')
    main(file_path, output_dir)
