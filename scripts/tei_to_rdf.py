import lxml.etree as ET
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, DCTERMS, FOAF
import os
import sys

# === 1. 路径设置 ===
script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)
project_root = os.path.dirname(script_dir)

xml_file_path = os.path.join(project_root, "data", "tei", "wildest_dreams.xml")
output_rdf_path = os.path.join(project_root, "output", "tei_extract_deep.ttl")

# === 2. 定义本体 ===
# 使用 CIDOC CRM 来描述物理特征和指涉关系
CRM = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
# 使用自定义命名空间来创建本地节点（比如具体的某处涂改）
MYNS = Namespace("https://example.org/taylor-project/")

g = Graph()
g.bind("crm", CRM)
g.bind("dcterms", DCTERMS)
g.bind("my", MYNS)
g.bind("rdfs", RDFS)

# === 3. 解析与提取逻辑 ===

def process_tei(xml_path):
    if not os.path.exists(xml_path):
        print(f"❌ 错误: 找不到文件 {xml_path}")
        return

    tree = ET.parse(xml_path)
    root = tree.getroot()
    # TEI 的命名空间，解析时必须带上
    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
    
    # 核心主体：这份手稿 (item_001)
    # 必须和宏观层面的 ID 保持一致，这样两个 RDF 文件才能连起来！
    item_uri = MYNS["item_001"]
    
    print(f"正在深度解析手稿: {item_uri}")

    # --- A. 提取 Header 信息 (物理属性) ---
    # 提取材质 "Ink on lined paper"
    medium = root.xpath("//tei:sourceDesc/tei:bibl/tei:medium/text()", namespaces=ns)
    if medium:
        # P45 consists of (material) -> 这是一个简单的处理，把材质作为 Literal 或者创建一个材质节点
        # 为了展示深度，我们把材质作为描述加进去
        g.add((item_uri, CRM.P3_has_note, Literal(f"Material: {medium[0]}")))
        g.add((item_uri, DCTERMS.medium, Literal(medium[0])))

    # --- B. 提取实体并分类 (Entity Extraction & Typing) ---
    # 1. 提取地点 (placeName)
    for place in root.xpath("//tei:placeName", namespaces=ns):
        uri = place.get("ref")
        text = place.text
        if uri:
            ref_node = URIRef(uri)
            # 建立联系：手稿 -> 提及了 -> 某个URI
            g.add((item_uri, CRM.P67_refers_to, ref_node))
            # 深度体现：定义这个 URI 是什么类型 (E53 Place)
            g.add((ref_node, RDF.type, CRM.E53_Place))
            g.add((ref_node, RDFS.label, Literal(text)))
            print(f"  [地点] {text} -> {uri}")

    # 2. 提取物体 (objectName)
    for obj in root.xpath("//tei:objectName", namespaces=ns):
        uri = obj.get("ref")
        text = obj.text
        if uri:
            ref_node = URIRef(uri)
            g.add((item_uri, CRM.P67_refers_to, ref_node))
            # 深度体现：定义这个 URI 是人造物体类型 (E22)
            g.add((ref_node, RDF.type, CRM.E22_Man_Made_Object))
            g.add((ref_node, RDFS.label, Literal(text)))
            print(f"  [物体] {text} -> {uri}")
            
    # 3. 提取时间术语 (term type="time")
    for term in root.xpath("//tei:term[@type='time']", namespaces=ns):
        uri = term.get("ref")
        text = term.text
        if uri:
            ref_node = URIRef(uri)
            g.add((item_uri, CRM.P67_refers_to, ref_node))
            g.add((ref_node, RDF.type, CRM.E52_Time_Span)) # 定义为时间跨度
            print(f"  [时间] {text} -> {uri}")

    # --- C. 提取创作痕迹 (Genetic Criticism / Modifications) ---
    # 这是 TEI 最独特的地方：删除 (<del>) 和 添加 (<add>)
    
    # 1. 处理删除 (Deletions)
    deletions = root.xpath("//tei:del", namespaces=ns)
    for i, deletion in enumerate(deletions):
        text = deletion.text
        if text:
            # 创建一个本地节点来代表这次“删除行为”或“删除痕迹”
            # 命名规则：modification_del_1, modification_del_2...
            mod_node = MYNS[f"feature_del_{i+1}"]
            
            # 建立联系：手稿 -> 承载了 -> 这个特征
            g.add((item_uri, CRM.P56_bears_feature, mod_node))
            
            # 定义特征类型：E25 Man-Made Feature (人造特征/痕迹)
            g.add((mod_node, RDF.type, CRM.E25_Man_Made_Feature))
            
            # 描述这个特征
            g.add((mod_node, RDFS.label, Literal(f"Deletion of '{text}'")))
            g.add((mod_node, RDFS.comment, Literal("Author crossed out this text during composition.")))
            print(f"  [痕迹] 删除: '{text}'")

    # 2. 处理添加 (Additions)
    additions = root.xpath("//tei:add", namespaces=ns)
    for i, addition in enumerate(additions):
        text = addition.text
        place = addition.get("place", "unknown") # 获取添加的位置 (如 above)
        if text:
            mod_node = MYNS[f"feature_add_{i+1}"]
            
            g.add((item_uri, CRM.P56_bears_feature, mod_node))
            g.add((mod_node, RDF.type, CRM.E25_Man_Made_Feature))
            
            g.add((mod_node, RDFS.label, Literal(f"Addition of '{text}'")))
            g.add((mod_node, RDFS.comment, Literal(f"Author inserted this text. Placement: {place}")))
            print(f"  [痕迹] 添加: '{text}' (位置: {place})")

    # === 4. 保存 ===
    if not os.path.exists(os.path.dirname(output_rdf_path)):
        os.makedirs(os.path.dirname(output_rdf_path))

    g.serialize(destination=output_rdf_path, format="turtle")
    print("\n✅ 深度 RDF 文件生成完毕！")
    print(f"文件位置: {output_rdf_path}")
    print(f"包含三元组数量: {len(g)}")

# 运行
if __name__ == "__main__":
    process_tei(xml_file_path)
