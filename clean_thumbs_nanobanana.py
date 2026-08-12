# -*- coding: utf-8 -*-
"""
나노바나나(Gemini 2.5 Flash Image)로 썸네일의 합성 텍스트·뱃지·화살표 제거.
사용법:
  1) https://aistudio.google.com/apikey 에서 API 키 발급
  2) PowerShell:  $env:GEMINI_API_KEY="발급받은키"
  3) python clean_thumbs_nanobanana.py
입력:  img/product/sh-cards/*.jpg   (download_cards.ps1 결과물)
출력:  img/product/sh-cards-clean/*.jpg
이미 처리된 파일은 건너뛰므로 중단 후 재실행해도 안전합니다.
"""
import os, sys, json, base64, glob, time, urllib.request

KEY = os.environ.get("GEMINI_API_KEY")
if not KEY:
    sys.exit("GEMINI_API_KEY 환경변수를 먼저 설정하세요:  $env:GEMINI_API_KEY=\"...\"")

SRC = os.path.join("img", "product", "sh-cards")
DST = os.path.join("img", "product", "sh-cards-clean")
os.makedirs(DST, exist_ok=True)

MODELS = ["gemini-2.5-flash-image", "gemini-2.5-flash-image-preview"]
def url_for(model):
    return f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={KEY}"

PROMPT = (
    "Remove ALL overlaid graphics from this laboratory equipment product photo: "
    "text labels, capacity badges (like 401L, 250L), colored circles and speech bubbles, "
    "arrows, 'CO2 Controller' / 'Analog' / 'Digital' style tags, CE marks floating in "
    "the background, power-cord icons, colored banner strips at top or bottom, and any "
    "Korean or English annotation text. "
    "Keep the product itself EXACTLY as it is - same shape, colors, position, lighting, "
    "including any text printed on the product's own control panel or body labels. "
    "Fill removed areas with clean pure white background. "
    "Output must look like a clean product pack-shot on a plain white background."
)

def call(model, b64):
    body = json.dumps({
        "contents": [{"parts": [
            {"text": PROMPT},
            {"inline_data": {"mime_type": "image/jpeg", "data": b64}},
        ]}],
        "generationConfig": {"responseModalities": ["IMAGE"]},
    }).encode()
    req = urllib.request.Request(url_for(model), data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())

def clean(path, out):
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    last_err = None
    for model in MODELS:
        for attempt in range(3):
            try:
                res = call(model, b64)
                for part in res["candidates"][0]["content"]["parts"]:
                    if "inlineData" in part:
                        with open(out, "wb") as f:
                            f.write(base64.b64decode(part["inlineData"]["data"]))
                        return True
                return False
            except urllib.error.HTTPError as e:
                detail = ""
                try:
                    detail = e.read().decode()[:600]
                except Exception:
                    pass
                last_err = f"{model} HTTP {e.code}: {detail}"
                if e.code == 429:
                    wait = 25 * (attempt + 1)
                    print(f"    429 쿼터 대기 {wait}s... ({model}, {attempt+1}/3)")
                    time.sleep(wait)
                    continue
                break  # 429 외 오류면 다음 모델로
    raise RuntimeError(last_err or "unknown")

files = sorted(glob.glob(os.path.join(SRC, "*.jpg")))
if len(sys.argv) > 1:  # 특정 파일만: python clean_thumbs_nanobanana.py 파일명.jpg
    files = [f for f in files if os.path.basename(f) in sys.argv[1:]]
if not files:
    sys.exit(f"{SRC} 에 이미지가 없습니다. download_cards.ps1 을 먼저 실행하세요.")

ok = fail = skip = 0
for i, p in enumerate(files, 1):
    name = os.path.basename(p)
    out = os.path.join(DST, name)
    if os.path.exists(out):
        skip += 1
        continue
    try:
        if clean(p, out):
            ok += 1
            print(f"[{i}/{len(files)}] OK   {name}")
        else:
            fail += 1
            print(f"[{i}/{len(files)}] NOIMG {name}")
    except Exception as e:
        fail += 1
        print(f"[{i}/{len(files)}] FAIL {name}\n    -> {str(e)[:500]}")
    time.sleep(1.2)  # 무료 티어 분당 요청 제한 대응

print(f"\n완료: {ok}  실패: {fail}  건너뜀: {skip}")
print("결과 확인 후 클로드에게 '나노바나나 처리 끝'이라고 알려주세요.")
