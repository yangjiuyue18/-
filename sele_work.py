from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from lxml import etree
import time
import re

# 配置Chrome选项，设置为无头模式
# Настройте параметры Chrome, перейдите в безголовый режим
chrome_options = Options()
chrome_options.add_argument("--headless")  # 启用无头模式  Включить безголовый режим
chrome_options.add_argument("--disable-gpu")  # 禁用GPU加速，某些情况下避免出现问题
chrome_options.add_argument("--window-size=1920,1080")  # 设置浏览器窗口大小

# ChromeDriver的路径
# Путь к ChromeDriver
chrome_driver_path = r'C:\Users\yty43\.cache\selenium\chromedriver\win64\122.0.6261.94\chromedriver.exe'


# 初始化WebDriver
# Инициализация WebDriver
service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Официальный сайт факультета технологии программирования
# 编程技术系官方网站
url = "https://apmath.spbu.ru/fakultet/kafedry/18-kafedra-tekhnologii-programmirovaniya"
# url = "https://apmath.spbu.ru/fakultet/kafedry/6-kafedra-teorii-upravleniya"

# 打开网页
# Открыть страницу
driver.get(url)

# Пауза на 5 секунд в ожидании загрузки JavaScript
time.sleep(5)  # 暂停5秒，等待JavaScript加载

# 获取页面源码
# Получить исходный код страницы
page_source = driver.page_source

# 解析HTML
# Парсинг HTML
tree = etree.HTML(page_source)

# 定位到所有的<p>标签，这里假设所有相关信息都在这些<p>标签内
# Найдите все теги <p>, предполагая, что вся необходимая информация находится внутри них.
p_tags = tree.xpath('/html/body/div[6]/div[2]/div/main/article//p')

# 遍历所有找到的<p>标签
# Итерация по всем найденным тегам <p>
for p in p_tags:
    # 提取姓名，假定它总是在<strong>标签内
    # Извлеките название, предполагая, что оно всегда находится внутри тега <strong>
    name = p.xpath(".//strong/text()")

    # 提取邮箱地址，假定它是<a>标签的href属性中的mailto链接
    # Извлеките адрес электронной почты, предполагая, что это ссылка mailto в атрибуте href тега <a>.
    email_links = p.xpath(".//span/a[contains(@href, 'mailto:')]/@href")

    # 使用正则表达式处理提取到的每个邮箱链接，去除"mailto:"
    # Обработайте каждую извлеченную ссылку на почтовый ящик с помощью регулярных выражений, чтобы удалить "mailto:".
    email_addresses = [re.sub(r'^mailto:', '', email) for email in email_links]

    # 如果找到了姓名和邮箱地址，则打印这些信息
    # Если имя и адрес электронной почты найдены, выведите эту информацию.
    if name and email_addresses:
        print(f"姓名(имя и фамилия): {name[0]}, 邮箱(адрес электронной почты): {', '.join(email_addresses)}")

# 关闭浏览器
driver.quit()