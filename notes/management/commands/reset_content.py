from __future__ import annotations

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone


class Command(BaseCommand):
    help = "Delete all blog posts/notes and recreate a curated long-form set."

    @transaction.atomic
    def handle(self, *args, **options):
        from blog.models import Post
        from notes.models import Category, Note

        self.stdout.write("Deleting existing posts/notes/categories...")
        Post.objects.all().delete()
        Note.objects.all().delete()
        Category.objects.all().delete()

        category_names = [
            "Backend",
            "Programming",
            "Infra",
            "Database",
            "AI-Math",
            "Network",
            "Frontend",
            "UI-UX",
            "Certification",
        ]
        categories = {name: Category.objects.create(name=name) for name in category_names}

        now = timezone.now()

        def html(*parts: str) -> str:
            return "\n".join(p for p in parts if p).strip() + "\n"

        def ul(items: list[str]) -> str:
            return "<ul>\n" + "\n".join(f"<li>{x}</li>" for x in items) + "\n</ul>"

        def ol(items: list[str]) -> str:
            return "<ol>\n" + "\n".join(f"<li>{x}</li>" for x in items) + "\n</ol>"

        def pre(code: str) -> str:
            escaped = (
                code.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
            )
            return f"<pre><code>{escaped}</code></pre>"

        def render_post(spec: dict) -> str:
            parts: list[str] = [
                "<h2>요약</h2>",
                f"<p>{spec['intro']}</p>",
                "<h2>핵심 개념</h2>",
                ul(spec["core"]),
                "<h2>어떻게 작동하나</h2>",
                ol(spec["flow"]),
                "<h2>실무 포인트</h2>",
                ul(spec["practice"]),
                "<h2>자주 하는 실수</h2>",
                ul(spec["pitfalls"]),
                "<h2>추가 키워드</h2>",
                ul(spec["keywords"]),
            ]
            if code := spec.get("code"):
                parts.insert(6, "<h2>짧은 예시</h2>")
                parts.insert(7, pre(code))
            if closing := spec.get("closing"):
                parts.append("<h2>정리</h2>")
                parts.append(f"<p>{closing}</p>")
            return html(*parts)

        def render_note(spec: dict) -> str:
            parts = [
                "<h2>중요 키워드</h2>",
                ul(spec["keywords"]),
                "<h2>예시로 정리</h2>",
                ul(spec["examples"]),
                "<h2>느낀점</h2>",
                "\n".join(f"<p>{x}</p>" for x in spec["reflections"]),
            ]
            return html(*parts)

        def specs_for_topic(
            *,
            topic: str,
            category: str,
            titles: list[str],
            intro: str,
            core_base: list[str],
            flow_base: list[str],
            practice_base: list[str],
            pitfalls_base: list[str],
            keywords_base: list[str],
            focuses: list[dict] | None = None,
        ) -> list[dict]:
            focuses = focuses or [{} for _ in titles]
            if len(focuses) != len(titles):
                raise ValueError(f"{topic}: focuses length mismatch")

            out: list[dict] = []
            for title, focus in zip(titles, focuses):
                out.append(
                    {
                        "topic": topic,
                        "category": category,
                        "title": title,
                        "intro": focus.get("intro", intro),
                        "core": core_base + focus.get("core", []),
                        "flow": flow_base + focus.get("flow", []),
                        "practice": practice_base + focus.get("practice", []),
                        "pitfalls": pitfalls_base + focus.get("pitfalls", []),
                        "keywords": keywords_base + focus.get("keywords", []),
                        "code": focus.get("code"),
                        "closing": focus.get("closing"),
                    }
                )
            return out

        posts: list[dict] = []

        # Django (3)
        posts += specs_for_topic(
            topic="Django",
            category="Backend",
            titles=[
                "[Django] MVT를 ‘요청→응답’ 흐름으로 이해하기",
                "[Django] ORM 성능: N+1을 발견하고 고치기",
                "[Django] 인증 기본기: 세션/쿠키/CSRF 연결하기",
            ],
            intro="용어를 외우기보다 흐름(어디서 무엇이 결정되는지)을 잡으면 디버깅 속도가 확 올라간다.",
            core_base=[
                "URLConf는 요청 경로를 View로 매핑한다",
                "View는 ‘조회/검증/처리/응답’을 조합하는 곳이다",
                "ORM은 쿼리를 조합해 DB를 객체처럼 다룬다",
                "Template은 표현에 집중하고 로직은 최소화한다",
            ],
            flow_base=[
                "브라우저 요청 → <code>urls.py</code> 패턴 매칭",
                "View 실행 → 필요한 데이터(ORM) 조회/가공",
                "<code>render()</code>로 템플릿 + context 렌더링",
                "응답 반환 → 브라우저 렌더링",
            ],
            practice_base=[
                "리스트/검색 페이지는 항상 쿼리 개수부터 확인한다",
                "FK는 <code>select_related</code>, M2M/역참조는 <code>prefetch_related</code>",
                "검증은 Form/Serializer 등으로 분리해 View를 가볍게 유지한다",
                "권한/인증 실패는 401/403을 구분해 응답한다",
            ],
            pitfalls_base=[
                "템플릿 루프 안에서 ORM 접근을 반복해 N+1이 생김",
                "View에 비즈니스 로직이 누적되어 테스트/유지보수가 어려워짐",
                "쿠키 기반 인증인데 CSRF를 가볍게 보는 실수",
            ],
            keywords_base=[
                "MVT",
                "URLConf",
                "select_related",
                "prefetch_related",
                "session/cookie",
                "CSRF",
            ],
            focuses=[
                {
                    "code": "def post_detail(request, pk):\n    post = Post.objects.get(pk=pk)\n    return render(request, 'blog/post_detail.html', {'post': post})\n",
                    "closing": "요청이 어디서 어떤 코드를 타는지 ‘지도’를 만들면, 문제의 위치도 그 지도 위에서 바로 찾을 수 있다.",
                },
                {
                    "intro": "‘그냥 느리다’는 증상은 대부분 ORM 쿼리 폭증으로 시작한다. N+1을 잡는 습관이 가장 큰 차이를 만든다.",
                    "core": [
                        "N+1 = 1번 조회 + N번 반복 조회",
                        "쿼리 수를 고정(2~3개 수준)하는 게 목표다",
                    ],
                    "flow": [
                        "리스트 화면에서 연관 객체를 반복 접근 → 추가 쿼리 발생",
                        "필요한 연관을 미리 로드해 반복 조회를 제거",
                    ],
                    "practice": ["디버깅 도구(쿼리 로그/툴바)로 ‘몇 번 나가는지’부터 숫자로 본다"],
                    "code": "qs = Post.objects.select_related('author').prefetch_related('categories')\nfor p in qs:\n    print(p.author.username, [c.name for c in p.categories.all()])\n",
                },
                {
                    "intro": "로그인은 비밀번호 확인이 아니라 ‘다음 요청에서도 사용자를 식별하는 상태 관리’다.",
                    "core": [
                        "쿠키에는 보통 세션 키만 담기고, 실제 상태는 서버가 가진다",
                        "<code>SameSite</code>/<code>Secure</code> 같은 옵션이 보안에 직접 영향",
                    ],
                    "flow": [
                        "로그인 성공 → 세션 생성/저장",
                        "응답에 세션 키 쿠키 전달",
                        "이후 요청마다 쿠키로 사용자 식별",
                        "CSRF 토큰으로 ‘의도한 요청’인지 확인",
                    ],
                    "practice": [
                        "HTTPS라면 <code>SESSION_COOKIE_SECURE</code>를 점검한다",
                        "POST 요청은 CSRF 토큰 포함 여부를 먼저 확인한다",
                    ],
                },
            ],
        )

        # Linux (3)
        posts += specs_for_topic(
            topic="Linux",
            category="Infra",
            titles=[
                "[Linux] 권한/소유권: chmod/chown을 실수 없이 쓰기",
                "[Linux] 프로세스/서비스 진단: ps/top/systemd 기본",
                "[Linux] 로그 읽기: grep/tail/journalctl로 범위 좁히기",
            ],
            intro="리눅스는 ‘외우는 명령어’보다 ‘문제를 좁히는 순서’가 중요하다.",
            core_base=[
                "권한은 user/group/other로 나뉜다",
                "r=4, w=2, x=1의 합으로 755 같은 숫자 권한을 만든다",
                "장애 대응은 로그 + 리소스(CPU/메모리/디스크/FD)를 같이 본다",
                "systemd 환경에서는 journal이 표준 로그 채널이다",
            ],
            flow_base=[
                "증상(느림/죽음/재시작)을 먼저 분류한다",
                "프로세스 상태/리소스를 확인한다",
                "서비스 단위로 로그 범위를 좁힌다",
                "원인을 가정 → 재현/검증으로 확정한다",
            ],
            practice_base=[
                "<code>ls -l</code>로 권한/소유권을 ‘읽는 습관’을 만든다",
                "<code>systemctl status</code> + <code>journalctl -u</code> 조합을 익힌다",
                "디스크(<code>df</code>)와 열린 파일(<code>lsof</code>)을 같이 확인한다",
                "<code>grep -C</code>로 앞뒤 문맥까지 읽는다",
            ],
            pitfalls_base=[
                "원인을 모른 채 <code>chmod -R 777</code> 같은 강제 해결을 해버림",
                "로그 한 줄만 보고 결론을 내림(문맥 부족)",
                "디스크 가득 참/FD 고갈 같은 시스템 이슈를 놓침",
            ],
            keywords_base=["chmod", "chown", "ps/top", "systemctl", "journalctl", "grep/tail"],
            focuses=[
                {"code": "chmod 640 .env\nchown app:app /var/www/app/.env\n"},
                {"code": "systemctl status gunicorn\njournalctl -u gunicorn -f\n"},
                {"code": "tail -f app.log\ngrep -n \"ERROR\" -C 3 app.log\n"},
            ],
        )

        # Python (5)
        posts += specs_for_topic(
            topic="Python",
            category="Programming",
            titles=[
                "[Python] 매직 메서드: 객체를 파이썬답게 만들기",
                "[Python] 예외 처리: 실패를 통제 가능한 형태로 바꾸기",
                "[Python] 제너레이터: 큰 데이터를 안전하게 처리하기",
                "[Python] 타입 힌트: 협업/리팩터링을 돕는 도구",
                "[Python] 테스트 습관: 리팩터링이 무섭지 않게",
            ],
            intro="파이썬은 빨리 만들기 쉽지만, 오래 가는 코드는 ‘읽기 쉬움’과 ‘실수 방지 장치’가 만든다.",
            core_base=[
                "데이터 모델(매직 메서드)은 객체의 사용성을 결정한다",
                "예외는 숨기지 말고 의미 있는 메시지/분류로 다룬다",
                "제너레이터는 메모리 사용을 줄이는 핵심 도구다",
                "타입/테스트는 협업과 리팩터링의 안전망이다",
            ],
            flow_base=[
                "문제가 생기면 먼저 실패 유형을 분류한다(입력 오류/외부 장애/버그)",
                "인터페이스(입출력)를 명확히 정의한다(타입/계약)",
                "데이터 흐름을 스트리밍/분리해 단순화한다",
                "테스트로 기대 동작을 고정한다",
            ],
            practice_base=[
                "__repr__/__str__로 디버깅 정보를 남긴다",
                "예외는 가능한 한 좁게 잡고, 상위 계층에 의미를 전달한다",
                "큰 입력은 리스트로 만들기보다 이터레이터/제너레이터로 처리한다",
                "테스트는 AAA(Arrange-Act-Assert) 구조로 작성한다",
            ],
            pitfalls_base=[
                "광범위한 <code>except:</code>로 오류를 삼켜서 디버깅이 어려워짐",
                "중첩 컴프리헨션/거대한 함수로 가독성이 무너짐",
                "대용량 데이터를 한 번에 메모리에 올려 OOM이 남",
            ],
            keywords_base=["__repr__", "exceptions", "with", "yield", "type hints", "unit test"],
            focuses=[
                {"code": "class Bag:\n    def __init__(self, items):\n        self._items = list(items)\n    def __len__(self):\n        return len(self._items)\n    def __iter__(self):\n        return iter(self._items)\n"},
                {"core": ["‘잡을 수 있는 예외만 잡기’가 안전한 기준이다"]},
                {"code": "def read_lines(path):\n    with open(path, 'r', encoding='utf-8') as f:\n        for line in f:\n            yield line.rstrip('\\n')\n"},
                {"core": ["경계(입력/출력)부터 타입을 붙이면 효율이 크다"]},
                {"core": ["테스트는 ‘바꿀 수 있게 만드는 것’이 가장 큰 가치다"]},
            ],
        )

        # DB (3)
        posts += specs_for_topic(
            topic="DB",
            category="Database",
            titles=[
                "[DB] 정규화/반정규화: 원칙으로 시작해 측정으로 바꾸기",
                "[DB] 트랜잭션/락: 동시성에서 발생하는 문제 이해하기",
                "[DB] 인덱스 설계: 많이 만든다고 빨라지지 않는다",
            ],
            intro="데이터베이스는 ‘정답’보다 ‘트래픽/쿼리 패턴’이 결정을 만든다. 측정(EXPLAIN/슬로우 로그)으로 판단하자.",
            core_base=[
                "정규화는 중복을 줄이고 무결성을 높인다",
                "반정규화는 읽기를 빠르게 하지만 갱신 비용이 늘 수 있다",
                "격리수준/락은 안정성과 처리량의 타협이다",
                "인덱스는 읽기↑ 쓰기↓, 쿼리 패턴 기반으로 설계한다",
            ],
            flow_base=[
                "문제(느림/대기/타임아웃)를 관측한다",
                "가장 느린 쿼리를 찾는다(슬로우 로그/모니터링)",
                "EXPLAIN으로 실행 계획을 확인한다",
                "인덱스/쿼리/트랜잭션 범위를 조정한다",
            ],
            practice_base=[
                "트랜잭션은 짧게, 잠금 범위를 좁게 유지한다",
                "조건/정렬 컬럼을 기준으로 인덱스를 검토한다",
                "반정규화는 ‘병목 확인 후’ 제한적으로 도입한다",
            ],
            pitfalls_base=[
                "인덱스를 무작정 추가해 쓰기 성능이 급격히 저하됨",
                "긴 트랜잭션으로 락이 오래 잡혀 장애가 전파됨",
                "EXPLAIN 없이 ‘감’으로 튜닝함",
            ],
            keywords_base=["normalization", "transaction", "isolation", "lock", "index", "EXPLAIN"],
        )

        # AI Math (5)
        posts += specs_for_topic(
            topic="AI-Math",
            category="AI-Math",
            titles=[
                "[AI·수학] 벡터/행렬: 모델이 숫자를 다루는 방식",
                "[AI·수학] 미분/경사하강: 학습이 내려가는 이유",
                "[AI·수학] 확률/통계: 불확실성을 다루는 기본기",
                "[AI·수학] 손실함수: 목표를 정하면 학습이 보인다",
                "[AI·수학] 과적합/정규화: 외우지 말고 일반화하기",
            ],
            intro="수학은 공식 암기보다 ‘무슨 문제를 해결하려고 등장했는지’를 잡으면 학습이 빨라진다.",
            core_base=[
                "벡터는 특성(feature)의 묶음이며, 유사도/거리를 계산할 수 있다",
                "미분(gradient)은 손실을 줄이는 방향 정보를 준다",
                "확률/통계는 노이즈/불확실성을 모델링한다",
                "손실함수는 ‘무엇을 벌점 줄지’를 정한다",
                "정규화는 과적합을 줄여 일반화를 돕는다",
            ],
            flow_base=[
                "데이터를 벡터로 표현한다",
                "모델이 예측을 만들고 손실을 계산한다",
                "미분으로 기울기를 구해 파라미터를 업데이트한다",
                "검증 데이터로 과적합을 감시하고 규제를 조정한다",
            ],
            practice_base=[
                "학습/검증 곡선으로 과적합 시점을 판단한다",
                "손실과 평가 지표를 연결해서 해석한다",
                "차원(shape)을 항상 확인해 행렬 곱 오류를 줄인다",
            ],
            pitfalls_base=[
                "공식만 외우고 ‘무엇을 의미하는지’를 놓침",
                "학습률을 무작정 올/내려서 발산/정체를 반복",
                "불균형 데이터에서 정확도만 보고 착각함",
            ],
            keywords_base=["vector", "matrix", "gradient", "loss", "regularization", "bias-variance"],
            focuses=[
                {},
                {"code": "w = w - lr * grad_w\nb = b - lr * grad_b\n"},
                {},
                {},
                {},
            ],
        )

        # Network (3)
        posts += specs_for_topic(
            topic="Network",
            category="Network",
            titles=[
                "[Network] TCP vs UDP: 빠름이 아니라 ‘보장’의 선택",
                "[Network] HTTP 상태코드: 숫자가 아니라 의사소통",
                "[Network] DNS→TLS→HTTP: 브라우저 요청의 숨은 단계",
            ],
            intro="웹 문제를 서버 코드만으로 보면 원인을 놓치기 쉽다. 네트워크 단계를 ‘연결된 지도’로 갖고 있어야 한다.",
            core_base=[
                "TCP는 연결/순서/재전송/혼잡 제어를 제공한다",
                "UDP는 지연이 중요할 때 선택되지만, 앱이 많은 책임을 진다",
                "HTTP 상태코드는 클라이언트와 서버의 계약이다",
                "DNS/TLS 단계에서 실패하면 앱 로그가 비어 있을 수도 있다",
            ],
            flow_base=[
                "DNS로 도메인→IP 조회",
                "TCP 연결, HTTPS면 TLS 핸드셰이크",
                "HTTP 요청/응답",
                "상태코드/에러 구조로 다음 행동 결정",
            ],
            practice_base=[
                "401(인증 필요)과 403(권한 없음)을 구분한다",
                "타임아웃/재전송의 로그 신호를 볼 수 있게 설정한다",
                "클라이언트(브라우저 네트워크 탭)와 서버 로그를 같이 본다",
            ],
            pitfalls_base=[
                "상태코드를 아무 숫자로 보내서 클라이언트가 오해함",
                "DNS/인증서 문제를 앱 문제로 착각함",
                "TCP 재전송/혼잡 징후를 모르면 ‘그냥 느림’으로 끝남",
            ],
            keywords_base=["TCP", "UDP", "HTTP status", "DNS", "TLS", "timeout"],
        )

        # JS (2)
        posts += specs_for_topic(
            topic="JS",
            category="Frontend",
            titles=[
                "[JS] 이벤트 루프: 비동기 실행 순서를 예측하기",
                "[JS] fetch + async/await: 실패 케이스까지 포함하기",
            ],
            intro="비동기는 ‘마법’이 아니라 실행 순서 규칙이다. 이 규칙을 알면 디버깅이 쉬워진다.",
            core_base=[
                "Call Stack, Task Queue, Microtask Queue 구조를 이해한다",
                "Promise 콜백은 microtask라서 우선 실행될 수 있다",
                "fetch는 HTTP 오류에서 reject되지 않으므로 <code>res.ok</code>를 확인한다",
            ],
            flow_base=[
                "동기 코드는 Call Stack에서 즉시 실행",
                "Promise 콜백은 microtask로 먼저 처리",
                "그 다음 task queue 콜백 처리",
                "네트워크 응답 처리 후 UI 업데이트",
            ],
            practice_base=[
                "실패 경로(네트워크 오류/HTTP 오류)를 분리해 처리한다",
                "로딩/에러 UI 상태를 명확히 만든다",
                "try/catch(async) 또는 .catch로 에러를 표준화한다",
            ],
            pitfalls_base=[
                "실행 순서를 모르고 setTimeout/Promise가 섞인 버그를 만듦",
                "fetch의 HTTP 오류를 성공으로 착각함",
                "에러를 콘솔에만 찍고 사용자 UX는 방치함",
            ],
            keywords_base=["event loop", "microtask", "Promise", "async/await", "fetch", "res.ok"],
            focuses=[
                {},
                {
                    "code": "const res = await fetch('/api/posts');\nif (!res.ok) throw new Error(`HTTP ${res.status}`);\nconst data = await res.json();\n",
                    "closing": "요청 코드는 성공보다 실패 처리에서 품질이 갈린다. ‘어떤 실패를 어떤 메시지로 바꿀지’가 핵심이다.",
                },
            ],
        )

        # UI/UX (2)
        posts += specs_for_topic(
            topic="UI-UX",
            category="UI-UX",
            titles=[
                "[UI/UX] 폼 UX: 사용자가 실수하지 않게 만들기",
                "[UI/UX] 정보 구조(IA): 큰 카테고리부터 잡기",
            ],
            intro="UI/UX는 ‘예쁜 화면’보다 ‘실수를 줄이고 선택을 쉽게 만드는 구조’에서 결정된다.",
            core_base=[
                "폼은 라벨/에러/피드백이 핵심이다",
                "에러 메시지는 해결 방법까지 포함해야 한다",
                "IA는 사용자 목표(Goal) 중심으로 큰 덩어리를 먼저 만든다",
                "접근성(키보드 탭 이동 등)은 기본 품질이다",
            ],
            flow_base=[
                "사용자 목표를 정의한다",
                "큰 카테고리로 정보를 묶는다",
                "폼 입력/검증/피드백 흐름을 설계한다",
                "실사용 로그/피드백으로 반복 개선한다",
            ],
            practice_base=[
                "라벨을 placeholder로 대체하지 않는다",
                "로딩/비활성 상태를 명확히 표시한다",
                "카테고리는 과세분화보다 검색/필터와 역할 분담한다",
            ],
            pitfalls_base=[
                "에러를 ‘오류’ 한 줄로 끝내서 사용자가 막힘",
                "메뉴/카테고리를 기능 추가 때마다 늘려서 길을 잃게 함",
                "키보드/모바일 입력을 고려하지 않아 이탈이 생김",
            ],
            keywords_base=["form UX", "validation", "error message", "IA", "accessibility", "feedback"],
        )

        # 정보처리기능사 (6)
        posts += specs_for_topic(
            topic="Certification",
            category="Certification",
            titles=[
                "[정보처리기능사] 공부 로드맵: 개념→기출→오답으로 반복",
                "[정보처리기능사] 운영체제: 프로세스/스케줄링/교착상태",
                "[정보처리기능사] 데이터베이스: 키/정규화/SQL 기본",
                "[정보처리기능사] 네트워크: OSI 7계층을 기능으로 연결",
                "[정보처리기능사] 알고리즘·자료구조: 정렬/탐색/스택·큐 집중",
                "[정보처리기능사] 기출 회독 전략: 오답을 자산으로 만들기",
            ],
            intro="자격증 공부는 ‘많이 풀기’보다 ‘다시 안 틀리기’를 만드는 과정이다. 오답을 분류하면 효율이 급상승한다.",
            core_base=[
                "오답은 개념/용어/실수/해석 문제로 분류한다",
                "교착상태 4조건은 세트로 외운다",
                "PK/FK와 정규화 목적을 문장으로 설명할 수 있어야 한다",
                "OSI는 2~4계층 키워드(MAC/IP/Port)가 출제 핵심이다",
            ],
            flow_base=[
                "큰 개념을 먼저 잡고 용어 지도를 만든다",
                "기출을 풀어 빈틈을 찾는다",
                "오답을 유형별로 묶어 반복한다",
                "시험 직전에는 오답/요약 회독으로 마무리한다",
            ],
            practice_base=[
                "틀린 이유를 1문장으로 정리한다",
                "헷갈리는 개념은 비교 표로 고정한다",
                "시간복잡도는 표 + 한 줄 설명으로 암기한다",
            ],
            pitfalls_base=[
                "오답을 ‘찍어서 틀림’으로 넘겨 다시 반복함",
                "정답 근거 없이 외워서 변형 문제에 흔들림",
                "시험 직전에 새로운 문제를 늘려 불안을 키움",
            ],
            keywords_base=["오답 노트", "교착상태 4조건", "PK/FK", "정규화", "OSI", "시간복잡도"],
        )

        # Requested counts: 3+3+5+3+5+3+2+2+6 = 32
        if len(posts) != 32:
            raise RuntimeError(f"expected 32 posts, got {len(posts)}")

        self.stdout.write("Creating posts...")
        for i, spec in enumerate(posts):
            post = Post.objects.create(
                title=spec["title"],
                content=render_post(spec),
                created_at=now - timedelta(days=60 - i, hours=(i * 3) % 12),
            )
            post.categories.set([categories[spec["category"]]])

        notes: list[dict] = [
            {
                "title": "Django 노트: 흐름을 알면 디버깅이 빨라진다",
                "category": "Backend",
                "keywords": ["URLConf", "View 책임", "N+1", "select_related", "prefetch_related", "세션/쿠키", "CSRF"],
                "examples": [
                    "리스트 화면에서 연관 객체를 보여줄 때 쿼리 수가 폭증하면 N+1을 의심한다",
                    "쿠키에는 세션 키가 담기고, 서버가 상태를 가진다는 구조로 보안 설정을 이해한다",
                ],
                "reflections": [
                    "‘동작한다’에서 끝내지 않고, 어디서 무엇이 결정되는지 지도를 만들면 디버깅이 빨라졌다.",
                    "ORM은 편해서 더 위험했다. 쿼리 개수를 숫자로 보니 실무 코드가 달라 보였다.",
                ],
            },
            {
                "title": "Linux 노트: 권한/프로세스/로그를 한 세트로 보기",
                "category": "Infra",
                "keywords": ["chmod", "chown", "user/group/other", "ps/top", "systemctl", "journalctl", "grep -C"],
                "examples": [
                    "Permission denied면 소유권과 디렉터리 x 권한부터 확인한다",
                    "서비스 재시작 루프면 Exit code와 직전 로그를 먼저 본다",
                ],
                "reflections": [
                    "추측보다 관측이 먼저라는 걸 배웠다. 리소스와 로그를 같이 보면 원인이 빨리 좁혀졌다.",
                    "명령어를 외우기보다, 증상별로 무엇을 확인할지 ‘순서’가 생겼다.",
                ],
            },
            {
                "title": "Python 노트: 읽기 쉬움이 곧 생산성이다",
                "category": "Programming",
                "keywords": ["데이터 모델", "__repr__", "예외 범위", "with", "yield", "type hints", "tests"],
                "examples": [
                    "__iter__/__len__ 같은 작은 구현이 객체 사용성을 크게 바꾼다",
                    "대용량 입력은 리스트 대신 제너레이터로 처리하면 안전하다",
                ],
                "reflections": [
                    "빨리 짜는 코드는 쉬웠지만, 오래 가는 코드는 결국 가독성과 규칙이 만들었다.",
                    "테스트를 ‘나중에’가 아니라 ‘바꿀 수 있게’ 만드는 장치로 보게 됐다.",
                ],
            },
            {
                "title": "DB 노트: 동시성(락)과 측정(EXPLAIN)이 핵심",
                "category": "Database",
                "keywords": ["정규화", "반정규화", "트랜잭션", "격리수준", "락", "인덱스", "EXPLAIN"],
                "examples": [
                    "느린 UPDATE는 인덱스 부재로 넓게 스캔하며 락을 오래 잡는지 의심한다",
                    "인덱스는 많이보다 정확히: 쿼리 패턴 기반으로 만든다",
                ],
                "reflections": [
                    "DB는 ‘정답’보다 트래픽이 결정을 만든다는 말이 체감됐다.",
                    "감으로 튜닝하지 않고 EXPLAIN으로 숫자를 보는 습관이 중요했다.",
                ],
            },
            {
                "title": "AI·수학 노트: 공식보다 ‘왜 필요한가’가 먼저",
                "category": "AI-Math",
                "keywords": ["벡터/행렬", "gradient", "확률/분산", "손실함수", "과적합", "정규화", "bias-variance"],
                "examples": [
                    "손실함수는 모델이 무엇을 벌점 줄지(목표)를 정한다",
                    "학습/검증 곡선이 갈라지면 과적합을 의심하고 규제를 조정한다",
                ],
                "reflections": [
                    "공식만 외우면 잊었는데, 문제-도구 연결로 이해하니 오래 남았다.",
                    "손실/지표를 같이 보니 튜닝이 ‘감’이 아니라 ‘판단’이 됐다.",
                ],
            },
            {
                "title": "Network 노트: 앞단(DNS/TLS)을 알면 장애가 보인다",
                "category": "Network",
                "keywords": ["TCP/UDP", "HTTP status", "401 vs 403", "DNS", "TLS", "timeout", "retransmission"],
                "examples": [
                    "앱 로그가 비어도 DNS/TLS 단계에서 실패했을 수 있다",
                    "상태코드를 올바르게 쓰면 클라이언트 행동과 디버깅이 쉬워진다",
                ],
                "reflections": [
                    "서버 코드만 보던 시야가 네트워크 단계까지 확장되면서 원인 파악이 빨라졌다.",
                    "‘웹이 안 된다’는 증상이 생각보다 많은 단계에서 발생할 수 있음을 체감했다.",
                ],
            },
            {
                "title": "JavaScript 노트: 비동기에서 중요한 건 실패 처리",
                "category": "Frontend",
                "keywords": ["event loop", "microtask", "Promise", "async/await", "fetch", "res.ok", "error UI"],
                "examples": [
                    "Promise 콜백은 microtask라서 setTimeout보다 먼저 실행될 수 있다",
                    "fetch는 404여도 reject되지 않으니 res.ok를 체크한다",
                ],
                "reflections": [
                    "성공 흐름보다 실패 케이스를 꼼꼼히 다루는 순간 코드 품질이 갈린다고 느꼈다.",
                    "실행 순서를 예측할 수 있게 되니 디버깅 시간이 확 줄었다.",
                ],
            },
            {
                "title": "UI/UX 노트: 실수를 줄이고 선택을 쉽게 만들기",
                "category": "UI-UX",
                "keywords": ["라벨", "에러 메시지", "로딩 상태", "접근성", "정보 구조(IA)", "용어 일관성"],
                "examples": [
                    "에러 메시지는 ‘오류’가 아니라 ‘어떻게 고치는지’를 알려줘야 한다",
                    "카테고리는 과세분화보다 큰 덩어리로 먼저 잡고, 검색/필터로 보완한다",
                ],
                "reflections": [
                    "UX는 감각이 아니라 사용자의 행동을 예측해 설계하는 일이라는 걸 알게 됐다.",
                    "작은 피드백(로딩/비활성)만 잘 줘도 사용자의 불안을 크게 줄일 수 있었다.",
                ],
            },
            {
                "title": "정보처리기능사 노트: 오답을 분류하면 점수가 안정된다",
                "category": "Certification",
                "keywords": ["오답 분류", "교착상태 4조건", "OSI", "PK/FK", "정렬 시간복잡도", "회독 전략"],
                "examples": [
                    "틀린 문제를 개념/용어/실수/해석으로 나눠서 같은 유형만 반복한다",
                    "계층 문제는 MAC/IP/Port 키워드로 빠르게 매칭한다",
                ],
                "reflections": [
                    "기출은 ‘많이’보다 ‘다시 안 틀리기’가 훨씬 중요했다.",
                    "틀린 이유를 한 문장으로 정리하는 습관이 실력의 핵심이라고 느꼈다.",
                ],
            },
        ]

        self.stdout.write("Creating notes...")
        for i, spec in enumerate(notes):
            n = Note.objects.create(
                title=spec["title"],
                content=render_note(spec),
            )
            n.categories.set([categories[spec["category"]]])
            Note.objects.filter(pk=n.pk).update(
                created_at=now - timedelta(days=20 - i, minutes=19 * i),
                updated_at=now - timedelta(days=20 - i, minutes=19 * i),
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. posts={Post.objects.count()} notes={Note.objects.count()} categories={Category.objects.count()}"
            )
        )
