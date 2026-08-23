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
import os, sys, io, json, base64, glob, time, urllib.request

KEY = os.environ.get("GEMINI_API_KEY")
if not KEY:
    sys.exit("GEMINI_API_KEY 환경변수를 먼저 설정하세요:  $env:GEMINI_API_KEY=\"...\"")

SRC = os.path.join("img", "product", "sh-cards")
DST = os.path.join("img", "product", "sh-cards-clean")
os.makedirs(DST, exist_ok=True)

MODELS = ["gemini-3.1-flash-lite-image", "gemini-2.5-flash-image"]
if os.environ.get("GEMINI_IMAGE_MODEL"):          # 특정 모델 강제
    MODELS = [os.environ["GEMINI_IMAGE_MODEL"]]

def _live_models():
    """계정에서 실제로 쓸 수 있는 이미지 모델만 남긴다(없는 모델에 호출해 404 낭비 방지)."""
    try:
        u = f"https://generativelanguage.googleapis.com/v1beta/models?key={KEY}&pageSize=200"
        with urllib.request.urlopen(u, timeout=30) as r:
            names = {m["name"].split("/")[-1] for m in json.loads(r.read()).get("models", [])}
        live = [m for m in MODELS if m in names]
        if live:
            if live != MODELS:
                print("사용 가능 모델:", ", ".join(live),
                      " (제외:", ", ".join(m for m in MODELS if m not in live) + ")")
            return live
        print("경고: 지정한 이미지 모델이 계정에 없습니다. 목록에서 자동 탐색합니다.")
        auto = sorted(n for n in names if "image" in n and "gemini" in n)
        if auto:
            print("  →", ", ".join(auto[:5]))
            return auto[:2]
    except Exception as e:
        print("모델 목록 조회 실패(무시하고 진행):", str(e)[:200])
    return MODELS

MODELS = _live_models()

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
                if e.code == 429 or last_err is None:
                    last_err = f"{model} HTTP {e.code}: {detail}"
                if e.code == 429:
                    wait = 25 * (attempt + 1)
                    print(f"    429 쿼터 대기 {wait}s... ({model}, {attempt+1}/3)")
                    time.sleep(wait)
                    continue
                break  # 429 외 오류면 다음 모델로
    raise RuntimeError(last_err or "unknown")

files = sorted(glob.glob(os.path.join(SRC, "*.jpg")))

# ── 인자 파싱 ──────────────────────────────────────────────
#   python clean_thumbs_nanobanana.py              → 남은 것 중 5장
#   python clean_thumbs_nanobanana.py --limit 10   → 10장
#   python clean_thumbs_nanobanana.py --all        → 전부
#   python clean_thumbs_nanobanana.py a.jpg b.jpg  → 지정 파일만
LIMIT = 5
argv = sys.argv[1:]
picks = []
i = 0
while i < len(argv):
    a = argv[i]
    if a == "--all":
        LIMIT = 0
    elif a == "--limit":
        i += 1
        LIMIT = int(argv[i])
    elif a.startswith("--limit="):
        LIMIT = int(a.split("=", 1)[1])
    else:
        picks.append(a)
    i += 1

if picks:
    files = [f for f in files if os.path.basename(f) in picks]
    LIMIT = 0
if not files:
    sys.exit(f"{SRC} 에 이미지가 없습니다. _ops\\download_sh_cards_v2.ps1 을 먼저 실행하세요.")

todo = [f for f in files if not os.path.exists(os.path.join(DST, os.path.basename(f)))]
done_all = len(files) - len(todo)
if not todo:
    sys.exit(f"남은 이미지가 없습니다. (원본 {len(files)}장 전부 처리 완료)")
batch = todo if LIMIT <= 0 else todo[:LIMIT]

LOG = os.path.join("_ops", "clean_fail.log")
os.makedirs("_ops", exist_ok=True)

def logfail(name, msg):
    with io.open(LOG, "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')}\t{name}\t{msg}\n")

print(f"원본 {len(files)}장 · 처리완료 {done_all}장 · 남음 {len(todo)}장 → 이번 실행 {len(batch)}장\n")

ok = fail = 0
for i, p in enumerate(batch, 1):
    name = os.path.basename(p)
    out = os.path.join(DST, name)
    try:
        if clean(p, out):
            ok += 1
            print(f"[{i}/{len(batch)}] OK    {name}")
        else:
            fail += 1
            print(f"[{i}/{len(batch)}] NOIMG {name}  (모델이 이미지 대신 텍스트를 반환)")
            logfail(name, "NOIMG: 응답에 inlineData 없음")
    except Exception as e:
        fail += 1
        msg = str(e).replace("\n", " ")[:800]
        print(f"[{i}/{len(batch)}] FAIL  {name}\n    -> {msg[:300]}")
        logfail(name, msg)
    time.sleep(1.2)  # 무료 티어 분당 요청 제한 대응

left = len(todo) - ok
print(f"\n이번 실행: 성공 {ok}  실패 {fail}   |   전체 남은 장수 {left}")
if fail:
    print(f"실패 상세 로그: {LOG}  (마지막 3줄)")
    try:
        for ln in io.open(LOG, encoding="utf-8").read().splitlines()[-3:]:
            print("   " + ln[:240])
    except Exception:
        pass
if left:
    print("계속하려면 같은 명령을 다시 실행하세요 (이미 만든 파일은 자동으로 건너뜁니다).")
else:
    print("전부 완료. 클로드에게 '나노바나나 처리 끝'이라고 알려주세요.")
