---
name: weather-fetcher
description: 두바이(UAE)의 현재 기상 온도 데이터를 Open-Meteo API에서 가져오는 지침입니다
user-invocable: false
---

# 날씨 가져오기 스킬

이 스킬은 현재 날씨 데이터를 가져오는 지침을 제공합니다.

## 작업

두바이(UAE)의 현재 온도를 요청된 단위(섭씨 또는 화씨)로 가져옵니다.

## 지침

1. **날씨 데이터 가져오기**: WebFetch 도구를 사용하여 Open-Meteo API에서 두바이의 현재 날씨 데이터를 가져옵니다.

   **섭씨**의 경우:
   - URL: `https://api.open-meteo.com/v1/forecast?latitude=25.2048&longitude=55.2708&current=temperature_2m&temperature_unit=celsius`

   **화씨**의 경우:
   - URL: `https://api.open-meteo.com/v1/forecast?latitude=25.2048&longitude=55.2708&current=temperature_2m&temperature_unit=fahrenheit`

2. **온도 추출**: JSON 응답에서 현재 온도를 추출합니다:
   - 필드: `current.temperature_2m`
   - 단위 라벨: `current_units.temperature_2m`

3. **결과 반환**: 온도 값과 단위를 명확하게 반환합니다.

## 예상 출력

이 스킬의 지침을 완료한 후:
```
Current Dubai Temperature: [X]°[C/F]
Unit: [Celsius/Fahrenheit]
```

## 참고사항

- 온도만 가져오고, 변환하거나 파일을 작성하지 않습니다
- Open-Meteo는 무료이며 API 키가 필요 없고, 신뢰성을 위해 좌표 기반 조회를 사용합니다
- 두바이 좌표: 위도 25.2048, 경도 55.2708
- 숫자 온도 값과 단위를 명확하게 반환합니다
- 호출자의 요청에 따라 섭씨와 화씨 모두 지원합니다
