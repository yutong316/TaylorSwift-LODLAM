import lxml.etree as ET
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, DCTERMS
import os
import sys

# === 1. 路径设置 ===
script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)
project_root = os.path.dirname(script_dir)

xml_file_path = os.path.join(project_root, "data", "tei", "wildest_dreams.xml")
output_rdf_path = os.path.join(project_root, "output", "tei_extract.ttl")

print(f"正在读取 XML: {xml_file_path}")

if not os.path.exists(xml_file_path):
    print("❌ 找不到 XML 文件！请检查 data/tei/ 文件夹。")
    sys.exit(1)

# === 2. 定义本体 ===
MYNS = Namespace("https://example.org/taylor-project/")
# 我们用 DCTERMS.references 来表示“手稿里提到了...”
# 也可以用 crm:P67_refers_to

g = Graph()
g.bind("dcterms", DCTERMS)
g.bind("my", MYNS)

# === 3. 解析 XML 并提取 ===
try:
    # 我们的手稿在 CSV 里叫 item_001，所以这里也要用同一个 ID，这样数据才能连起来
    item_uri = MYNS["item_001"]
    
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    
    # 定义 XML 命名空间 (TEI 必须要有这个)
    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}

    print("正在提取实体链接...")
    
    # 查找所有带有 ref 属性的标签 (不管它是 placeName 还是 objectName)
    # xpath 语法：//* 找所有标签，[@ref] 只要有 ref 属性的
    tags_with_ref = root.xpath("//*[@ref]", namespaces=ns)
    
    count = 0
    for tag in tags_with_ref:
        # 获取链接
        ref_link = tag.get("ref")
        # 获取标签里的文字
        text_content = tag.text
        
        if ref_link:
            # 生成 RDF: item_001 --(references)--> Wikidata链接
            g.add((item_uri, DCTERMS.references, URIRef(ref_link)))
            print(f"  -> 发现关联: '{text_content}' 指向 {ref_link}")
            count += 1

    # === 4. 保存结果 ===
    if not os.path.exists(os.path.dirname(output_rdf_path)):
        os.makedirs(os.path.dirname(output_rdf_path))
        
    g.serialize(destination=output_rdf_path, format="turtle")
    
    print("-" * 30)
    print(f"✅ 成功提取了 {count} 个实体链接！")
    print(f"微观 RDF 文件已保存: {output_rdf_path}")
    print("-" * 30)

except Exception as e:
    print(f"❌ 出错: {e}")