# ITRAP 鍥介檯鏉＄害缁撴瀯鍖栨暟鎹泦

鏈粨搴撴敹褰曚竴鎵瑰浗闄呮潯绾︺€佸崗瀹氥€佽瀹氫功銆佽仈鍚堝０鏄庣瓑娉曞緥鏂囦欢鐨勭粨鏋勫寲 JSON 鏁版嵁銆傛暟鎹富瑕侀潰鍚戝浗闄呮硶妫€绱€佹潯绾︽潯娆捐В鏋愩€佹硶寰嬬煡璇嗗簱鏋勫缓銆丷AG 妫€绱㈠寮恒€佹硶寰嬫枃鏈彲瑙嗗寲鍜岃嚜鐒惰瑷€澶勭悊瀹為獙銆?
褰撳墠鏁版嵁鏂囦欢浣嶄簬 `json/`锛屾瘡涓?JSON 鏂囦欢瀵瑰簲涓€浠芥硶寰嬫枃浠躲€傛枃浠堕噰鐢ㄧ粺涓€鐨勬枃妗ｆ爲缁撴瀯锛屽寘鍚?`meta` 鍏冩暟鎹拰 `children` 姝ｆ枃缁撴瀯鑺傜偣銆?
## 鏁版嵁姒傝

- 鏁版嵁瑙勬ā锛?4 浠?JSON 鏂囦欢
- 涓昏璇锛氫腑鏂囷紝鍚釜鍒嫳鏂囨枃鏈?- 鏂囦欢绫诲瀷锛氭潯绾︺€佸崗瀹氥€佽瀹氫功銆佽皡瑙ｅ蹇樺綍銆佽仈鍚堝０鏄庛€佸叕鎶ャ€侀檮浠剁瓑
- 缁撴瀯褰㈠紡锛歚document -> preamble/article/annex -> text`
- 鍏冩暟鎹储寮曪細瑙?`metadata/catalog.csv`
- 缁撴瀯璇存槑锛氳 `metadata/schema.md`

## 鐩綍缁撴瀯

```text
data/
  json/                # 宸叉暣鐞嗙殑鏉＄害 JSON 鏁版嵁
metadata/
  catalog.csv          # 鏁版嵁鐩綍绱㈠紩
  schema.md            # JSON 缁撴瀯鍜屽瓧娈佃鏄?plugins/
  treaty-ast-integrity-checker/
                      # 鏉＄害 AST 瀹屾暣鎬ф鏌ュ伐鍏?```

## 蹇€熶娇鐢?
鍙互鐩存帴璇诲彇鍗曚釜 JSON 鏂囦欢锛?
```python
import json
from pathlib import Path

path = Path("json/宸撮粠鍗忓畾.json")
data = json.loads(path.read_text(encoding="utf-8"))

print(data["meta"]["title"])
print(data["children"][0]["type"])
```

涔熷彲浠ュ厛璇诲彇 `metadata/catalog.csv` 杩涜绛涢€夛紝鍐嶆墦寮€瀵瑰簲鐨?JSON 鏂囦欢銆?
## 瀛楁璇存槑

姣忎唤 JSON 椤跺眰閫氬父鍖呭惈锛?
- `meta`锛氭枃浠舵爣棰樸€佺被鍨嬨€佺紨绾︽柟銆佸叧閿瘝銆佺缃叉棩鏈熴€佺敓鏁堟棩鏈熴€佹潵婧?URL 绛夊厓鏁版嵁
- `type`锛氶《灞傝妭鐐圭被鍨嬶紝閫氬父涓?`document`
- `title`锛氭枃妗ｆ爣棰?- `children`锛氭枃妗ｆ鏂囩粨鏋勶紝閫氬父鍖呮嫭搴忚█銆佹潯銆侀檮浠剁瓑鑺傜偣

璇︾粏瀛楁鍚箟璇峰弬瑙?`metadata/schema.md`銆?
## 鏁版嵁鏉ユ簮涓庡噯纭€?
鏁版嵁涓殑 `source`銆乣source_url`銆乣source_file_url` 瀛楁璁板綍浜嗘暣鐞嗘椂浣跨敤鐨勬潵婧愪俊鎭€傞儴鍒嗘枃鏈潵婧愬寘鎷腑鍗庝汉姘戝叡鍜屽浗鏉＄害鏁版嵁搴撱€佷腑鍥借嚜鐢辫锤鏄撳尯鏈嶅姟缃戙€佷腑鍗庝汉姘戝叡鍜屽浗澶栦氦閮ㄧ瓑鍏紑椤甸潰銆?
鏈暟鎹泦鏄粨鏋勫寲鏁寸悊缁撴灉锛屼笉鏋勬垚娉曞緥鎰忚銆傜敤浜庢硶寰嬬爺绌躲€佹寮忓紩鐢ㄦ垨鍚堣鍒ゆ柇鏃讹紝璇蜂互瀹樻柟鍏竷鏂囨湰鍜岀幇琛屾湁鏁堟硶寰嬫枃浠朵负鍑嗐€?
## 鏍￠獙

浠撳簱涓寘鍚竴涓熀纭€瀹屾暣鎬ф鏌ュ伐鍏凤細

```powershell
python plugins/treaty-ast-integrity-checker/scripts/check_treaty_ast.py "json/宸撮粠鍗忓畾.json"
```

璇ュ伐鍏蜂富瑕佹鏌?JSON 璇硶銆佸繀闇€瀛楁銆佽妭鐐圭粨鏋勭瓑宸ョ▼瀹屾暣鎬ч棶棰橈紝涓嶉獙璇佹硶寰嬪唴瀹规湰韬殑鍑嗙‘鎬с€?
## 寮曠敤寤鸿

濡傞渶寮曠敤鏈暟鎹泦锛屽缓璁敞鏄庯細

```text
ITRAP 鍥介檯鏉＄害缁撴瀯鍖栨暟鎹泦锛孞SON 缁撴瀯鍖栨暣鐞嗙増鏈紝璁块棶鏃ユ湡锛歒YYY-MM-DD銆?```

寮曠敤鍏蜂綋鏉＄害鏂囨湰鏃讹紝璇峰悓鏃跺紩鐢ㄥ搴?JSON 涓殑瀹樻柟鏉ユ簮閾炬帴銆?
