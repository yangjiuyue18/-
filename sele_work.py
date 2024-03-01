from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from lxml import etree
import time
import re

# 配置Chrome选项，设置为无头模式
chrome_options = Options()
chrome_options.add_argument("--headless")  # 启用无头模式
chrome_options.add_argument("--disable-gpu")  # 禁用GPU加速，某些情况下避免出现问题
chrome_options.add_argument("--window-size=1920,1080")  # 设置浏览器窗口大小

# 替换为你的ChromeDriver的路径
chrome_driver_path = r'C:\Users\yty43\.cache\selenium\chromedriver\win64\122.0.6261.94\chromedriver.exe'


# 初始化WebDriver
service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

url = "https://apmath.spbu.ru/fakultet/kafedry/18-kafedra-tekhnologii-programmirovaniya"

# 打开网页
driver.get(url)

# 等待页面加载完成（根据实际情况调整等待时间）
time.sleep(5)  # 暂停5秒，等待JavaScript加载

# 获取页面源码
page_source = driver.page_source

# 解析HTML
tree = etree.HTML(page_source)

# 定位到所有的<p>标签，这里假设所有相关信息都在这些<p>标签内
# 如果有更具体的路径，应该使用更具体的XPath
p_tags = tree.xpath('/html/body/div[6]/div[2]/div/main/article//p')

# 遍历所有找到的<p>标签
for p in p_tags:
    # 提取姓名，假定它总是在<strong>标签内
    name = p.xpath(".//strong/text()")

    # 提取邮箱地址，假定它是<a>标签的href属性中的mailto链接
    email_addresses = p.xpath(".//span/a[contains(@href, 'mailto:')]/@href")

    # 如果找到了姓名和邮箱地址，则打印这些信息
    if name and email_addresses:
        print(f"姓名: {name[0]}, 邮箱: {', '.join(email_addresses)}")

# 关闭浏览器
driver.quit()