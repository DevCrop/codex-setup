# RTK 실시간 보기

파일 HTML은 저장 시점의 스냅샷이다. 실시간 보기는 사용자가 별도로 시작하는
표준 라이브러리 Python 서버와 동일한 보고 템플릿으로 제공한다. OpenAI 기능이나
실제 사용량 측정기가 아니며 RTK의 로컬 추정 집계를 보여 준다.

## 시작

Python 3.11 이상과 이미 검증된 TRACE RTK 설치가 필요하다. `CODEX_HOME`을
지정했다면 서버에도 그대로 전달된다. 아래 보고 폴더는 이 기능을 승인한 PC의
폴더로 바꾼다. 저장소 루트에서 실행한다.

```powershell
./scripts/start_rtk_dashboard.ps1 -ReportsDir 'C:\approved\reports'
```

보고 폴더에는 `rtk-efficiency.template.html`과
`assets/PretendardVariable.woff2`가 있어야 한다. 선택적인
`rtk-efficiency.json`의 `probe`는 마지막 실제 압축 검사 근거다. 없으면 미확인이다.
템플릿과 폰트는 `templates/reports`에서 해당 폴더로 복사할 수 있지만 기존 사용자
수정은 먼저 비교한다. 머신의 집계나 기존 성공 기록은 다른 PC로 복사하지 않는다.

런처는 숨김 서버를 시작하고 실제 준비 파일을 읽어 브라우저를 연다.
같은 보고 폴더의 살아 있는 동일 인스턴스는 재사용한다. `.rtk-live-ready.json`은
URL·프로세스 번호·인스턴스 식별자만 갖는 로컬 상태다. Git에 올리지 않는다.
같은 이름의 기존 파일이 TRACE 준비 기록 형식이 아니면 덮어쓰지 않고 중단한다.
재부팅 후에는 런처를 다시 실행한다. Windows 시작 프로그램이나 신규 자동화는
설치하지 않는다. 사용 종료 시 준비 파일의 번호와 실제 서버 프로세스를 확인한
후 그 서버만 종료할 수 있다. 탭을 닫으면 집계 조회는 멈추고 서버는 대기한다.

다른 플랫폼은 다음 명령으로 시작하고 터미널에 출력된 로컬 URL을 연다.

```text
python -B scripts/rtk_dashboard.py --reports-dir /approved/reports
```

## 데이터 흐름과 표시

1. 보고 화면이 보일 때 2초마다 `/api/rtk`를 읽는다. 조회 소요 시간 뒤 2초를
   기다리므로 정확히 매 2초 도착한다는 보장은 없다.
2. 서버가 기존 `CODEX_HOME/bin/trace_rtk.py`로 `gain --daily --format json`을 읽는다.
   러너의 기존 소유권·바이너리 해시 검사를 거친다. 새 진단 명령은 만들지 않는다.
3. 숫자·날짜 허용 필드만 반환한다. 프로젝트 경로·명령 이력·stderr는 보내지 않는다.
   여러 탭의 동시 요청은 2초 캐시와 직렬 수집으로 합친다.
4. 누적 수치·일별 차트·표·CSV가 함께 갱신된다. 정렬과 차트 선택은 유지된다.
   집계 시각은 초 단위 KST, RTK 기록 날짜는 별도로 표시한다.
5. 저장된 `probe.checked_at`은 그대로다. 집계를 읽었다고 새 압축 검사가
   통과한 것으로 표시하지 않는다. 실제 OpenAI 토큰·달러·구독 잔량은 환산하지 않는다.
6. 숨긴 탭과 일시정지는 조회를 쉬고, 다시 보이면 조회를 재개한다. 연결 실패는
   이전 값을 유지하고 오류 배지를 표시하며 최대 30초까지 재시도 간격을 늘린다.

최초 페이지 요청에서 집계가 실패해도 HTML 화면은 유지한다. 유효한 저장 스냅샷은
원래 수집 시각과 오류 배지로 표시하고, 저장 자료도 없으면 수치·이력은 미확인으로
남긴다. API는 계속 503을 반환하며 성공한 다음 조회만 실제 수치를 갱신한다.
DB 손상 후 일부 이력만 복구한 호스트는 `history_recovery` 허용 필드로 복구 상태와
이전 누적 스냅샷을 구분한다. 이전 집계와 복구 DB를 합산하거나 가짜 기록을
삽입하지 않는다. 선택적 `rtk-history-snapshot.html`은 손상 전 화면을 읽는 링크다.

화면 위의 두 카드는 **이전 누적·고정 스냅샷**과 **현재 DB·별도 집계**다.
현재 DB에는 복구된 과거 기록과 이후 신규 기록이 함께 있다. 순증 실행 수는
현재 실행 수에서 최초 복구 수를 뺀 값이며, 손상 전 누적 대비 증가량이 아니다.
현재 DB로 표시한 KPI·일별 차트·표·CSV는 현재 DB만 사용한다. 같은 화면의
**이전 날짜별 집계**에는 보존된 날짜·실행 수·입력/출력·절감 추정치·절감률을
고정 표와 막대로 표시한다. 이전 기록은 황갈색, 현재 집계는 녹색으로 구분하고
각각의 수집 시각을 따로 유지한다. 같은 날짜도 서로 다른 범위이므로 합산이나
증감률 비교를 하지 않는다. 이전 마지막 날짜도 당시 수집 시점의 값이지 하루의
최종값이 아니다. 빈 날짜는 0으로 만들지 않는다. 아카이브 원본 링크도 유지한다.

### 이전 날짜별 집계를 한 화면에 보존하기

이전 원본 `rtk-history-snapshot.json/html`은 변경하지 않는다. 이 호스트에서
보존한 집계 JSON을 읽어 숫자/날짜 허용 필드만 **호스트 보고 템플릿**의
`<script id="rtk-history-data" type="application/json">` 내용에 투영한다.
필드는 `collected_at`, `arithmetic_difference`, `daily`이며 각 날짜에는
`date`, `commands`, `input_tokens`, `output_tokens`, `saved_tokens`,
`savings_pct`만 넣는다. 원시 명령·경로·DB 행은 복제하지 않는다.
JSON 직렬화 후 `</`를 `<\/`로 이스케이프한다.

공유 템플릿의 이 슬롯은 `{}`다. 다른 PC에 이 호스트 수치를 배포하지 않는다.
현재 집계 슬롯 `__RTK_REPORT_DATA__` 하나는 그대로 유지한다. 일일 생성 시
기존 호스트의 고정 슬롯을 보존하거나 동일한 보존 원본으로 재구성한 뒤 현재
집계를 삽입한다. 라이브 서버는 페이지 요청마다 이 템플릿을 읽으므로 기존
인스턴스를 다시 시작하거나 추가 API/스케줄러를 설치할 필요가 없다.

클라이언트는 페이지를 열 때 고정 집계를 한 번 읽는다. 날짜/숫자·중복 날짜를
검사하고 `history_recovery.previous_collected_at`이 있으면 기준 시각도 대조한다.
유효하지 않거나 시각이 다르면 이전 날짜별 표시는 미확인/보류로 남긴다.
현재 `/api/rtk` 폴링은 기존대로 유지하며 이전 집계를 갱신·합산하지 않는다.
파일 스냅샷에도 같은 고정 집계가 내장되므로 추가 파일 요청 없이 볼 수 있다.

이 서버는 DB 자동 초기화·삭제·복구를 하지 않는다. 실제 손상은 원본과 sidecar의
일관된 보존, 활성 쓰기 확인, 격리 복구 및 무결성/집계 비교 후 승인 범위에서
처리한다. [SQLite 공식 복구](https://sqlite.org/recovery.html)는 복구 데이터가
불완전할 수 있음을 명시한다. 화면 복구와 원래 전체 이력 복구는 별도 판정이다.

실시간 조회는 메모리에서만 동작한다. 일일 정본·날짜별 집계와 저장 HTML을
덮어쓰지 않는다. 기존 등록된 점검은 그 호스트의 실제 일정대로 계속 수집한다.
이 기능이 없던 과거 날짜에 기록을 만들지 않는다.

## DB 재손상 위험과 일일 복구점

손상 발생 원인은 미확인이다. 정상 집계와 백업은 무손상 보장이 아니다.
2026-10-12 확인한 공식 RTK 안정판은 0.51.0이며, 해당 태그는 bundled
rusqlite 0.31을 사용한다. 이 호스트의 검증된 바이너리에서 발견한 SQLite
3.45.0 버전·SOURCE_ID는 [공식 3.45.0 기록](https://sqlite.org/releaselog/3_45_0.html)과
일치했다. [SQLite WAL-reset 안내](https://sqlite.org/wal.html#walresetbug)는
3.7.0–3.51.2의 드문 동시 쓰기/체크포인트 결함과 수정 버전을 설명한다.
이는 재검토할 위험 근거이며 이번 손상의 원인 증명은 아니다.
새 RTK 안정판 검토 때 내장 SQLite의 수정 여부를 확인한다. SQLite 도구를
업데이트해도 RTK에 내장된 SQLite는 교체되지 않는다. 임의 RTK 빌드, DLL 교체,
강제 WAL 전환, synchronous=OFF, VACUUM·수동 체크포인트를 해결책으로 적용하지 않는다.
`gain`은 집계 조회지만 RTK의 일반 DB 초기화 경로를 사용한다. HTTP의 읽기 전용
성격이 RTK 내부 연결까지 SQLite read-only로 강제한다는 뜻은 아니다.

사용자가 이 호스트에서 승인한 일일 DB 보존은 `scripts/rtk_db_maintenance.py`로
실행한다. 새 자동화·훅은 만들지 않는다. 확인한 실제 DB 경로와 사전에 검토한
SQLite 3.51.3+ 도구 및 그 SHA-256을 명시한다. 설치·다운로드·경로 재지정은 하지 않는다.

```text
python -B scripts/rtk_db_maintenance.py --database DATABASE --sqlite REVIEWED_SQLITE --sqlite-sha256 REVIEWED_SHA256
```

1. 소유 경로·링크·도구 해시·버전을 검사한다. 기본 private state는 CODEX_HOME을
   존중하며 `--state`로 기존 사용자 정의 상태를 명시할 수 있다.
2. 원본을 `-readonly`로 열어 quick_check를 실행한다. 일관된 온라인 `.backup`으로
   WAL에 커밋된 데이터까지 새 후보에 포함한다. 원본 DB만 단순 복사하지 않는다.
3. 후보의 전체 integrity_check와 commands 테이블을 검사한 후에만 최신 백업을
   교체한다. 직전 정상 백업 한 개를 유지한다. 잠금/시간 초과/손상/경로 불명확은
   실패로 남기며 기존 정상 백업을 덮어쓰지 않는다. 중단으로 영수증과 파일이
   어긋나도 자동 추정·덮어쓰기 대신 중단한다.
4. 두 DB 백업과 해시 영수증은 private `rtk-db-backup/`에만 둔다. 백업에는 원래
   RTK 이력이 포함되므로 내용을 열람·정규 기록/보고서로 복제·Git 게시하지 않는다.
   `routine-review.json`에는 시각·무결성·크기·건수·해시·실패 상태만 기록한다.
5. 매일 한 번, 또는 실제 DB 오류/승인된 DB 변경 전후에만 검사한다. 매 명령·2초
   화면 조회마다 백업하지 않는다. 기존 일일 집계와 이전 누적 스냅샷도 보존한다.
6. 실패하면 원본·WAL/SHM을 보존하고 자동 초기화·삭제·복구를 하지 않는다.
   활성 DB의 이름 변경/교체 및 sidecar 제거는 금지한다. 복구가 필요한 경우 별도
   검토에서 활성 연결 종료 확인, 격리 복구, 무결성·집계·원래 경로 검증을 수행한다.

이 절차는 조기 감지와 복구 가능성을 높이며 마지막 백업 이후 이력까지 보장하지 않는다.
업스트림 수정 여부·중복 DB 경로·디스크/동기화/강제 종료 가설을 확정 원인으로
표시하지 않는다. 임의 저장소·브라우저 프로필·대화 DB는 이 절차의 대상이 아니다.
근거: [SQLite Online Backup API](https://sqlite.org/backup.html),
[손상 방지 주의사항](https://sqlite.org/howtocorrupt.html),
[quick_check 한계](https://sqlite.org/pragma.html#pragma_quick_check),
[RTK 고정 태그의 초기화](https://github.com/rtk-ai/rtk/blob/v0.51.0/src/core/tracking.rs).

## 범위와 검증

서버는 `127.0.0.1`에만 바인딩하고 임의 포트를 사용한다. 정확한 Host와
동일 Origin만 허용하며 외부 Origin·교차 사이트·임의 경로·쿼리·쓰기 요청을
거부한다. 디렉터리 목록, 파일 업로드, 임의 명령 실행, 공개 호스팅은 제공하지 않는다.
이는 공개 서비스용 서버가 아니다. 경로의 링크·Windows reparse point를 거부하고
기존 설정·훅·인증·권한·자동화 일정을 변경하지 않는다.

```text
python -B scripts/test_rtk_dashboard.py
node scripts/test_rtk_dashboard_client.cjs
python -B scripts/test_rtk_db_maintenance.py
python -B scripts/validate_repo.py
```

테스트는 수집 명령 고정, 캐시, 숫자·날짜 검증, 실패 시 오래된 값의 성공 처리 방지,
HTTP 경계, UI의 자동 갱신·숨김·일시정지·실패·동시 조회 방지를 확인한다.
DOM 대역을 쓴 스크립트 검사는 실제 브라우저 렌더링 증거와 구분한다.

설계 근거: [Python HTTP server](https://docs.python.org/3/library/http.server.html),
[Page Visibility API](https://developer.mozilla.org/en-US/docs/Web/API/Page_Visibility_API).
