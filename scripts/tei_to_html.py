import lxml.etree as ET
import os
import sys

# === 1. 侦探模式：确定路径 ===
script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)
project_root = os.path.dirname(script_dir)

# 构建路径
xml_file_path = os.path.join(project_root, "data", "tei", "wildest_dreams.xml")
xslt_file_path = os.path.join(script_dir, "transform.xsl")
output_dir = os.path.join(project_root, "docs")
output_html_path = os.path.join(output_dir, "wildest_dreams.html")

# === 2. 检查文件 ===
if not os.path.exists(xml_file_path):
    print(f"❌ 错误：找不到 XML 文件！\n请检查路径: {xml_file_path}")
    sys.exit(1)

if not os.path.exists(xslt_file_path):
    print(f"❌ 错误：找不到 XSLT 文件！\n请检查路径: {xslt_file_path}")
    sys.exit(1)

# === 3. 开始转换 ===
try:
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    dom = ET.parse(xml_file_path)
    xslt = ET.parse(xslt_file_path)
    transform = ET.XSLT(xslt)
    new_dom = transform(dom)
    
    with open(output_html_path, "wb") as f:
        f.write(ET.tostring(new_dom, pretty_print=True))
        
    print("\n✅ 成功！Success! 网页已生成。")
except Exception as e:
    print(f"❌ 运行出错: {e}")