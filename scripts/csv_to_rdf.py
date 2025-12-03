import pandas as pd
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, FOAF, DCTERMS
import os
import sys

# === 1. 路径设置 ===
script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)
project_root = os.path.dirname(script_dir)
csv_path = os.path.join(project_root, "data", "csv", "taylor_swift_metadata.csv")
output_dir = os.path.join(project_root, "output")
output_ttl_path = os.path.join(output_dir, "taylor_swift_graph.ttl")

# === 2. 定义本体 ===
CRM = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
FRBROO = Namespace("http://iflastandards.info/ns/fr/frbr/frbroo/")
MYNS = Namespace("https://example.org/taylor-project/")

g = Graph()
g.bind("crm", CRM)
g.bind("frbroo", FRBROO)
g.bind("foaf", FOAF)
g.bind("dcterms", DCTERMS)

# 中心节点
taylor_uri = URIRef("http://viaf.org/viaf/88582739")
g.add((taylor_uri, RDF.type, FOAF.Person))
g.add((taylor_uri, FOAF.name, Literal("Taylor Swift")))

# === 3. 读取与转换 ===
try:
    df = pd.read_csv(csv_path)
    # 关键步骤：去除表头和内容的空格，防止 " type" 这种错误
    df.columns = [c.strip() for c in df.columns]
    
    for index, row in df.iterrows():
        # 清洗数据
        item_id = str(row['id']).strip()
        title = str(row['title']).strip()
        item_type = str(row['type']).strip() # 这里现在是标准的 crm:xxx 了
        creator_uri_str = str(row['creator_uri']).strip()
        
        item_uri = MYNS[item_id]
        
        # 基础元数据
        g.add((item_uri, DCTERMS.title, Literal(title)))
        g.add((item_uri, DCTERMS.date, Literal(str(row['date']))))
        g.add((item_uri, DCTERMS.description, Literal(str(row['description']))))
        
        # 创作者链接 (如果有链接用链接，没有用文字)
        if "http" in creator_uri_str:
            g.add((item_uri, DCTERMS.creator, URIRef(creator_uri_str)))
        else:
            g.add((item_uri, DCTERMS.creator, Literal(row['creator'])))

        # --- 逻辑映射 (根据清洗后的 Type) ---
        
        # 1. 地点
        if "E53_Place" in item_type:
            g.add((item_uri, RDF.type, CRM.E53_Place))
            g.add((taylor_uri, CRM.P14_performed_at, item_uri))

        # 2. 物品 (手稿、吉他、衣服)
        elif "E22_Man-Made_Object" in item_type:
            g.add((item_uri, RDF.type, CRM.E22_Man_Made_Object))
            if "Lyrics" in title:
                 # 手稿是被创作的
                 g.add((item_uri, FRBROO.R17i_was_created_by, taylor_uri))
            else:
                 # 吉他和衣服是被拥有的
                 g.add((item_uri, CRM.P51_has_former_or_current_owner, taylor_uri))

        # 3. 作品 (专辑、电影、杂志)
        elif "F1_Work" in item_type:
            g.add((item_uri, RDF.type, FRBROO.F1_Work))
            if "Miss Americana" in title:
                g.add((item_uri, CRM.P129_is_about, taylor_uri))
            elif "Time" in title:
                g.add((item_uri, FOAF.depicts, taylor_uri))
            else:
                g.add((item_uri, DCTERMS.creator, taylor_uri))

        # 4. 事件 (Eras Tour)
        elif "E5_Event" in item_type:
            g.add((item_uri, RDF.type, CRM.E5_Event))
            g.add((item_uri, CRM.P11_had_participant, taylor_uri))

        # 5. 奖项 (Grammy)
        elif "E13_Attribute_Assignment" in item_type:
            g.add((item_uri, RDF.type, CRM.E13_Attribute_Assignment))
            g.add((item_uri, CRM.P140_assigned_attribute_to, taylor_uri))
            
        # 6. 人物 (Scott)
        elif "Person" in item_type:
            g.add((item_uri, RDF.type, FOAF.Person))
            g.add((taylor_uri, FOAF.knows, item_uri))

    # 保存
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    g.serialize(destination=output_ttl_path, format="turtle")
    print(f"\n✅ 成功！RDF 文件已生成: {output_ttl_path}")

except Exception as e:
    print(f"❌ 出错: {e}")