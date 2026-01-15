import pandas as pd
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, FOAF, DCTERMS, RDFS, OWL, XSD
import os
import sys

# === 1. 路径设置 (根据你的描述调整) ===
# 假设脚本在 script/ 文件夹，数据在 data/csv/ 文件夹
script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)       # .../project/script
project_root = os.path.dirname(script_dir)      # .../project
csv_path = os.path.join(project_root, "data", "csv", "taylor_swift_metadata.csv")
output_dir = os.path.join(project_root, "output")
output_ttl_path = os.path.join(output_dir, "taylor_swift_graph.ttl")

# === 2. 定义命名空间 ===
CRM = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
FRBROO = Namespace("http://iflastandards.info/ns/fr/frbr/frbroo/")
MYNS = Namespace("https://example.org/taylor-project/")

g = Graph()
g.bind("crm", CRM)
g.bind("frbroo", FRBROO)
g.bind("foaf", FOAF)
g.bind("dcterms", DCTERMS)
g.bind("owl", OWL)
g.bind("rdfs", RDFS)

# === 3. 核心升级：定义实体映射字典 (LOD 的关键) ===
# 我们在这里集中管理那些重要人物/机构的外部链接
# 脚本遇到这些名字时，会自动使用这里的丰富信息，而不是简单的 CSV 里的字符串
entity_data = {
    "Swift, Taylor": {
        "uri": MYNS["agent/taylor_swift"],
        "type": CRM.E39_Actor,
        "links": [
            "http://viaf.org/viaf/88582739",
            "http://www.wikidata.org/entity/Q26876",
            "http://dbpedia.org/resource/Taylor_Swift"
        ]
    },
    "Scott Borchetta": {
        "uri": MYNS["agent/scott_borchetta"],
        "type": CRM.E39_Actor,
        "links": [
            "http://viaf.org/viaf/305203362",
            "http://www.wikidata.org/entity/Q1968872"
        ]
    },
    "Gibson Brands, Inc.": {
        "uri": MYNS["agent/gibson_brands"],
        "type": CRM.E39_Actor,
        "links": [
            "http://viaf.org/viaf/135013788",
            "http://www.wikidata.org/entity/Q247109"
        ]
    },
    "Kurland, Amy": {
        "uri": MYNS["agent/amy_kurland"],
        "type": CRM.E39_Actor,
        "links": ["http://viaf.org/viaf/305203362"] # 假设链接
    },
    "Taylor Swift Merchandising": {
        "uri": MYNS["agent/taylor_swift_merch"],
        "type": CRM.E39_Actor,
        "links": []
    },
    "The Recording Academy": {
        "uri": MYNS["agent/recording_academy"],
        "type": CRM.E39_Actor,
        "links": ["http://viaf.org/viaf/144184305"]
    }
}

# === 4. 预处理：先在图谱里生成这些“大人物”的节点 ===
# 这样不仅 item 指向他们，他们自己也是图谱里独立存在的实体
print("正在构建实体节点与外部链接...")
local_entity_map = {} 

for name, data in entity_data.items():
    local_node = data["uri"]
    local_entity_map[name] = local_node # 存入缓存方便查找
    
    # 定义基本信息
    g.add((local_node, RDF.type, data["type"]))
    g.add((local_node, RDFS.label, Literal(name)))
    
    # 添加所有外部链接 (owl:sameAs) - 这是 5 星级 LOD 的关键
    for link in data["links"]:
        g.add((local_node, OWL.sameAs, URIRef(link)))

# === 5. 读取与转换 CSV ===
try:
    # 确保 CSV 存在
    if not os.path.exists(csv_path):
        print(f"❌ 错误：找不到 CSV 文件：{csv_path}")
        sys.exit(1)

    df = pd.read_csv(csv_path)
    # 清洗列名，去除可能存在的空格
    df.columns = [c.strip() for c in df.columns]
    
    print(f"开始处理 {len(df)} 条数据...")

    for index, row in df.iterrows():
        # --- 基础数据清洗 ---
        item_id = str(row['id']).strip()
        title = str(row['title']).strip()
        creator_name = str(row['creator']).strip()
        date_str = str(row['date']).strip()
        item_type_raw = str(row['type']).strip() # 例如 "crm:E22_Man-Made_Object"
        description = str(row['description']).strip()
        
        # 生成物品的 URI
        item_uri = MYNS[item_id] 
        
        # --- 添加基础属性 ---
        g.add((item_uri, DCTERMS.title, Literal(title)))
        g.add((item_uri, DCTERMS.date, Literal(date_str)))
        g.add((item_uri, DCTERMS.description, Literal(description)))
        
        # --- 处理 Creator (创作者) ---
        # 逻辑：如果字典里有这个名字，就用本地节点；否则用 CSV 里的 URI；如果还没，就存文字
        if creator_name in local_entity_map:
            creator_node = local_entity_map[creator_name]
            g.add((item_uri, DCTERMS.creator, creator_node))
        elif "http" in str(row['creator_uri']):
            g.add((item_uri, DCTERMS.creator, URIRef(str(row['creator_uri']).strip())))
        else:
            g.add((item_uri, DCTERMS.creator, Literal(creator_name)))

        # --- 处理 Type (类型) 并添加特定属性 ---
        # 我们根据 CSV 里的 'type' 列来决定 rdf:type 和其他关系
        
        # 1. 物品 (Man-Made Object)
        if "E22" in item_type_raw:
            g.add((item_uri, RDF.type, CRM.E22_Man_Made_Object))
            # 只有当作者是 Swift 时，我们假设她是 Owner (根据你的业务逻辑)
            # 或者你可以根据 description 内容判断
            if "Swift" in creator_name:
                 g.add((item_uri, CRM.P51_has_former_or_current_owner, local_entity_map.get("Swift, Taylor", Literal("Taylor Swift"))))
            
            # 手稿特殊处理
            if "Lyrics" in title:
                 g.add((item_uri, FRBROO.R17i_was_created_by, local_entity_map.get("Swift, Taylor", Literal("Taylor Swift"))))

        # 2. 地点 (Place) - 比如 item_002 Bluebird Cafe
        elif "E53" in item_type_raw:
            g.add((item_uri, RDF.type, CRM.E53_Place))
            # 可以在这里添加地点特有的属性，比如 P89_falls_within (Nashville)
            if "Nashville" in str(row['coverage_place']):
                g.add((item_uri, CRM.P89_falls_within, Literal("Nashville")))

        # 3. 作品 (Work) - 比如 item_004 Fearless
        elif "F1" in item_type_raw:
            g.add((item_uri, RDF.type, FRBROO.F1_Work))
            if "Miss Americana" in title:
                g.add((item_uri, CRM.P129_is_about, local_entity_map.get("Swift, Taylor", Literal("Taylor Swift"))))
            elif "Time" in title:
                g.add((item_uri, FOAF.depicts, local_entity_map.get("Swift, Taylor", Literal("Taylor Swift"))))

        # 4. 事件 (Event) - 比如 item_008 Eras Tour
        elif "E5" in item_type_raw:
            g.add((item_uri, RDF.type, CRM.E5_Event))
            g.add((item_uri, CRM.P11_had_participant, local_entity_map.get("Swift, Taylor", Literal("Taylor Swift"))))

        # 5. 奖项 (Attribute Assignment) - 比如 item_009 Grammy
        elif "E13" in item_type_raw:
            g.add((item_uri, RDF.type, CRM.E13_Attribute_Assignment))
            g.add((item_uri, CRM.P140_assigned_attribute_to, local_entity_map.get("Swift, Taylor", Literal("Taylor Swift"))))
            
        # 6. 人物 (Person) - 比如 item_005 Scott Borchetta
        # 注意：这里处理的是 CSV 里作为 item 出现的人
        elif "foaf:Person" in item_type_raw:
            g.add((item_uri, RDF.type, FOAF.Person))
            # 如果这个人是 Scott，添加他和 Taylor 的关系
            if "Scott" in title:
                # 建立 item_005 和 agent/scott_borchetta 的等同关系 (可选，防止重复)
                if "Scott Borchetta" in local_entity_map:
                    g.add((item_uri, OWL.sameAs, local_entity_map["Scott Borchetta"]))
                
                # Scott 认识 Taylor
                taylor_node = local_entity_map.get("Swift, Taylor")
                if taylor_node:
                    g.add((item_uri, FOAF.knows, taylor_node))

    # === 6. 保存文件 ===
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    g.serialize(destination=output_ttl_path, format="turtle")
    print(f"\n✅ 成功！RDF 文件已生成: {output_ttl_path}")
    print(f"包含三元组数量: {len(g)}")

except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"❌ 出错: {e}")
