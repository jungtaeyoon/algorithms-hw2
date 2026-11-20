# 구현 계획

에이전트에게 "코드는 쓰지 말고 계획만" 요청해 받은 것을 검토하고 고친 결과다.
줄이 그어진 항목은 검토하며 뺀 것이다.

1. `src/hash_table.py`: 개별 체이닝 테이블. 칸마다 연결 리스트, 호너 해시, 적재율을 넘으면 칸 수를 두 배
2. `tests/test_hash_table.py`: 명세 6절의 해시 경계 사례
3. `src/shortener.py`: 일련번호 + base62, `HashTable` 두 개(URL→코드, 코드→URL)
4. `tests/test_shortener.py`: 명세 6절의 단축기 경계 사례
5. `experiments/probe_experiment.py`: 칸 수를 고정한 테이블에서 적재율별 평균 비교 노드 수
6. `src/server.py`: `http.server`로 폼, 단축, 이동

검토하며 바꾼 것

- ~~코드를 URL의 해시값으로 만든다~~ → 일련번호로 바꿨다. 해시값을 코드로 쓰면 다른
  URL이 같은 코드를 받을 수 있고, 그것을 또 처리해야 한다.
- ~~Python `dict`로 URL→코드를 저장한다~~ → 명세 3절 위반. 직접 만든 테이블을 쓴다.
- 테스트를 구현보다 먼저 쓰게 순서를 바꿨다.
