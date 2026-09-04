# Alicat 파트넘버 문법 (공식)

출처: https://www.alicat.com/documentation/part-number-decoder/ · 수집 2026-09-04

파트넘버 = `최상위 파트넘버` + `/` + `애더 코드(쉼표 구분)`
최상위 요소는 하이픈(-)으로 구분한다.

예: `MCRWD-40SLPM-TFTRD-DB15-MODBUS-485-54X54-SAE-EPDM-CC / CM, 102P, RIN, ...`

## Primary Instrument Types (1번째 글자)

| 코드 | 뜻 |
|---|---|
| L | Liquid flow meter |
| M | Gas mass flow meter |
| P | Pressure gauge |

## Secondary Instrument Types (조합)

| 코드 | 뜻 |
|---|---|
| 3 | Remote pressure sense port |
| B | Battery-powered |
| C | Flow or pressure controller |
| D | Dual valves |
| E | Enclosed valve |
| H | Hammerhead valves |
| P | Large Pneutronics valve |
| Q | High pressure gas flow |
| R | High-flow Rolamite valve |
| S | Stainless sensor for corrosives |
| SS | Stainless sensor for corrosives with 316L body |
| T | Stream switching controller |
| V | Enclosed valve plus pneumatic shutoff valve |
| W | Whisper(TM) low pressure drop |

즉 `MC` = M(가스 질량유량) + C(컨트롤러). `MCRHS` = M+C+R(Rolamite)+H(Hammerhead)+S(부식성 스테인리스).

## 레인지 표기

`xSCCM` `xSLPM` (가스 유량) · `xPSIA` `xPSID` `xPSIG` `xTORRA` (압력)

## 디스플레이 옵션

D 흑백 백라이트 · O 표시 없음 · RD 흑백 리모트 · RDE 흑백 리모트 인클로즈드
TFT 컬러 · TFTRD 컬러 리모트 · TFTRDE 컬러 리모트 인클로즈드

## 주의

- `PCA` 는 파트넘버 코드가 **아니다.** 상세페이지에서 밸브 타입 이름으로 쓰고 있는데
  공식 문서에서 확인되지 않았다. `PCV` 는 확인됨. 재확인 전까지 손대지 말 것.
- 스톡 모델 레인지는 stock_models.json 참조.
