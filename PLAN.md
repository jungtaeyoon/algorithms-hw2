# 구현 계획

## 1. Base62 모듈과 입력 검증
- `src/base62.py`에 `encode(n)`과 `decode(s)`를 만든다.
- 문자 알파벳을 `0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ`로 고정한다.
- `encode(0)`은 `"0"`으로 반환한다.
- 음수, 실수, 부울, 빈 문자열, 알파벳 밖 문자를 명세에 맞게 거절한다.
- 이 단계의 경계 사례는 구현 전에 `tests/test_base62.py`에 작성한다.

## 2. 개별 체이닝 해시 테이블
- `src/hash_table.py`에 직접 구현한 체이닝 해시 테이블을 만든다.
- 배열과 연결 노드만 사용하고 `dict`, `set`, 내장 `hash()`를 사용하지 않는다.
- 문자열 키를 문자 단위 호너 해시로 계산한 뒤 테이블 크기로 나눈 나머지를 배열 인덱스로 한다.
- 초기 크기는 11로 하고 충돌은 각 배열 칸의 연결 리스트로 해결한다.
- 기존 키는 값을 갱신하고 새 키는 연결 리스트 앞에 삽입한다.
- 적재율이 0.75를 넘으면 다음 소수 크기로 확장한다.
- `put`, `get`, `remove`, `contains`, `__len__`, `__contains__`를 제공한다.
- 없는 키 조회와 삭제 동작을 테스트에서 고정한다.

## 3. 단축기 API
- `src/shortener.py`에 `shorten(url)`과 `expand(code)`를 만든다.
- 내부 식별자는 1부터 시작하고 새 URL마다 1씩 증가한다.
- 식별자를 `encode()`로 변환해 단축 코드를 만든다.
- 이미 단축된 URL은 기존 코드를 재사용한다.
- URL과 코드 각각을 해시 테이블에 저장한다.
- URL 형식과 타입을 검증하고 유효하지 않은 입력은 명세의 예외로 거절한다.

## 4. 테스트 우선 구현 검증
- 명세의 경계 사례를 `tests/test_base62.py`, `tests/test_hash_table.py`,
  `tests/test_shortener.py`로 나눠 작성한다.
- 구현 이후에는 테스트를 기준으로만 동작을 수정한다.
- `make test`로 전체 테스트를 실행한다.
- VS Code의 unittest 발견 설정이 계속 동작하는지 확인한다.

## 5. 웹 서버
- 표준 라이브러리 `http.server`를 사용해 `src/server.py`를 만든다.
- 기본 포트 8000으로 실행 가능한 `make serve` 흐름을 제공한다.
- `GET /`, `POST /shorten`, `GET /<code>`, `GET /table`을 구현한다.
- `/table`에는 배열 칸, 연결 리스트, 호너 해시 계산과 최종 인덱스를 표시한다.
- 잘못된 URL은 400, 없는 코드는 404, 정상 리다이렉트는 302로 응답한다.

## 6. 최종 점검
- 모든 구현에서 금지된 `dict`, `set`, 내장 `hash()` 호출이 없는지 검사한다.
- 전체 단위 테스트와 서버 라우트 수동 확인을 수행한다.
- 각 단계의 변경은 별도 feature 브랜치와 GitHub 이슈로 관리한다.
