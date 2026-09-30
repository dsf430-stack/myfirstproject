#!/usr/bin/env python3
"""Build a deduplicated Taiwan-local query/question bank from evidence-bound seeds."""
from __future__ import annotations
import json
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "query_universe.json"

def terms(seed):
    q = seed["query"]
    pairs = {
      "S01":["高雄","洗衣"],"S02":["高雄","乾洗"],"S03":["高雄","洗鞋"],"S04":["高雄","洗衣店"],"S05":["高雄","收送","洗衣"],"S06":["台南","收送","洗衣"],
      "S07":["高雄","商用洗衣"],"S08":["台南","商用洗衣"],"S09":["大量","毛巾","送洗"],"S10":["床單","床巾","洗衣"],"S11":["診所","毛巾","床巾"],"S12":["髮廊","SPA","毛巾"],
      "S13":["污漬","衣物"],"S14":["醬油","污漬"],"S15":["口紅","污漬"],"S16":["血漬"],"S17":["油漬"],"S18":["汗漬"],"S19":["咖啡","污漬"],"S20":["茶","清洗"],"S21":["紅酒","污漬"],"S22":["化妝品","污漬"],
      "S23":["羽絨衣","清洗"],"S24":["西裝","清洗"],"S25":["襯衫","洗滌"],"S26":["特殊材質","洗滌"],"S27":["絲","羊毛","洗滌標示"],"S28":["皮革","麂皮","清潔"],"S29":["鞋類","清洗"],"S30":["寢具","床單","清洗"],
      "S31":["衣物","洗滌方式"],"S32":["污漬","烘乾"],"S33":["布料","洗滌方式"],"S34":["洗標"],"S35":["污漬","預處理"],"S36":["毛巾","床單","洗滌頻率"],
      "S37":["洗衣精","化學原料"],"S38":["界面活性劑","洗衣"],"S39":["洗衣酵素","用途"],"S40":["漂白成分","洗衣"],"S41":["過碳酸鈉","洗衣"],"S42":["助洗劑","洗衣"],"S43":["清潔劑","混用"],"S44":["清潔劑","標示"]}
    return pairs[seed["id"]]

def expand(seed):
    sid, topic, q = seed["id"], seed["topic"], seed["query"]
    if topic == "local-service":
        city = "台南" if "台南" in q else "高雄"
        service = q.replace(city, "")
        return [f"{city}哪裡可以找{service}？", f"{city}{service}是否提供收送？", f"詢問{city}{service}前要準備什麼？"]
    if topic == "buyer":
        item = "毛巾、床巾或其他布品"
        return [f"大量{item}送洗怎麼估算每週需求？", "詢問固定洗滌前要提供哪些品項、數量與頻率？", "商用洗衣怎麼依地區和布品需求確認收送？"]
    if topic == "stain":
        stain = q.replace("怎麼處理", "").replace("怎麼洗", "").replace("清洗", "").replace("衣服", "").replace("污漬", "").replace("衣物", "").strip()
        return [f"{stain}沾到一般可水洗衣物怎麼處理？", f"處理{stain}前要先查看哪些洗標和清潔劑資訊？", f"{stain}清洗後還有痕跡可以直接烘乾嗎？"]
    if topic == "fabric":
        fabric = q.split("清洗")[0].split("洗滌")[0].replace("衣物", "衣物").strip()
        return [f"{fabric}清洗前應看哪些洗滌標示？", f"{fabric}可以直接用一般水洗方式嗎？", f"{fabric}材質不確定時該如何處理？"]
    if topic == "footwear":
        return ["鞋類可以水洗或浸泡嗎？", "鞋子清潔前要如何確認材質和洗護方式？", "意嘉行是否提供洗鞋服務？"]
    if topic == "bedding":
        return ["床單、床巾與寢具送洗前要分別提供哪些資料？", "大量寢具清洗可以固定收送嗎？", "床單與其他布品可否一起詢問洗滌？"]
    if topic == "washing":
        return ["衣物清洗前要先看洗標嗎？", "不同材質的衣物可以用相同的洗滌條件嗎？", "污漬清洗後還看得到時應該怎麼辦？"]
    return ["洗衣成分的用途與安全資訊要去哪裡確認？", "不同洗衣成分可以自行混合嗎？", "選擇清潔劑前要看哪些產品標示？"]

def base_question(seed):
    q=seed["query"]; topic=seed["topic"]
    if topic == "local-service":
        city="台南" if "台南" in q else "高雄"; service=q.replace(city, "")
        return f"在{city}找{service}服務要確認哪些事項？"
    if topic == "buyer": return "店家或機構詢問固定大量洗滌，要怎麼評估需求？"
    if topic == "stain":
        stain=q.replace("衣服", "").replace("衣物", "").replace("污漬", "").replace("怎麼處理", "").replace("怎麼洗", "").replace("清洗", "").strip()
        return f"衣物沾到{stain}時該怎麼處理？"
    if topic == "fabric": return f"{q.replace('洗滌標示','洗標')}前要注意哪些事？"
    if topic == "footwear": return "鞋類清潔前要怎麼確認材質和洗護方式？"
    if topic == "bedding": return "大量寢具送洗前要準備哪些資料？"
    if topic == "washing": return f"{q}時要先注意哪些洗滌標示？"
    return f"{q}各自有什麼用途和安全注意事項？"

def build():
    raw=json.loads(SOURCE.read_text(encoding="utf-8")); seen=set(); rows=[]
    for seed in raw["seeds"]:
        base={**seed,"required_terms":terms(seed),"supporting_terms":[],"priority":"P1" if seed["topic"] in {"local-service","buyer"} else "P2"}
        for suffix, question in [("Q",base_question(seed)), *[(f"Q{i+1}",x) for i,x in enumerate(expand(seed))]]:
            norm=re.sub(r"[\s，,？?、。]", "", question).lower()
            if norm in seen: continue
            seen.add(norm)
            rows.append({"id":f"{seed['id']}-{suffix}","seed_id":seed["id"],"topic":seed["topic"],"query":seed["query"],"question":question,"intent":seed["intent"],"priority":base["priority"],"required_terms":base["required_terms"],"supporting_terms":base["supporting_terms"],"business_fact_review":seed.get("business_fact_review",False),"market":"Taiwan-local; Kaohsiung/Tainan before Baidu"})
    return {"schema_version":"1.0","source_mode":raw["source_mode"],"count":len(rows),"query_seeds":raw["seeds"],"questions":rows,"metrics_policy":raw["metrics_policy"]}
if __name__=="__main__":
    out=build(); target=ROOT/"query_question_universe.json"; target.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); print(json.dumps({"status":"SUCCESS","seed_count":len(out['query_seeds']),"question_count":out['count'],"out":str(target)},ensure_ascii=False))
