// Blue-X UI translations. Arrays interleave static text with dynamic values.
const UI_MESSAGES = {
  "m001": {
    "ko": [
      "참여자 개요"
    ],
    "en": [
      "Participant overview"
    ]
  },
  "m002": {
    "ko": [
      "자격증명"
    ],
    "en": [
      "Credentials"
    ]
  },
  "m003": {
    "ko": [
      "내 제공 서비스"
    ],
    "en": [
      "My services"
    ]
  },
  "m004": {
    "ko": [
      "서비스 이용"
    ],
    "en": [
      "Use services"
    ]
  },
  "m005": {
    "ko": [
      "활동 로그"
    ],
    "en": [
      "Activity log"
    ]
  },
  "m006": {
    "ko": [
      "운영 관리"
    ],
    "en": [
      "Administration"
    ]
  },
  "m007": {
    "ko": [
      "통과"
    ],
    "en": [
      "Pass"
    ]
  },
  "m008": {
    "ko": [
      "실패"
    ],
    "en": [
      "Fail"
    ]
  },
  "m009": {
    "ko": [
      "확인 불가"
    ],
    "en": [
      "Unverifiable"
    ]
  },
  "m010": {
    "ko": [
      "주의"
    ],
    "en": [
      "Warning"
    ]
  },
  "m011": {
    "ko": [
      "해당 없음"
    ],
    "en": [
      "Not applicable"
    ]
  },
  "m012": {
    "ko": [
      "미실행"
    ],
    "en": [
      "Not run"
    ]
  },
  "m013": {
    "ko": [
      "가입 완료. VC를 등록해보세요."
    ],
    "en": [
      "Account created. Add your credentials to get started."
    ]
  },
  "m014": {
    "ko": [
      "로그인했습니다."
    ],
    "en": [
      "Signed in successfully."
    ]
  },
  "m015": {
    "ko": [
      "<div class=\"section-heading\"><h2>내가 제공하는 서비스</h2><small>전체 ",
      "개 · 제공 중 ",
      "개</small></div><div class=\"service-grid\">",
      "</div>",
      "<details class=\"card service-form\" ",
      "><summary>새 서비스 등록</summary>",
      "</details><section class=\"card\"><div class=\"row between\"><h2>내 서비스를 이용하는 참여자</h2><small>",
      "개 계약 기록</small></div>",
      "</section>"
    ],
    "en": [
      "<div class=\"section-heading\"><h2>Services I provide</h2><small>Total ",
      " services · Available:  ",
      " items</small></div><div class=\"service-grid\">",
      "</div>",
      "<details class=\"card service-form\" ",
      "><summary>Register a new service</summary>",
      "</details><section class=\"card\"><div class=\"row between\"><h2>Participants using my services</h2><small>",
      " contract records</small></div>",
      "</section>"
    ]
  },
  "m016": {
    "ko": [
      "<section class=\"card service-card\"><div class=\"row between\"><span class=\"service-type\">",
      "</span>",
      "</div><h2>",
      "</h2><p class=\"muted\">제공자 ",
      "</p><div class=\"service-meta\"><span>허용 국가 <b>",
      "</b></span><span>이용 계약 ",
      "건</span></div>",
      "<details><summary>서비스 설정 보기</summary><p><small>원본 API 주소</small><br><code>",
      "</code></p>",
      "</details></section>"
    ],
    "en": [
      "<section class=\"card service-card\"><div class=\"row between\"><span class=\"service-type\">",
      "</span>",
      "</div><h2>",
      "</h2><p class=\"muted\">Provider ",
      "</p><div class=\"service-meta\"><span>Allowed country <b>",
      "</b></span><span>Access contracts ",
      " records</span></div>",
      "<details><summary>View service settings</summary><p><small>Source API URL</small><br><code>",
      "</code></p>",
      "</details></section>"
    ]
  },
  "m017": {
    "ko": [
      "제공 중"
    ],
    "en": [
      "Available"
    ]
  },
  "m018": {
    "ko": [
      "제공 중지"
    ],
    "en": [
      "Suspended"
    ]
  },
  "m019": {
    "ko": [
      "서비스 삭제"
    ],
    "en": [
      "Delete service"
    ]
  },
  "m020": {
    "ko": [
      "<section class=\"card empty\"><h3>첫 서비스를 등록해보세요</h3><p>다른 참여자가 계약하고 이용할 데이터 서비스를 제공할 수 있습니다.</p></section>"
    ],
    "en": [
      "<section class=\"card empty\"><h3>Register your first service</h3><p>Publish a data service that other participants can contract and use.</p></section>"
    ]
  },
  "m021": {
    "ko": [
      "<p class=\"muted\">제공 조직 <b>",
      "</b></p><label for=\"svcname\">서비스 이름</label><input id=\"svcname\" placeholder=\"예: 해양 기상 데이터\" maxlength=\"200\"><label for=\"svcurl\">API base URL</label><input id=\"svcurl\" class=\"key\" value=\"demo://weather\"><small>고정 샘플은 demo://weather, 실제 API는 데이터 경로 앞의 기본 주소를 입력하세요.</small><label for=\"svccountry\">이용을 허용할 국가</label><input id=\"svccountry\" value=\"",
      "\" maxlength=\"2\" placeholder=\"KR\"><small>국가 코드 두 자리 · 예: KR</small><details><summary>등록 가능한 외부 API</summary><p class=\"muted\">운영자가 허용한 주소에 서비스를 등록할 수 있습니다.</p>",
      "</details><div class=\"row\" style=\"margin-top:20px\">",
      "</div><p class=\"muted\">등록에 사용한 VC가 삭제·만료되거나 검증에 실패하면 제공이 중지됩니다. 참여 세션의 종료만으로는 중지되지 않습니다.</p>"
    ],
    "en": [
      "<p class=\"muted\">Provider organization <b>",
      "</b></p><label for=\"svcname\">Service name</label><input id=\"svcname\" placeholder=\"e.g. Ocean weather data\" maxlength=\"200\"><label for=\"svcurl\">API base URL</label><input id=\"svcurl\" class=\"key\" value=\"demo://weather\"><small>Use demo://weather for the fixed sample, or enter the base URL preceding the data path for a real API.</small><label for=\"svccountry\">Allowed consumer country</label><input id=\"svccountry\" value=\"",
      "\" maxlength=\"2\" placeholder=\"KR\"><small>Two-letter country code · e.g. KR</small><details><summary>Available external API origins</summary><p class=\"muted\">Services can use API addresses allowed by an operator.</p>",
      "</details><div class=\"row\" style=\"margin-top:20px\">",
      "</div><p class=\"muted\">Service delivery is suspended if its credential is deleted, expires or fails verification. Ending the participant session alone does not suspend delivery.</p>"
    ]
  },
  "m022": {
    "ko": [
      "<p class=\"muted\">허용된 외부 API가 없습니다. 운영자에게 등록을 요청하세요.</p>"
    ],
    "en": [
      "<p class=\"muted\">No external APIs are allowed yet. Ask an operator to register one.</p>"
    ]
  },
  "m023": {
    "ko": [
      "서비스 등록"
    ],
    "en": [
      "Register service"
    ]
  },
  "m024": {
    "ko": [
      "<p class=\"muted\">자격증명을 검증하고 참여 세션을 연결하면 서비스를 등록할 수 있습니다.</p>",
      ""
    ],
    "en": [
      "<p class=\"muted\">Verify credentials and connect a participant session to register a service.</p>",
      ""
    ]
  },
  "m025": {
    "ko": [
      "자격증명으로 이동"
    ],
    "en": [
      "Go to credentials"
    ]
  },
  "m026": {
    "ko": [
      "<div class=\"scroll\"><table><thead><tr><th>서비스</th><th>이용 참여자</th><th>상태</th><th>만료</th></tr></thead><tbody>",
      "</tbody></table></div>"
    ],
    "en": [
      "<div class=\"scroll\"><table><thead><tr><th>Service</th><th>Consumer</th><th>Status</th><th>Expiry</th></tr></thead><tbody>",
      "</tbody></table></div>"
    ]
  },
  "m027": {
    "ko": [
      "이름 없음"
    ],
    "en": [
      "Unnamed"
    ]
  },
  "m028": {
    "ko": [
      "활성"
    ],
    "en": [
      "Active"
    ]
  },
  "m029": {
    "ko": [
      "만료"
    ],
    "en": [
      "Expiry"
    ]
  },
  "m030": {
    "ko": [
      "<p class=\"empty\">아직 계약한 참여자가 없습니다.</p>"
    ],
    "en": [
      "<p class=\"empty\">No participants have established a contract yet.</p>"
    ]
  },
  "m031": {
    "ko": [
      "<section class=\"card log-card\"><div class=\"row between\"><div><h2>활동 및 검증 로그</h2><small>총 ",
      "건 · 최근 작업부터 표시 · 초기화 후에도 보존</small></div><div class=\"row\"><select id=\"logfilter\" aria-label=\"결과 필터\"><option value=\"\">모든 결과</option><option value=\"pass\">성공 / 통과</option><option value=\"fail\">실패</option></select>",
      "</div></div>",
      "<div class=\"row\" style=\"margin-top:15px\">",
      "",
      "</div></section>"
    ],
    "en": [
      "<section class=\"card log-card\"><div class=\"row between\"><div><h2>Activity & verification log</h2><small>Total ",
      " entries · Newest first · Retained after reset</small></div><div class=\"row\"><select id=\"logfilter\" aria-label=\"Result filter\"><option value=\"\">All results</option><option value=\"pass\">Success / pass</option><option value=\"fail\">Fail</option></select>",
      "</div></div>",
      "<div class=\"row\" style=\"margin-top:15px\">",
      "",
      "</div></section>"
    ]
  },
  "m032": {
    "ko": [
      "> 전체 계정</label>"
    ],
    "en": [
      "> All accounts</label>"
    ]
  },
  "m033": {
    "ko": [
      "<details><summary><span class=\"row\">",
      "<small>",
      "</small><b>",
      "</b><span class=\"muted\">",
      " · ",
      "ms</span></span></summary><p><b>작업</b> ",
      " · HTTP ",
      " · <b>실행자</b> ",
      "</p><small>작업 ID ",
      "</small>",
      "",
      "",
      "",
      "</details>"
    ],
    "en": [
      "<details><summary><span class=\"row\">",
      "<small>",
      "</small><b>",
      "</b><span class=\"muted\">",
      " · ",
      "ms</span></span></summary><p><b>Operation</b> ",
      " · HTTP ",
      " · <b>Actor</b> ",
      "</p><small>Operation ID ",
      "</small>",
      "",
      "",
      "",
      "</details>"
    ]
  },
  "m034": {
    "ko": [
      "미인증"
    ],
    "en": [
      "Unauthenticated"
    ]
  },
  "m035": {
    "ko": [
      "접속 키 / 미인증"
    ],
    "en": [
      "Access key / unauthenticated"
    ]
  },
  "m036": {
    "ko": [
      "<p><b>upstream 경로</b> <code>"
    ],
    "en": [
      "<p><b>Upstream path</b> <code>"
    ]
  },
  "m037": {
    "ko": [
      "<details><summary>presigned URL 발급 객체 "
    ],
    "en": [
      "<details><summary>Objects with presigned URLs:  "
    ]
  },
  "m038": {
    "ko": [
      "건"
    ],
    "en": [
      " records"
    ]
  },
  "m039": {
    "ko": [
      " · 만료 "
    ],
    "en": [
      " · Expiry "
    ]
  },
  "m040": {
    "ko": [
      "초"
    ],
    "en": [
      " seconds"
    ]
  },
  "m041": {
    "ko": [
      " · 일부만 기록"
    ],
    "en": [
      " · Partial record"
    ]
  },
  "m042": {
    "ko": [
      "<p class=\"empty\">기록된 작업이 없습니다.</p>"
    ],
    "en": [
      "<p class=\"empty\">No activity recorded yet.</p>"
    ]
  },
  "m043": {
    "ko": [
      "이전"
    ],
    "en": [
      "Previous"
    ]
  },
  "m044": {
    "ko": [
      "다음"
    ],
    "en": [
      "Next"
    ]
  },
  "m045": {
    "ko": [
      "<section class=\"card\"><h2>참여자 계정 관리</h2><p class=\"muted\">운영자는 참여자 역할과 별개인 플랫폼 관리 권한입니다. 대상 계정의 콘솔을 열어 VC·세션·계약·제공 서비스·접속 키를 관리합니다. 운영자 권한 부여·해제는 서버의 manage_admin.py로만 합니다.</p><table><thead><tr><th>계정</th><th>권한</th><th>가입 시각</th><th>관리</th></tr></thead><tbody>",
      "</tbody></table></section><section class=\"card\"><h2>데이터 API origin 허용 목록</h2><p class=\"muted\">참여자가 서비스에 등록하는 외부 API 주소는 이 목록의 origin(scheme://host[:port])과 일치해야 합니다. 추가·해제는 즉시 반영되며 재배포가 필요 없습니다. 해제하면 해당 origin을 쓰는 서비스는 곧바로 제공 중지됩니다. 각 origin 아래에는 포털이 호출할 수 있는 데이터 경로를 origin 기준 전체 경로(예: /api/griddata)로 등록하며, 정확히 일치하는 경로만 허용합니다. ping은 포털 내부 기능이라 등록하지 않습니다.</p><label for=\"originval\">origin</label><input id=\"originval\" class=\"key\" placeholder=\"https://weather-api.example.com\"><label for=\"originnote\">메모 (선택)</label><input id=\"originnote\" maxlength=\"200\" placeholder=\"예: Carol Co 격자 API\"><div class=\"row\" style=\"margin-top:14px\">",
      "</div><div class=\"scroll\" style=\"margin-top:18px\"><table><thead><tr><th>origin</th><th>출처</th><th>메모</th><th>등록</th><th>사용 서비스</th><th></th></tr></thead><tbody>",
      "</tbody></table></div><p class=\"muted\">사설·루프백·메타데이터 등 내부 주소는 콘솔에서 허용할 수 없습니다. 운영 중 신뢰하는 기준선은 서버 환경변수로 두는 것을 권장합니다.</p></section><section class=\"card\"><h2>플랫폼 샘플 서비스</h2><p class=\"muted\">참여자 VC 없이 연결 테스트용으로만 쓰는 고정 샘플(demo://weather)입니다. 실제 API는 VC를 연결한 참여자 계정의 서비스 제공 메뉴에서 등록합니다.</p><label for=\"svcname\">서비스 이름</label><input id=\"svcname\" value=\"Weather Demo\"><label for=\"svccountry\">허용 국가 (두 자리)</label><input id=\"svccountry\" value=\"KR\" maxlength=\"2\"><div class=\"row\" style=\"margin-top:14px\">",
      "</div></section><section class=\"card\"><h2>전체 서비스</h2>",
      "<p class=\"muted\">PoC 정책 변경은 서비스 삭제 후 재등록으로 진행합니다. 삭제 시 관련 계약도 해제됩니다.</p></section>"
    ],
    "en": [
      "<section class=\"card\"><h2>Participant accounts</h2><p class=\"muted\">Operators manage the platform independently of participant roles. Open an account console to manage credentials, sessions, contracts, services and access keys. Operator privileges can only be changed on the server using manage_admin.py.</p><table><thead><tr><th>Account</th><th>Privileges</th><th>Created</th><th>Manage</th></tr></thead><tbody>",
      "</tbody></table></section><section class=\"card\"><h2>Allowed data API origins</h2><p class=\"muted\">External APIs must use an allowed origin (scheme://host[:port]). Changes take effect immediately. Removing an origin suspends its services. Register each permitted path under its origin (for example, /api/griddata); paths must match exactly. The internal ping endpoint does not need registration.</p><label for=\"originval\">origin</label><input id=\"originval\" class=\"key\" placeholder=\"https://weather-api.example.com\"><label for=\"originnote\">Note (optional)</label><input id=\"originnote\" maxlength=\"200\" placeholder=\"e.g. Carol Co grid API\"><div class=\"row\" style=\"margin-top:14px\">",
      "</div><div class=\"scroll\" style=\"margin-top:18px\"><table><thead><tr><th>origin</th><th>Source</th><th>Note</th><th>Registered</th><th>Services using origin</th><th></th></tr></thead><tbody>",
      "</tbody></table></div><p class=\"muted\">Private, loopback and metadata addresses cannot be allowed through this console. Use server environment variables for trusted baseline settings.</p></section><section class=\"card\"><h2>Platform sample service</h2><p class=\"muted\">A fixed sample (demo://weather) for connectivity tests without participant credentials. To register a real API, connect a participant session and use My services.</p><label for=\"svcname\">Service name</label><input id=\"svcname\" value=\"Weather Demo\"><label for=\"svccountry\">Allowed country (two letters)</label><input id=\"svccountry\" value=\"KR\" maxlength=\"2\"><div class=\"row\" style=\"margin-top:14px\">",
      "</div></section><section class=\"card\"><h2>All services</h2>",
      "<p class=\"muted\">To change a policy in this PoC, delete and register the service again. Deletion also ends related contracts.</p></section>"
    ]
  },
  "m046": {
    "ko": [
      "운영자"
    ],
    "en": [
      "Operator"
    ]
  },
  "m047": {
    "ko": [
      "참여자"
    ],
    "en": [
      "Participant"
    ]
  },
  "m048": {
    "ko": [
      "콘솔 열기"
    ],
    "en": [
      "Open console"
    ]
  },
  "m049": {
    "ko": [
      "허용 추가"
    ],
    "en": [
      "Allow origin"
    ]
  },
  "m050": {
    "ko": [
      "<tr><td><code>",
      "</code></td><td>",
      "</td><td>",
      "</td><td>",
      "</td><td>",
      "</td><td>",
      "</td></tr><tr class=\"pathrow\"><td colspan=\"6\"><small class=\"muted\">허용 데이터 경로 ",
      "개</small><div class=\"pathlist\">",
      "</div><div class=\"pathadd\"><input id=\"pathval-",
      "\" class=\"key\" placeholder=\"/api/gridfile\" aria-label=\"경로\"><input id=\"pathnote-",
      "\" maxlength=\"200\" placeholder=\"메모 (선택)\" aria-label=\"경로 메모\" style=\"flex:0 1 200px\">",
      "</div></td></tr>"
    ],
    "en": [
      "<tr><td><code>",
      "</code></td><td>",
      "</td><td>",
      "</td><td>",
      "</td><td>",
      "</td><td>",
      "</td></tr><tr class=\"pathrow\"><td colspan=\"6\"><small class=\"muted\">Allowed data paths ",
      " items</small><div class=\"pathlist\">",
      "</div><div class=\"pathadd\"><input id=\"pathval-",
      "\" class=\"key\" placeholder=\"/api/gridfile\" aria-label=\"Path\"><input id=\"pathnote-",
      "\" maxlength=\"200\" placeholder=\"Note (optional)\" aria-label=\"Path note\" style=\"flex:0 1 200px\">",
      "</div></td></tr>"
    ]
  },
  "m051": {
    "ko": [
      "서버 설정"
    ],
    "en": [
      "Server configuration"
    ]
  },
  "m052": {
    "ko": [
      "콘솔"
    ],
    "en": [
      "Console"
    ]
  },
  "m053": {
    "ko": [
      "허용 해제"
    ],
    "en": [
      "Remove permission"
    ]
  },
  "m054": {
    "ko": [
      "<small class=\"muted\">서버에서만 변경</small>"
    ],
    "en": [
      "<small class=\"muted\">Change on server only</small>"
    ]
  },
  "m055": {
    "ko": [
      "서버 설정"
    ],
    "en": [
      "Server configuration"
    ]
  },
  "m056": {
    "ko": [
      "해제"
    ],
    "en": [
      "Remove"
    ]
  },
  "m057": {
    "ko": [
      "<small class=\"muted\">등록된 경로가 없어 이 origin의 서비스는 ping만 가능합니다.</small>"
    ],
    "en": [
      "<small class=\"muted\">No paths are registered. Only ping is available for this origin.</small>"
    ]
  },
  "m058": {
    "ko": [
      "경로 추가"
    ],
    "en": [
      "Add path"
    ]
  },
  "m059": {
    "ko": [
      "<tr><td colspan=\"6\" class=\"empty\">허용된 origin이 없습니다.</td></tr>"
    ],
    "en": [
      "<tr><td colspan=\"6\" class=\"empty\">No origins have been allowed yet.</td></tr>"
    ]
  },
  "m060": {
    "ko": [
      "샘플 서비스 등록"
    ],
    "en": [
      "Register sample service"
    ]
  },
  "m061": {
    "ko": [
      "<div class=\"row between\" style=\"margin:14px 0\"><span><b>",
      "</b> ",
      " · ",
      "<br><small>제공자 ",
      "",
      " · ",
      "</small></span>",
      "</div>"
    ],
    "en": [
      "<div class=\"row between\" style=\"margin:14px 0\"><span><b>",
      "</b> ",
      " · ",
      "<br><small>Provider ",
      "",
      " · ",
      "</small></span>",
      "</div>"
    ]
  },
  "m062": {
    "ko": [
      "제공 중"
    ],
    "en": [
      "Available"
    ]
  },
  "m063": {
    "ko": [
      "제공 중지"
    ],
    "en": [
      "Suspended"
    ]
  },
  "m064": {
    "ko": [
      "서비스 삭제"
    ],
    "en": [
      "Delete service"
    ]
  },
  "m065": {
    "ko": [
      "<p class=\"muted\">서비스 없음</p>"
    ],
    "en": [
      "<p class=\"muted\">No services</p>"
    ]
  },
  "m066": {
    "ko": [
      "파일을 선택해주세요"
    ],
    "en": [
      "Select a file first."
    ]
  },
  "m067": {
    "ko": [
      "VC 검증 통과. 세션을 연결해보세요."
    ],
    "en": [
      "Credential verification passed. Connect a participant session next."
    ]
  },
  "m068": {
    "ko": [
      "검증이 완료되었습니다. 실패·확인 불가 항목을 확인하세요."
    ],
    "en": [
      "Verification completed. Review failed and unverifiable checks."
    ]
  },
  "m069": {
    "ko": [
      "접속 주소를 복사했습니다."
    ],
    "en": [
      "Access URL copied."
    ]
  },
  "m070": {
    "ko": [
      "주소를 선택했습니다. Ctrl+C로 복사하세요."
    ],
    "en": [
      "URL selected. Press Ctrl+C to copy it."
    ]
  },
  "m071": {
    "ko": [
      "먼저 세션을 연결해주세요"
    ],
    "en": [
      "Connect a participant session first."
    ]
  },
  "m072": {
    "ko": [
      "허용된 데이터 경로가 없습니다"
    ],
    "en": [
      "No data paths are allowed."
    ]
  },
  "m073": {
    "ko": [
      "쿼리 칸에는 경로 없이 key=value만 입력하세요. 경로는 위 목록에서 선택합니다"
    ],
    "en": [
      "Enter key=value parameters only. Select the path from the list above."
    ]
  },
  "m074": {
    "ko": [
      "요청 성공. 활동 로그에서 결과를 확인할 수 있습니다."
    ],
    "en": [
      "Request succeeded. Details are available in the activity log."
    ]
  },
  "m075": {
    "ko": [
      "서비스 이름을 입력해주세요"
    ],
    "en": [
      "Enter a service name."
    ]
  },
  "m076": {
    "ko": [
      "국가 코드는 KR처럼 영문 두 자리로 입력해주세요"
    ],
    "en": [
      "Enter a two-letter country code, such as KR."
    ]
  },
  "m077": {
    "ko": [
      "서비스를 등록했습니다. 다른 참여자의 카탈로그에 표시됩니다."
    ],
    "en": [
      "Service registered. Other participants can now find it in the catalog."
    ]
  },
  "m078": {
    "ko": [
      " 을(를) 허용했습니다."
    ],
    "en": [
      " has been allowed."
    ]
  },
  "m079": {
    "ko": [
      " 경로를 허용했습니다."
    ],
    "en": [
      " Path allowed."
    ]
  },
  "m080": {
    "ko": [
      " 경로 허용을 해제할까요? 이 경로 호출은 즉시 차단됩니다."
    ],
    "en": [
      " Remove this allowed path? Requests to this path will be blocked immediately."
    ]
  },
  "m081": {
    "ko": [
      " 경로 허용을 해제했습니다."
    ],
    "en": [
      " Path permission removed."
    ]
  },
  "m082": {
    "ko": [
      " 허용을 해제할까요? 이 origin을 쓰는 서비스는 즉시 제공 중지되고, 콘솔에서 등록한 하위 경로도 함께 삭제됩니다."
    ],
    "en": [
      " Remove this allowed origin? Its services will be suspended immediately, and paths registered through the console will also be removed."
    ]
  },
  "m083": {
    "ko": [
      " 허용을 해제했습니다."
    ],
    "en": [
      " Permission removed."
    ]
  },
  "m084": {
    "ko": [
      "플랫폼 샘플 서비스를 등록했습니다."
    ],
    "en": [
      "Platform sample service registered."
    ]
  },
  "m085": {
    "ko": [
      " 서비스를 계약할까요?\n제공자: "
    ],
    "en": [
      " Establish a contract for this service?\nProvider: "
    ]
  },
  "m086": {
    "ko": [
      " · 허용 국가: "
    ],
    "en": [
      " · Allowed country: "
    ]
  },
  "m087": {
    "ko": [
      "\n계약은 현재 참여 세션 및 자격증명의 유효기간 내에서 유지됩니다."
    ],
    "en": [
      "\nThe contract is valid only within the lifetime of the current session and credentials."
    ]
  },
  "m088": {
    "ko": [
      "세션과 계약을 초기화할까요? VC, 주소, 로그는 유지됩니다."
    ],
    "en": [
      "Reset the session and contracts? Credentials, access URLs and logs will be retained."
    ]
  },
  "m089": {
    "ko": [
      "VC를 삭제할까요? 연결된 세션과 계약이 해제되고, 이 VC로 제공 중인 서비스는 제공 중지됩니다."
    ],
    "en": [
      "Delete this credential set? Linked sessions and contracts will end, and services using it will be suspended."
    ]
  },
  "m090": {
    "ko": [
      "접속 키를 재발급할까요? 기존 Web-ECDIS 주소는 사용할 수 없게 됩니다."
    ],
    "en": [
      "Rotate the access key? Existing Web-ECDIS URLs will stop working."
    ]
  },
  "m091": {
    "ko": [
      "서비스와 관련 계약을 삭제할까요?"
    ],
    "en": [
      "Delete this service and its related contracts?"
    ]
  },
  "m092": {
    "ko": [
      "세션을 연결할까요? 기존 세션과 계약은 초기화되며 서비스 계약을 다시 해야 합니다."
    ],
    "en": [
      "Connect this session? Existing sessions and contracts will be reset. You will need to establish service contracts again."
    ]
  },
  "m093": {
    "ko": [
      "작업 완료. 상세 결과는 활동 및 검증 로그에서 확인하세요."
    ],
    "en": [
      "Completed. Open the activity log for detailed results."
    ]
  },
  "m094": {
    "ko": [
      "조직의 자격증명과 서비스 활동을 한눈에 확인하세요."
    ],
    "en": [
      "Your organization's credentials and service activity at a glance."
    ]
  },
  "m095": {
    "ko": [
      "자격증명을 검증하고 참여 세션에 연결하세요."
    ],
    "en": [
      "Verify credentials and connect your participant session."
    ]
  },
  "m096": {
    "ko": [
      "내 데이터를 서비스로 제공하고 이용 현황을 확인하세요."
    ],
    "en": [
      "Publish your data services and monitor their use."
    ]
  },
  "m097": {
    "ko": [
      "서비스를 찾아 계약하고 데이터에 연결하세요."
    ],
    "en": [
      "Discover services, establish contracts and connect to data."
    ]
  },
  "m098": {
    "ko": [
      "검증부터 데이터 요청까지, 모든 작업의 과정을 확인하세요."
    ],
    "en": [
      "Trace every operation, from verification to data requests."
    ]
  },
  "m099": {
    "ko": [
      "참여자와 데이터 API 접근 범위를 관리하세요."
    ],
    "en": [
      "Manage participants and permitted data API access."
    ]
  },
  "m100": {
    "ko": [
      "",
      "시간 ",
      "분"
    ],
    "en": [
      "",
      " hours ",
      " minutes"
    ]
  },
  "m101": {
    "ko": [
      "",
      "분"
    ],
    "en": [
      "",
      " minutes"
    ]
  },
  "m102": {
    "ko": [
      "자격증명에서 시작하는 신뢰 기반 데이터 연결"
    ],
    "en": [
      "Trusted data access starts with verifiable credentials."
    ]
  },
  "m103": {
    "ko": [
      "<div class=\"auth-layout\"><section class=\"auth-story\"><div class=\"eyebrow\">TRUSTED DATA TRANSACTIONS</div><h2>신뢰를 확인하고,<br>데이터를 연결하세요.</h2><p class=\"muted\">Blue-X에서 조직의 자격증명을 검증하고 서비스를 제공하거나 이용하세요.</p><div class=\"steps\"><div class=\"step\"><i>1</i><b>자격증명 등록 및 검증</b></div><div class=\"step\"><i>2</i><b>참여 세션 연결</b></div><div class=\"step\"><i>3</i><b>서비스 제공 · 계약 · 데이터 이용</b></div></div></section><section class=\"card auth\"><div class=\"eyebrow\">PARTICIPANT CONSOLE</div><h2 style=\"margin-top:16px;font-size:24px\">",
      "</h2><p class=\"muted\">",
      "</p><form id=\"authform\"><label for=\"username\">아이디</label><input id=\"username\" autocomplete=\"username\" placeholder=\"3–32자 아이디\" required minlength=\"3\" maxlength=\"32\"><label for=\"password\">비밀번호</label><input id=\"password\" type=\"password\" autocomplete=\"",
      "\" placeholder=\"8자 이상\" required minlength=\"8\" maxlength=\"128\"><div class=\"row\" style=\"margin-top:24px\"><button class=\"primary\" type=\"submit\">",
      "</button></div></form><p class=\"auth-note muted\">",
      " <button class=\"auth-switch\" data-action=\"toggle-auth\">",
      "</button></p><small>서비스 제공·이용은 로그인 후 VC 검증과 참여 세션 연결을 거쳐 진행합니다.</small></section></div>"
    ],
    "en": [
      "<div class=\"auth-layout\"><section class=\"auth-story\"><div class=\"eyebrow\">TRUSTED DATA TRANSACTIONS</div><h2>Verify trust.<br>Connect to data.</h2><p class=\"muted\">Verify your organization's credentials, then provide or use data services with Blue-X.</p><div class=\"steps\"><div class=\"step\"><i>1</i><b>Register and verify credentials</b></div><div class=\"step\"><i>2</i><b>Connect participant session</b></div><div class=\"step\"><i>3</i><b>Provide services · Contract · Access data</b></div></div></section><section class=\"card auth\"><div class=\"eyebrow\">PARTICIPANT CONSOLE</div><h2 style=\"margin-top:16px;font-size:24px\">",
      "</h2><p class=\"muted\">",
      "</p><form id=\"authform\"><label for=\"username\">Username</label><input id=\"username\" autocomplete=\"username\" placeholder=\"Username (3–32 characters)\" required minlength=\"3\" maxlength=\"32\"><label for=\"password\">Password</label><input id=\"password\" type=\"password\" autocomplete=\"",
      "\" placeholder=\"At least 8 characters\" required minlength=\"8\" maxlength=\"128\"><div class=\"row\" style=\"margin-top:24px\"><button class=\"primary\" type=\"submit\">",
      "</button></div></form><p class=\"auth-note muted\">",
      " <button class=\"auth-switch\" data-action=\"toggle-auth\">",
      "</button></p><small>After signing in, verify credentials and connect a participant session to provide or use services.</small></section></div>"
    ]
  },
  "m104": {
    "ko": [
      "참여자 계정 만들기"
    ],
    "en": [
      "Create a participant account"
    ]
  },
  "m105": {
    "ko": [
      "로그인"
    ],
    "en": [
      "Sign in"
    ]
  },
  "m106": {
    "ko": [
      "하나의 계정으로 서비스를 제공하고 이용할 수 있어요."
    ],
    "en": [
      "Use one account to both provide and consume services."
    ]
  },
  "m107": {
    "ko": [
      "계정에 로그인해 참여자 공간을 열어보세요."
    ],
    "en": [
      "Sign in to open your participant workspace."
    ]
  },
  "m108": {
    "ko": [
      "계정 만들기"
    ],
    "en": [
      "Create account"
    ]
  },
  "m109": {
    "ko": [
      "로그인"
    ],
    "en": [
      "Sign in"
    ]
  },
  "m110": {
    "ko": [
      "이미 계정이 있나요?"
    ],
    "en": [
      "Already have an account?"
    ]
  },
  "m111": {
    "ko": [
      "처음 방문하셨나요?"
    ],
    "en": [
      "New to Blue-X?"
    ]
  },
  "m112": {
    "ko": [
      "로그인"
    ],
    "en": [
      "Sign in"
    ]
  },
  "m113": {
    "ko": [
      "회원가입"
    ],
    "en": [
      "Sign up"
    ]
  },
  "m114": {
    "ko": [
      "운영자"
    ],
    "en": [
      "Operator"
    ]
  },
  "m115": {
    "ko": [
      "세션 연결됨"
    ],
    "en": [
      "Session connected"
    ]
  },
  "m116": {
    "ko": [
      "미연결"
    ],
    "en": [
      "Not connected"
    ]
  },
  "m117": {
    "ko": [
      "새로고침"
    ],
    "en": [
      "Refresh"
    ]
  },
  "m118": {
    "ko": [
      "로그아웃"
    ],
    "en": [
      "Sign out"
    ]
  },
  "m119": {
    "ko": [
      "<div class=\"scope row between\"><span>운영자 작업 중 · 관리 대상 계정 <b>",
      "</b></span>",
      "</div>"
    ],
    "en": [
      "<div class=\"scope row between\"><span>Operator mode · Managing account <b>",
      "</b></span>",
      "</div>"
    ]
  },
  "m120": {
    "ko": [
      "내 계정으로 돌아가기"
    ],
    "en": [
      "Back to my account"
    ]
  },
  "m121": {
    "ko": [
      "<section class=\"card empty\" role=\"status\">불러오는 중…</section>"
    ],
    "en": [
      "<section class=\"card empty\" role=\"status\">Loading…</section>"
    ]
  },
  "m122": {
    "ko": [
      "<section class=\"card empty\">불러오지 못했습니다. 새로고침으로 다시 시도하세요.</section>"
    ],
    "en": [
      "<section class=\"card empty\">Could not load this page. Select Refresh to try again.</section>"
    ]
  },
  "m123": {
    "ko": [
      "자격증명을 등록·확인하세요"
    ],
    "en": [
      "Add or review your credentials."
    ]
  },
  "m124": {
    "ko": [
      "참여 세션을 연결하세요"
    ],
    "en": [
      "Connect your participant session."
    ]
  },
  "m125": {
    "ko": [
      "데이터 서비스를 이용할 준비가 됐어요"
    ],
    "en": [
      "You're ready to explore data services."
    ]
  },
  "m126": {
    "ko": [
      "<section class=\"hero\"><div class=\"row between\"><div><div class=\"eyebrow\">YOUR PARTICIPANT</div><h2>",
      " ",
      "</h2><span class=\"muted\">",
      "</span></div>",
      "</div><div class=\"hero-meta\"><div><small>로그인 계정</small><b>",
      "</b></div><div><small>참여 세션</small><b>",
      "</b></div><div><small>",
      "</small><b>",
      "</b></div></div>",
      "</section><div class=\"steps\"><div class=\"step ",
      "\"><i>",
      "</i><div><b>자격증명 검증</b><small>",
      "</small></div></div><div class=\"step ",
      "\"><i>",
      "</i><div><b>참여 세션 연결</b><small>",
      "</small></div></div><div class=\"step ",
      "\"><i>3</i><div><b>서비스 제공 · 이용</b><small>서비스 등록 또는 계약 후 요청</small></div></div></div><div class=\"section-heading\"><h2>나의 활동</h2><small>제공과 이용을 함께 할 수 있습니다</small></div><div class=\"grid\"><section class=\"card\"><h3>등록된 자격증명 세트</h3><div class=\"stat-number\">",
      "<small style=\"font-size:13px\"> 세트</small></div><small>검증 결과와 연결 상태 확인</small><div class=\"stat-footer\">",
      "</div></section><section class=\"card\"><h3>내 제공 서비스</h3><div class=\"stat-number\">",
      "<small style=\"font-size:13px\"> 개</small></div><small>제공 중 ",
      "개 · 이용 계약 ",
      "건</small><div class=\"stat-footer\">",
      "</div></section><section class=\"card\"><h3>내 이용 계약</h3><div class=\"stat-number\">",
      "<small style=\"font-size:13px\"> 건</small></div><small>유효기간 내 계약 · 요청 시 권한 재확인</small><div class=\"stat-footer\">",
      "</div></section></div><section class=\"card subtle-card row between\"><div><h3>작업이 어디까지 진행됐나요?</h3><small>검증 단계, 연결 결과, 데이터 요청 기록을 활동 로그에서 확인하세요.</small></div>",
      "</section><details class=\"card advanced\"><summary>연결 및 접속 키 관리</summary><div class=\"two-col\"><div><h3>참여 세션 종료</h3><p class=\"muted\">현재 세션과 이용 계약을 해제합니다. 자격증명·제공 서비스·접속 주소·로그는 유지됩니다.</p>",
      "</div><div><h3>접속 키 재발급</h3><p class=\"muted\">",
      " 재발급하면 이전 접속 주소는 사용할 수 없습니다.</p>",
      "</div></div></details>"
    ],
    "en": [
      "<section class=\"hero\"><div class=\"row between\"><div><div class=\"eyebrow\">YOUR PARTICIPANT</div><h2>",
      " ",
      "</h2><span class=\"muted\">",
      "</span></div>",
      "</div><div class=\"hero-meta\"><div><small>Signed-in account</small><b>",
      "</b></div><div><small>Participant session</small><b>",
      "</b></div><div><small>",
      "</small><b>",
      "</b></div></div>",
      "</section><div class=\"steps\"><div class=\"step ",
      "\"><i>",
      "</i><div><b>Verify credentials</b><small>",
      "</small></div></div><div class=\"step ",
      "\"><i>",
      "</i><div><b>Connect participant session</b><small>",
      "</small></div></div><div class=\"step ",
      "\"><i>3</i><div><b>Provide & consume</b><small>Publish a service or contract and request data</small></div></div></div><div class=\"section-heading\"><h2>My activity</h2><small>Provide and consume with one account</small></div><div class=\"grid\"><section class=\"card\"><h3>Credential sets</h3><div class=\"stat-number\">",
      "<small style=\"font-size:13px\"> sets</small></div><small>Review verification and connection status</small><div class=\"stat-footer\">",
      "</div></section><section class=\"card\"><h3>My services</h3><div class=\"stat-number\">",
      "<small style=\"font-size:13px\">  items</small></div><small>Available ",
      " services · Access contracts:  ",
      " records</small><div class=\"stat-footer\">",
      "</div></section><section class=\"card\"><h3>My contracts</h3><div class=\"stat-number\">",
      "<small style=\"font-size:13px\">  records</small></div><small>Unexpired contracts · Access rechecked on every request</small><div class=\"stat-footer\">",
      "</div></section></div><section class=\"card subtle-card row between\"><div><h3>Need to trace an operation?</h3><small>Review verification steps, connection results and data requests in the activity log.</small></div>",
      "</section><details class=\"card advanced\"><summary>Session & access key settings</summary><div class=\"two-col\"><div><h3>End participant session</h3><p class=\"muted\">Ends the current session and access contracts. Credentials, provided services, access URLs and logs are retained.</p>",
      "</div><div><h3>Rotate access key</h3><p class=\"muted\">",
      " Rotating the key invalidates previous access URLs.</p>",
      "</div></div></details>"
    ]
  },
  "m127": {
    "ko": [
      "연결된 조직 없음"
    ],
    "en": [
      "No organization connected"
    ]
  },
  "m128": {
    "ko": [
      "국가 미상"
    ],
    "en": [
      "Country unknown"
    ]
  },
  "m129": {
    "ko": [
      "서비스 둘러보기"
    ],
    "en": [
      "Explore services"
    ]
  },
  "m130": {
    "ko": [
      "세션 연결하기"
    ],
    "en": [
      "Connect session"
    ]
  },
  "m131": {
    "ko": [
      "자격증명 확인하기"
    ],
    "en": [
      "Review credentials"
    ]
  },
  "m132": {
    "ko": [
      "연결됨 · "
    ],
    "en": [
      "Connected · "
    ]
  },
  "m133": {
    "ko": [
      " 남음"
    ],
    "en": [
      " remaining"
    ]
  },
  "m134": {
    "ko": [
      "연결 전"
    ],
    "en": [
      "Not connected"
    ]
  },
  "m135": {
    "ko": [
      "세션 만료"
    ],
    "en": [
      "Session expiry"
    ]
  },
  "m136": {
    "ko": [
      "검증 상태"
    ],
    "en": [
      "Verification status"
    ]
  },
  "m137": {
    "ko": [
      "데모 연결 가능한 VC 있음"
    ],
    "en": [
      "Credentials eligible for demo access"
    ]
  },
  "m138": {
    "ko": [
      "자격증명 확인 필요"
    ],
    "en": [
      "Credentials need review"
    ]
  },
  "m139": {
    "ko": [
      "<details class=\"hero-id\"><summary>참여자 식별자 보기</summary><code>",
      "</code></details>"
    ],
    "en": [
      "<details class=\"hero-id\"><summary>View participant identifier</summary><code>",
      "</code></details>"
    ]
  },
  "m140": {
    "ko": [
      "연결 가능한 VC 확인"
    ],
    "en": [
      "Eligible credentials available"
    ]
  },
  "m141": {
    "ko": [
      "VC / VP 파일 등록"
    ],
    "en": [
      "Upload VC / VP files"
    ]
  },
  "m142": {
    "ko": [
      "조직 연결 완료"
    ],
    "en": [
      "Organization connected"
    ]
  },
  "m143": {
    "ko": [
      "검증된 자격증명으로 연결"
    ],
    "en": [
      "Connect with verified credentials"
    ]
  },
  "m144": {
    "ko": [
      "자격증명 관리 →"
    ],
    "en": [
      "Manage credentials →"
    ]
  },
  "m145": {
    "ko": [
      "제공 서비스 관리 →"
    ],
    "en": [
      "Manage my services →"
    ]
  },
  "m146": {
    "ko": [
      "계약한 서비스 보기 →"
    ],
    "en": [
      "View my contracts →"
    ]
  },
  "m147": {
    "ko": [
      "활동 로그 보기"
    ],
    "en": [
      "View activity log"
    ]
  },
  "m148": {
    "ko": [
      "세션 종료 · 초기화"
    ],
    "en": [
      "End session & reset"
    ]
  },
  "m149": {
    "ko": [
      "접속 키가 발급되어 있습니다."
    ],
    "en": [
      "An access key has been issued."
    ]
  },
  "m150": {
    "ko": [
      "첫 연결 시 접속 주소가 생성됩니다."
    ],
    "en": [
      "An access URL is created on your first connection."
    ]
  },
  "m151": {
    "ko": [
      "접속 키 재발급"
    ],
    "en": [
      "Rotate access key"
    ]
  },
  "m152": {
    "ko": [
      "<p class=\"muted\">이 작업에는 별도 검사 항목이 없습니다.</p>"
    ],
    "en": [
      "<p class=\"muted\">No separate checks were recorded for this operation.</p>"
    ]
  },
  "m153": {
    "ko": [
      "공통 검사"
    ],
    "en": [
      "Common checks"
    ]
  },
  "m154": {
    "ko": [
      "<details ",
      "><summary>",
      " <small>· ",
      "개 검사</small></summary><div class=\"scroll\"><table><thead><tr><th>검사 항목</th><th>결과</th><th>상세 설명</th></tr></thead><tbody>",
      "</tbody></table></div></details>"
    ],
    "en": [
      "<details ",
      "><summary>",
      " <small>· ",
      " checks</small></summary><div class=\"scroll\"><table><thead><tr><th>Check</th><th>Result</th><th>Details</th></tr></thead><tbody>",
      "</tbody></table></div></details>"
    ]
  },
  "m155": {
    "ko": [
      "<section class=\"card\"><div class=\"row between\"><div><h2>자격증명 등록</h2><p class=\"muted\">VC 또는 VP 파일을 제출하면 검증을 시작합니다. 여러 파일을 함께 선택할 수 있습니다.</p></div>",
      "</div><div class=\"upload-zone\"><label for=\"files\" style=\"margin-top:0\">자격증명 파일 선택</label><input id=\"files\" type=\"file\" multiple accept=\".jwt,.json,.zip,.txt\" aria-describedby=\"file-hint\"><div class=\"row between\"><small id=\"file-hint\">JWT · JSON · ZIP · TXT 지원</small>",
      "</div></div></section><div class=\"section-heading\"><h2>등록된 자격증명</h2><small>",
      "개 세트</small></div>",
      ""
    ],
    "en": [
      "<section class=\"card\"><div class=\"row between\"><div><h2>Register credentials</h2><p class=\"muted\">Submit VC or VP files to start verification. You can select multiple files together.</p></div>",
      "</div><div class=\"upload-zone\"><label for=\"files\" style=\"margin-top:0\">Select credential files</label><input id=\"files\" type=\"file\" multiple accept=\".jwt,.json,.zip,.txt\" aria-describedby=\"file-hint\"><div class=\"row between\"><small id=\"file-hint\">Supports JWT · JSON · ZIP · TXT</small>",
      "</div></div></section><div class=\"section-heading\"><h2>Registered credentials</h2><small>",
      " sets</small></div>",
      ""
    ]
  },
  "m156": {
    "ko": [
      "업로드 및 검증"
    ],
    "en": [
      "Upload & verify"
    ]
  },
  "m157": {
    "ko": [
      "<section class=\"card\"><div class=\"row between\"><div><h2>",
      "</h2><small>",
      " · 등록 ",
      "</small></div><div class=\"row\">",
      "",
      "</div></div><p class=\"muted\">유효기간 ",
      "</p><div class=\"row check-counts\">",
      "</div><div class=\"row\">",
      "",
      "",
      "</div><details><summary>문서별 검증 결과 <small>· 상세 검사와 확인 사유</small></summary><p class=\"credential-id\">세트 ID ",
      "</p>",
      "</details></section>"
    ],
    "en": [
      "<section class=\"card\"><div class=\"row between\"><div><h2>",
      "</h2><small>",
      " · Registered ",
      "</small></div><div class=\"row\">",
      "",
      "</div></div><p class=\"muted\">Valid until ",
      "</p><div class=\"row check-counts\">",
      "</div><div class=\"row\">",
      "",
      "",
      "</div><details><summary>Verification details by document <small>· Checks and supporting details</small></summary><p class=\"credential-id\">Set ID ",
      "</p>",
      "</details></section>"
    ]
  },
  "m158": {
    "ko": [
      "VC 세트"
    ],
    "en": [
      "Credential set"
    ]
  },
  "m159": {
    "ko": [
      "국가 미상"
    ],
    "en": [
      "Country unknown"
    ]
  },
  "m160": {
    "ko": [
      "현재 연결에 사용 중"
    ],
    "en": [
      "Used by current session"
    ]
  },
  "m161": {
    "ko": [
      "데모 연결 가능"
    ],
    "en": [
      "Eligible for demo access"
    ]
  },
  "m162": {
    "ko": [
      "확인 필요 / 만료"
    ],
    "en": [
      "Review needed / expired"
    ]
  },
  "m163": {
    "ko": [
      "<small>검사 결과 없음</small>"
    ],
    "en": [
      "<small>No check results</small>"
    ]
  },
  "m164": {
    "ko": [
      "재검증"
    ],
    "en": [
      "Recheck"
    ]
  },
  "m165": {
    "ko": [
      "참여 세션 연결"
    ],
    "en": [
      "Connect participant session"
    ]
  },
  "m166": {
    "ko": [
      "삭제"
    ],
    "en": [
      "Delete"
    ]
  },
  "m167": {
    "ko": [
      "<section class=\"card empty\"><h3>아직 등록된 자격증명이 없습니다</h3><p>위에서 VC / VP 파일을 선택해 첫 검증을 시작하세요.</p></section>"
    ],
    "en": [
      "<section class=\"card empty\"><h3>No credentials registered yet</h3><p>Select VC / VP files above to run your first verification.</p></section>"
    ]
  },
  "m168": {
    "ko": [
      "<div class=\"tabs\" aria-label=\"서비스 보기\"><button class=\"",
      "\" data-action=\"service-discover\">서비스 찾기 <small>",
      "</small></button><button class=\"",
      "\" data-action=\"my-contracts\">내 이용 계약 <small>",
      "</small></button></div>",
      "<div class=\"service-grid\">",
      "</div>",
      "<section class=\"card\"><div class=\"row between\"><h2>최근 요청 결과</h2><small id=\"response-label\">이 화면에서 실행한 요청</small></div><pre id=\"response\">",
      "</pre></section>"
    ],
    "en": [
      "<div class=\"tabs\" aria-label=\"Service view\"><button class=\"",
      "\" data-action=\"service-discover\">Discover services <small>",
      "</small></button><button class=\"",
      "\" data-action=\"my-contracts\">My contracts <small>",
      "</small></button></div>",
      "<div class=\"service-grid\">",
      "</div>",
      "<section class=\"card\"><div class=\"row between\"><h2>Latest response</h2><small id=\"response-label\">Requests made in this workspace</small></div><pre id=\"response\">",
      "</pre></section>"
    ]
  },
  "m169": {
    "ko": [
      "<section class=\"card row between\"><span class=\"muted\">서비스 이용을 위해 자격증명을 검증하고 참여 세션을 연결하세요.</span>"
    ],
    "en": [
      "<section class=\"card row between\"><span class=\"muted\">Verify credentials and connect a participant session to use services.</span>"
    ]
  },
  "m170": {
    "ko": [
      "자격증명으로 이동"
    ],
    "en": [
      "Go to credentials"
    ]
  },
  "m171": {
    "ko": [
      "<section class=\"card service-card\"><div class=\"row between\"><span class=\"service-type\">",
      "</span>",
      "</div><h2>",
      "</h2><p class=\"provider muted\">제공자 <b>",
      "</b> ",
      "</p><div class=\"service-meta\"><span>허용 국가 <b>",
      "</b></span><span>",
      "</span></div>",
      "",
      "<div class=\"row\">",
      "",
      "</div>",
      "</section>"
    ],
    "en": [
      "<section class=\"card service-card\"><div class=\"row between\"><span class=\"service-type\">",
      "</span>",
      "</div><h2>",
      "</h2><p class=\"provider muted\">Provider <b>",
      "</b> ",
      "</p><div class=\"service-meta\"><span>Allowed country <b>",
      "</b></span><span>",
      "</span></div>",
      "",
      "<div class=\"row\">",
      "",
      "</div>",
      "</section>"
    ]
  },
  "m172": {
    "ko": [
      "제공 중지"
    ],
    "en": [
      "Suspended"
    ]
  },
  "m173": {
    "ko": [
      "계약 활성"
    ],
    "en": [
      "Contract active"
    ]
  },
  "m174": {
    "ko": [
      "계약 가능"
    ],
    "en": [
      "Ready to contract"
    ]
  },
  "m175": {
    "ko": [
      "이용 조건 확인"
    ],
    "en": [
      "Check access requirements"
    ]
  },
  "m176": {
    "ko": [
      "플랫폼 샘플"
    ],
    "en": [
      "Platform sample"
    ]
  },
  "m177": {
    "ko": [
      "계약 만료 "
    ],
    "en": [
      "Contract expiry "
    ]
  },
  "m178": {
    "ko": [
      "계약 후 데이터 접근"
    ],
    "en": [
      "Data access requires a contract"
    ]
  },
  "m179": {
    "ko": [
      "<p class=\"muted\">현재 연결된 조직이 제공하는 서비스입니다.</p>"
    ],
    "en": [
      "<p class=\"muted\">This service is provided by your connected organization.</p>"
    ]
  },
  "m180": {
    "ko": [
      "<p class=\"muted\">현재 조직의 국가가 이용 조건과 다릅니다.</p>"
    ],
    "en": [
      "<p class=\"muted\">Your organization's country does not meet this service's policy.</p>"
    ]
  },
  "m181": {
    "ko": [
      "계약 해지"
    ],
    "en": [
      "End contract"
    ]
  },
  "m182": {
    "ko": [
      "서비스 계약"
    ],
    "en": [
      "Establish contract"
    ]
  },
  "m183": {
    "ko": [
      "연결 확인 · ping"
    ],
    "en": [
      "Check connection · ping"
    ]
  },
  "m184": {
    "ko": [
      "<details class=\"service-tools\"><summary>접속 주소 및 데이터 테스트</summary><label for=\"url-",
      "\">Web-ECDIS base URL</label><input class=\"key\" readonly type=\"password\" value=\"",
      "\" id=\"url-",
      "\"><div class=\"row\" style=\"margin-top:10px\">",
      "",
      "</div><small>접속 키가 포함된 주소입니다.</small>",
      "</details>"
    ],
    "en": [
      "<details class=\"service-tools\"><summary>Access URL & data request</summary><label for=\"url-",
      "\">Web-ECDIS base URL</label><input class=\"key\" readonly type=\"password\" value=\"",
      "\" id=\"url-",
      "\"><div class=\"row\" style=\"margin-top:10px\">",
      "",
      "</div><small>This URL contains your access key.</small>",
      "</details>"
    ]
  },
  "m185": {
    "ko": [
      "주소 표시 / 숨김"
    ],
    "en": [
      "Show / hide URL"
    ]
  },
  "m186": {
    "ko": [
      "주소 복사"
    ],
    "en": [
      "Copy URL"
    ]
  },
  "m187": {
    "ko": [
      "<label for=\"path-",
      "\">데이터 경로</label><select id=\"path-",
      "\">",
      "</select><label for=\"query-",
      "\">쿼리 · 선택 사항</label><input id=\"query-",
      "\" class=\"key\" placeholder=\"source=noaa&model=gfs\"><p class=\"muted\">경로를 제외한 key=value 형태로 입력하세요.</p>",
      ""
    ],
    "en": [
      "<label for=\"path-",
      "\">Data path</label><select id=\"path-",
      "\">",
      "</select><label for=\"query-",
      "\">Query parameters · optional</label><input id=\"query-",
      "\" class=\"key\" placeholder=\"source=noaa&model=gfs\"><p class=\"muted\">Enter key=value parameters without a path.</p>",
      ""
    ]
  },
  "m188": {
    "ko": [
      "데이터 요청"
    ],
    "en": [
      "Request data"
    ]
  },
  "m189": {
    "ko": [
      "<p class=\"muted\">허용된 데이터 경로가 없어 연결 확인만 가능합니다.</p>"
    ],
    "en": [
      "<p class=\"muted\">No data paths are allowed. Only the connection check is available.</p>"
    ]
  },
  "m190": {
    "ko": [
      "아직 이용 계약이 없습니다"
    ],
    "en": [
      "No access contracts yet"
    ]
  },
  "m191": {
    "ko": [
      "등록된 외부 서비스가 없습니다"
    ],
    "en": [
      "No external services registered"
    ]
  },
  "m192": {
    "ko": [
      "서비스를 둘러보고 필요한 데이터 서비스를 계약하세요."
    ],
    "en": [
      "Explore the catalog and establish a contract for a data service."
    ]
  },
  "m193": {
    "ko": [
      "다른 참여자가 서비스를 등록하면 이곳에 표시됩니다."
    ],
    "en": [
      "Services registered by other participants will appear here."
    ]
  },
  "m194": {
    "ko": [
      "서비스 찾기"
    ],
    "en": [
      "Discover services"
    ]
  },
  "m195": {
    "ko": [
      "연결 확인 또는 데이터 요청을 실행하면 응답이 표시됩니다."
    ],
    "en": [
      "Run a connection check or data request to see the response here."
    ]
  },
  "m196": {
    "ko": [
      "가입 신청이 접수되었습니다. 관리자 승인 후 로그인할 수 있습니다."
    ],
    "en": [
      "Sign-up request received. You can sign in once an operator approves it."
    ]
  },
  "m197": {
    "ko": [
      "승인 대기"
    ],
    "en": [
      "Pending approval"
    ]
  },
  "m198": {
    "ko": [
      "승인"
    ],
    "en": [
      "Approve"
    ]
  },
  "m199": {
    "ko": [
      "거절"
    ],
    "en": [
      "Reject"
    ]
  },
  "m200": {
    "ko": [
      " 계정을 승인했습니다."
    ],
    "en": [
      " has been approved."
    ]
  },
  "m201": {
    "ko": [
      "가입 신청을 거절하고 계정을 삭제할까요? 같은 아이디로 다시 신청할 수 있습니다."
    ],
    "en": [
      "Reject this sign-up and delete the account? The same username can apply again."
    ]
  },
  "m202": {
    "ko": [
      " 가입 신청을 거절했습니다."
    ],
    "en": [
      " sign-up request rejected."
    ]
  },
  "m203": {
    "ko": [
      "리포트 다운로드"
    ],
    "en": [
      "Download report"
    ]
  },
  "m204": {
    "ko": [
      "자격증명을 찾을 수 없습니다. 새로고침 후 다시 시도하세요."
    ],
    "en": [
      "Credential set not found. Refresh and try again."
    ]
  },
  "m205": {
    "ko": [
      "VC 검증 리포트"
    ],
    "en": [
      "Credential verification report"
    ]
  },
  "m206": {
    "ko": [
      "항목"
    ],
    "en": [
      "Item"
    ]
  },
  "m207": {
    "ko": [
      "값"
    ],
    "en": [
      "Value"
    ]
  },
  "m208": {
    "ko": [
      "조직"
    ],
    "en": [
      "Organization"
    ]
  },
  "m209": {
    "ko": [
      "국가"
    ],
    "en": [
      "Country"
    ]
  },
  "m210": {
    "ko": [
      "세트 ID"
    ],
    "en": [
      "Set ID"
    ]
  },
  "m211": {
    "ko": [
      "등록 시각"
    ],
    "en": [
      "Registered"
    ]
  },
  "m212": {
    "ko": [
      "유효기간"
    ],
    "en": [
      "Valid until"
    ]
  },
  "m213": {
    "ko": [
      "판정"
    ],
    "en": [
      "Result"
    ]
  },
  "m214": {
    "ko": [
      "검사 결과 수"
    ],
    "en": [
      "Check counts"
    ]
  },
  "m215": {
    "ko": [
      "리포트 생성 시각"
    ],
    "en": [
      "Report generated"
    ]
  },
  "m216": {
    "ko": [
      "검사"
    ],
    "en": [
      "Check"
    ]
  },
  "m217": {
    "ko": [
      "상태"
    ],
    "en": [
      "Status"
    ]
  },
  "m218": {
    "ko": [
      "상세"
    ],
    "en": [
      "Details"
    ]
  },
  "m219": {
    "ko": [
      "검사 결과가 없습니다."
    ],
    "en": [
      "No check results."
    ]
  },
  "m220": {
    "ko": [
      "검증 리포트를 다운로드했습니다."
    ],
    "en": [
      "Verification report downloaded."
    ]
  },
  "shell195": {
    "ko": [
      "Blue-X 홈"
    ],
    "en": [
      "Blue-X home"
    ]
  },
  "shell196": {
    "ko": [
      "주 메뉴"
    ],
    "en": [
      "Main navigation"
    ]
  },
  "shell197": {
    "ko": [
      "Gaia-X 기반 데이터 연결 PoC"
    ],
    "en": [
      "Gaia-X-based data access PoC"
    ]
  },
  "shell198": {
    "ko": [
      "참여자 개요"
    ],
    "en": [
      "Participant overview"
    ]
  },
  "shell199": {
    "ko": [
      "자격증명 등록부터 데이터 연결까지"
    ],
    "en": [
      "From credential verification to data access"
    ]
  },
  "shell200": {
    "ko": [
      "데모 정책에 따른 검증 결과이며, 공식 Gaia-X 인증이나 조직 대표 권한을 의미하지 않습니다."
    ],
    "en": [
      "Verification follows the demo policy. It does not certify Gaia-X compliance or authority to represent an organization."
    ]
  },
  "shell201": {
    "ko": [
      "시스템 정보 · v0.8.0 · loire-demo-v2 ⓘ"
    ],
    "en": [
      "System information · v0.8.0 · loire-demo-v2 ⓘ"
    ]
  },
  "shell202": {
    "ko": [
      "Blue-X 시스템 정보"
    ],
    "en": [
      "About Blue-X"
    ]
  },
  "shell203": {
    "ko": [
      "시스템 정보 닫기"
    ],
    "en": [
      "Close system information"
    ]
  },
  "shell204": {
    "ko": [
      "닫기"
    ],
    "en": [
      "Close"
    ]
  },
  "shell205": {
    "ko": [
      "애플리케이션"
    ],
    "en": [
      "Application"
    ]
  },
  "shell206": {
    "ko": [
      "검증 정책"
    ],
    "en": [
      "Verification policy"
    ]
  },
  "shell207": {
    "ko": [
      " · 프로젝트 데모 프로필"
    ],
    "en": [
      " · Project demo profile"
    ]
  },
  "shell208": {
    "ko": [
      "자격증명 환경"
    ],
    "en": [
      "Credential environment"
    ]
  },
  "shell209": {
    "ko": [
      "설계 참고 사양"
    ],
    "en": [
      "Design references"
    ]
  },
  "shell210": {
    "ko": [
      "참고 사양의 전체 구현·적합성 인증을 뜻하지 않습니다. 실제 검사는 프로젝트의 데모 정책과 포함된 스키마에 따라 수행합니다."
    ],
    "en": [
      "These references do not imply full implementation or conformity certification. Checks follow the project's demo policy and bundled schemas."
    ]
  }
};
// Exact matches only: participant names, URLs and raw API payloads are not translated.
const DIAGNOSTIC_TRANSLATIONS = {
  "참여자가 서비스에 등록하는 외부 API 주소는 이 목록의 origin(scheme://host[:port])과 일치해야 합니다. 추가·해제는 즉시 반영되며 재배포가 필요 없습니다. 해제하면 해당 origin을 쓰는 서비스는 곧바로 제공 중지됩니다. 각 origin 아래에는 포털이 호출할 수 있는 데이터 경로를 origin 기준 전체 경로(예: /api/griddata)로 등록하며, 정확히 일치하는 경로만 허용합니다. ping은 포털 내부 기능이라 등록하지 않습니다.": "External APIs must use an allowed origin (scheme://host[:port]). Changes take effect immediately. Removing an origin suspends its services. Register each permitted path under its origin (for example, /api/griddata); paths must match exactly. The internal ping endpoint does not need registration.",
  "운영자는 참여자 역할과 별개인 플랫폼 관리 권한입니다. 대상 계정의 콘솔을 열어 VC·세션·계약·제공 서비스·접속 키를 관리합니다. 운영자 권한 부여·해제는 서버의 manage_admin.py로만 합니다.": "Operators manage the platform independently of participant roles. Open an account console to manage credentials, sessions, contracts, services and access keys. Operator privileges can only be changed on the server using manage_admin.py.",
  "참여자 VC 없이 연결 테스트용으로만 쓰는 고정 샘플(demo://weather)입니다. 실제 API는 VC를 연결한 참여자 계정의 서비스 제공 메뉴에서 등록합니다.": "A fixed sample (demo://weather) for connectivity tests without participant credentials. To register a real API, connect a participant session and use My services.",
  "사설·루프백·메타데이터 등 내부 주소는 콘솔에서 허용할 수 없습니다. 운영 중 신뢰하는 기준선은 서버 환경변수로 두는 것을 권장합니다.": "Private, loopback and metadata addresses cannot be allowed through this console. Use server environment variables for trusted baseline settings.",
  "참고 사양의 전체 구현·적합성 인증을 뜻하지 않습니다. 실제 검사는 프로젝트의 데모 정책과 포함된 스키마에 따라 수행합니다.": "These references do not imply full implementation or conformity certification. Checks follow the project's demo policy and bundled schemas.",
  "허용을 해제할까요? 이 origin을 쓰는 서비스는 즉시 제공 중지되고, 콘솔에서 등록한 하위 경로도 함께 삭제됩니다.": "Remove this allowed origin? Its services will be suspended immediately, and paths registered through the console will also be removed.",
  "등록에 사용한 VC가 삭제·만료되거나 검증에 실패하면 제공이 중지됩니다. 참여 세션의 종료만으로는 중지되지 않습니다.": "Service delivery is suspended if its credential is deleted, expires or fails verification. Ending the participant session alone does not suspend delivery.",
  "VC를 삭제할까요? 연결된 세션과 계약이 해제되고, 이 VC로 제공 중인 서비스는 제공 중지됩니다.": "Delete this credential set? Linked sessions and contracts will end, and services using it will be suspended.",
  "고정 샘플은 demo://weather, 실제 API는 데이터 경로 앞의 기본 주소를 입력하세요.": "Use demo://weather for the fixed sample, or enter the base URL preceding the data path for a real API.",
  "데모 정책에 따른 검증 결과이며, 공식 Gaia-X 인증이나 조직 대표 권한을 의미하지 않습니다.": "Verification follows the demo policy. It does not certify Gaia-X compliance or authority to represent an organization.",
  "PoC 정책 변경은 서비스 삭제 후 재등록으로 진행합니다. 삭제 시 관련 계약도 해제됩니다.": "To change a policy in this PoC, delete and register the service again. Deletion also ends related contracts.",
  "VC 또는 VP 파일을 제출하면 검증을 시작합니다. 여러 파일을 함께 선택할 수 있습니다.": "Submit VC or VP files to start verification. You can select multiple files together.",
  "현재 세션과 이용 계약을 해제합니다. 자격증명·제공 서비스·접속 주소·로그는 유지됩니다.": "Ends the current session and access contracts. Credentials, provided services, access URLs and logs are retained.",
  "쿼리 칸에는 경로 없이 key=value만 입력하세요. 경로는 위 목록에서 선택합니다": "Enter key=value parameters only. Select the path from the list above.",
  "세션을 연결할까요? 기존 세션과 계약은 초기화되며 서비스 계약을 다시 해야 합니다.": "Connect this session? Existing sessions and contracts will be reset. You will need to establish service contracts again.",
  "접속 키를 재발급할까요? 기존 Web-ECDIS 주소는 사용할 수 없게 됩니다.": "Rotate the access key? Existing Web-ECDIS URLs will stop working.",
  "서비스 제공·이용은 로그인 후 VC 검증과 참여 세션 연결을 거쳐 진행합니다.": "After signing in, verify credentials and connect a participant session to provide or use services.",
  "Blue-X에서 조직의 자격증명을 검증하고 서비스를 제공하거나 이용하세요.": "Verify your organization's credentials, then provide or use data services with Blue-X.",
  "자격증명을 검증하고 참여 세션을 연결하면 서비스를 등록할 수 있습니다.": "Verify credentials and connect a participant session to register a service.",
  "검증 단계, 연결 결과, 데이터 요청 기록을 활동 로그에서 확인하세요.": "Review verification steps, connection results and data requests in the activity log.",
  "계약은 현재 참여 세션 및 자격증명의 유효기간 내에서 유지됩니다.": "The contract is valid only within the lifetime of the current session and credentials.",
  "등록된 경로가 없어 이 origin의 서비스는 ping만 가능합니다.": "No paths are registered. Only ping is available for this origin.",
  "다른 참여자가 계약하고 이용할 데이터 서비스를 제공할 수 있습니다.": "Publish a data service that other participants can contract and use.",
  "서비스 이용을 위해 자격증명을 검증하고 참여 세션을 연결하세요.": "Verify credentials and connect a participant session to use services.",
  "허용된 외부 API가 없습니다. 운영자에게 등록을 요청하세요.": "No external APIs are allowed yet. Ask an operator to register one.",
  "세션과 계약을 초기화할까요? VC, 주소, 로그는 유지됩니다.": "Reset the session and contracts? Credentials, access URLs and logs will be retained.",
  "서비스를 등록했습니다. 다른 참여자의 카탈로그에 표시됩니다.": "Service registered. Other participants can now find it in the catalog.",
  "작업 완료. 상세 결과는 활동 및 검증 로그에서 확인하세요.": "Completed. Open the activity log for detailed results.",
  "연결 확인 또는 데이터 요청을 실행하면 응답이 표시됩니다.": "Run a connection check or data request to see the response here.",
  "경로 허용을 해제할까요? 이 경로 호출은 즉시 차단됩니다.": "Remove this allowed path? Requests to this path will be blocked immediately.",
  "위에서 VC / VP 파일을 선택해 첫 검증을 시작하세요.": "Select VC / VP files above to run your first verification.",
  "검증이 완료되었습니다. 실패·확인 불가 항목을 확인하세요.": "Verification completed. Review failed and unverifiable checks.",
  "검증부터 데이터 요청까지, 모든 작업의 과정을 확인하세요.": "Trace every operation, from verification to data requests.",
  "내 데이터를 서비스로 제공하고 이용 현황을 확인하세요.": "Publish your data services and monitor their use.",
  "요청 성공. 활동 로그에서 결과를 확인할 수 있습니다.": "Request succeeded. Details are available in the activity log.",
  "서비스를 둘러보고 필요한 데이터 서비스를 계약하세요.": "Explore the catalog and establish a contract for a data service.",
  "하나의 계정으로 서비스를 제공하고 이용할 수 있어요.": "Use one account to both provide and consume services.",
  "운영자가 허용한 주소에 서비스를 등록할 수 있습니다.": "Services can use API addresses allowed by an operator.",
  "조직의 자격증명과 서비스 활동을 한눈에 확인하세요.": "Your organization's credentials and service activity at a glance.",
  "다른 참여자가 서비스를 등록하면 이곳에 표시됩니다.": "Services registered by other participants will appear here.",
  "불러오지 못했습니다. 새로고침으로 다시 시도하세요.": "Could not load this page. Select Refresh to try again.",
  "경로를 제외한 key=value 형태로 입력하세요.": "Enter key=value parameters without a path.",
  "허용된 데이터 경로가 없어 연결 확인만 가능합니다.": "No data paths are allowed. Only the connection check is available.",
  "건 · 최근 작업부터 표시 · 초기화 후에도 보존": " entries · Newest first · Retained after reset",
  "재발급하면 이전 접속 주소는 사용할 수 없습니다.": "Rotating the key invalidates previous access URLs.",
  "국가 코드는 KR처럼 영문 두 자리로 입력해주세요": "Enter a two-letter country code, such as KR.",
  "주소를 선택했습니다. Ctrl+C로 복사하세요.": "URL selected. Press Ctrl+C to copy it.",
  "참여자와 데이터 API 접근 범위를 관리하세요.": "Manage participants and permitted data API access.",
  "JWT · JSON · ZIP · TXT 지원": "Supports JWT · JSON · ZIP · TXT",
  "서비스를 찾아 계약하고 데이터에 연결하세요.": "Discover services, establish contracts and connect to data.",
  "자격증명에서 시작하는 신뢰 기반 데이터 연결": "Trusted data access starts with verifiable credentials.",
  "자격증명을 검증하고 참여 세션에 연결하세요.": "Verify credentials and connect your participant session.",
  "계정에 로그인해 참여자 공간을 열어보세요.": "Sign in to open your participant workspace.",
  "현재 조직의 국가가 이용 조건과 다릅니다.": "Your organization's country does not meet this service's policy.",
  "현재 연결된 조직이 제공하는 서비스입니다.": "This service is provided by your connected organization.",
  "유효기간 내 계약 · 요청 시 권한 재확인": "Unexpired contracts · Access rechecked on every request",
  "이 작업에는 별도 검사 항목이 없습니다.": "No separate checks were recorded for this operation.",
  "VC 검증 통과. 세션을 연결해보세요.": "Credential verification passed. Connect a participant session next.",
  "Gaia-X 기반 데이터 연결 PoC": "Gaia-X-based data access PoC",
  "데이터 서비스를 이용할 준비가 됐어요": "You're ready to explore data services.",
  "첫 연결 시 접속 주소가 생성됩니다.": "An access URL is created on your first connection.",
  "서비스 제공 · 계약 · 데이터 이용": "Provide services · Contract · Access data",
  "데이터 API origin 허용 목록": "Allowed data API origins",
  "제공과 이용을 함께 할 수 있습니다": "Provide and consume with one account",
  "플랫폼 샘플 서비스를 등록했습니다.": "Platform sample service registered.",
  "운영자 작업 중 · 관리 대상 계정": "Operator mode · Managing account",
  "presigned URL 발급 객체": "Objects with presigned URLs: ",
  "자격증명 등록부터 데이터 연결까지": "From credential verification to data access",
  "국가 코드 두 자리 · 예: KR": "Two-letter country code · e.g. KR",
  "예: Carol Co 격자 API": "e.g. Carol Co grid API",
  "가입 완료. VC를 등록해보세요.": "Account created. Add your credentials to get started.",
  "서비스와 관련 계약을 삭제할까요?": "Delete this service and its related contracts?",
  "서비스 등록 또는 계약 후 요청": "Publish a service or contract and request data",
  "아직 등록된 자격증명이 없습니다": "No credentials registered yet",
  "아직 계약한 참여자가 없습니다.": "No participants have established a contract yet.",
  "허용된 origin이 없습니다.": "No origins have been allowed yet.",
  "서비스를 계약할까요?": "Establish a contract for this service?",
  "접속 키가 포함된 주소입니다.": "This URL contains your access key.",
  "등록된 외부 서비스가 없습니다": "No external services registered",
  "접속 키가 발급되어 있습니다.": "An access key has been issued.",
  "허용된 데이터 경로가 없습니다": "No data paths are allowed.",
  "검증 결과와 연결 상태 확인": "Review verification and connection status",
  "데모 연결 가능한 VC 있음": "Credentials eligible for demo access",
  "접속 주소 및 데이터 테스트": "Access URL & data request",
  "작업이 어디까지 진행됐나요?": "Need to trace an operation?",
  "내 서비스를 이용하는 참여자": "Participants using my services",
  "자격증명을 등록·확인하세요": "Add or review your credentials.",
  "접속 주소를 복사했습니다.": "Access URL copied.",
  "경로 허용을 해제했습니다.": "Path permission removed.",
  "· 상세 검사와 확인 사유": "· Checks and supporting details",
  "아직 이용 계약이 없습니다": "No access contracts yet",
  "서비스 이름을 입력해주세요": "Enter a service name.",
  "이 화면에서 실행한 요청": "Requests made in this workspace",
  "Blue-X 시스템 정보": "About Blue-X",
  "· 프로젝트 데모 프로필": "· Project demo profile",
  "VC / VP 파일 등록": "Upload VC / VP files",
  "검증된 자격증명으로 연결": "Connect with verified credentials",
  "기록된 작업이 없습니다.": "No activity recorded yet.",
  "등록 가능한 외부 API": "Available external API origins",
  "첫 서비스를 등록해보세요": "Register your first service",
  "먼저 세션을 연결해주세요": "Connect a participant session first.",
  "연결 확인 · ping": "Check connection · ping",
  "참여 세션을 연결하세요": "Connect your participant session.",
  "자격증명 등록 및 검증": "Register and verify credentials",
  "연결 가능한 VC 확인": "Eligible credentials available",
  "허용 국가 (두 자리)": "Allowed country (two letters)",
  "예: 해양 기상 데이터": "e.g. Ocean weather data",
  "을(를) 허용했습니다.": "has been allowed.",
  "계약한 서비스 보기 →": "View my contracts →",
  "연결 및 접속 키 관리": "Session & access key settings",
  "허용을 해제했습니다.": "Permission removed.",
  "세션 종료 · 초기화": "End session & reset",
  "내 계정으로 돌아가기": "Back to my account",
  "등록된 자격증명 세트": "Credential sets",
  "계약 후 데이터 접근": "Data access requires a contract",
  "이미 계정이 있나요?": "Already have an account?",
  "데이터를 연결하세요.": "Connect to data.",
  "서비스 제공 · 이용": "Provide & consume",
  "제공 서비스 관리 →": "Manage my services →",
  "내가 제공하는 서비스": "Services I provide",
  "upstream 경로": "Upstream path",
  "현재 연결에 사용 중": "Used by current session",
  "경로를 허용했습니다.": "Path allowed.",
  "쿼리 · 선택 사항": "Query parameters · optional",
  "주소 표시 / 숨김": "Show / hide URL",
  "이용을 허용할 국가": "Allowed consumer country",
  "플랫폼 샘플 서비스": "Platform sample service",
  "확인 필요 / 만료": "Review needed / expired",
  "처음 방문하셨나요?": "New to Blue-X?",
  "자격증명 확인 필요": "Credentials need review",
  "참여자 식별자 보기": "View participant identifier",
  "파일을 선택해주세요": "Select a file first.",
  "활동 및 검증 로그": "Activity & verification log",
  "자격증명 파일 선택": "Select credential files",
  "참여자 계정 만들기": "Create a participant account",
  "접속 키 / 미인증": "Access key / unauthenticated",
  "문서별 검증 결과": "Verification details by document",
  "원본 API 주소": "Source API URL",
  "허용 데이터 경로": "Allowed data paths",
  "연결된 조직 없음": "No organization connected",
  "개 · 이용 계약": " services · Access contracts: ",
  "서비스 설정 보기": "View service settings",
  "참여자 계정 관리": "Participant accounts",
  "3–32자 아이디": "Username (3–32 characters)",
  "샘플 서비스 등록": "Register sample service",
  "자격증명 관리 →": "Manage credentials →",
  "시스템 정보 닫기": "Close system information",
  "신뢰를 확인하고,": "Verify trust.",
  "자격증명으로 이동": "Go to credentials",
  "자격증명 확인하기": "Review credentials",
  "업로드 및 검증": "Upload & verify",
  "Blue-X 홈": "Blue-X home",
  "새 서비스 등록": "Register a new service",
  "활동 로그 보기": "View activity log",
  "서버에서만 변경": "Change on server only",
  "조직 연결 완료": "Organization connected",
  "내 제공 서비스": "My services",
  "최근 요청 결과": "Latest response",
  "참여 세션 종료": "End participant session",
  "로그인했습니다.": "Signed in successfully.",
  "검사 결과 없음": "No check results",
  "참여 세션 연결": "Connect participant session",
  "· 일부만 기록": "· Partial record",
  "설계 참고 사양": "Design references",
  "서비스 둘러보기": "Explore services",
  "데모 연결 가능": "Eligible for demo access",
  "개 · 제공 중": " services · Available: ",
  "접속 키 재발급": "Rotate access key",
  "등록된 자격증명": "Registered credentials",
  "이용 조건 확인": "Check access requirements",
  "자격증명 등록": "Register credentials",
  "세션 연결하기": "Connect session",
  "자격증명 환경": "Credential environment",
  "불러오는 중…": "Loading…",
  "내 이용 계약": "My contracts",
  "성공 / 통과": "Success / pass",
  "개 계약 기록": " contract records",
  "메모 (선택)": "Note (optional)",
  "자격증명 검증": "Verify credentials",
  "서비스 찾기": "Discover services",
  "서비스 삭제": "Delete service",
  "서비스 등록": "Register service",
  "계정 만들기": "Create account",
  "참여자 개요": "Participant overview",
  "서비스 보기": "Service view",
  "사용 서비스": "Services using origin",
  "전체 서비스": "All services",
  "서비스 이용": "Use services",
  "서비스 없음": "No services",
  "세션 연결됨": "Session connected",
  "로그인 계정": "Signed-in account",
  "플랫폼 샘플": "Platform sample",
  "데이터 경로": "Data path",
  "이용 참여자": "Consumer",
  "서비스 계약": "Establish contract",
  "애플리케이션": "Application",
  "데이터 요청": "Request data",
  "서비스 이름": "Service name",
  "나의 활동": "My activity",
  "계약 만료": "Contract expiry",
  "서버 설정": "Server configuration",
  "검사 항목": "Check",
  "VC 세트": "Credential set",
  "제공 중지": "Suspended",
  "운영 관리": "Administration",
  "모든 결과": "All results",
  "제공 조직": "Provider organization",
  "허용 추가": "Allow origin",
  "확인 불가": "Unverifiable",
  "이름 없음": "Unnamed",
  "경로 메모": "Path note",
  "콘솔 열기": "Open console",
  "계약 가능": "Ready to contract",
  "8자 이상": "At least 8 characters",
  "허용 국가": "Allowed country",
  "연결됨 ·": "Connected ·",
  "가입 시각": "Created",
  "경로 추가": "Add path",
  "검증 정책": "Verification policy",
  "해당 없음": "Not applicable",
  "계약 활성": "Contract active",
  "참여 세션": "Participant session",
  "세트 ID": "Set ID",
  "상세 설명": "Details",
  "허용 해제": "Remove permission",
  "국가 미상": "Country unknown",
  "세션 만료": "Session expiry",
  "공통 검사": "Common checks",
  "작업 ID": "Operation ID",
  "전체 계정": "All accounts",
  "활동 로그": "Activity log",
  "계약 해지": "End contract",
  "주소 복사": "Copy URL",
  "검증 상태": "Verification status",
  "이용 계약": "Access contracts",
  "결과 필터": "Result filter",
  "새로고침": "Refresh",
  "제공 중": "Available",
  "비밀번호": "Password",
  "개 세트": " sets",
  "유효기간": "Valid until",
  "회원가입": "Sign up",
  "로그아웃": "Sign out",
  "개 검사": " checks",
  "주 메뉴": "Main navigation",
  "연결 전": "Not connected",
  "자격증명": "Credentials",
  "미연결": "Not connected",
  "아이디": "Username",
  "재검증": "Recheck",
  "운영자": "Operator",
  "실행자": "Actor",
  "미인증": "Unauthenticated",
  "미실행": "Not run",
  "서비스": "Service",
  "참여자": "Participant",
  "로그인": "Sign in",
  "제공자": "Provider",
  "만료": "Expiry",
  "세트": "sets",
  "다음": "Next",
  "등록": "Registered",
  "활성": "Active",
  "작업": "Operation",
  "닫기": "Close",
  "상태": "Status",
  "메모": "Note",
  "이전": "Previous",
  "출처": "Source",
  "통과": "Pass",
  "결과": "Result",
  "전체": "Total",
  "남음": "remaining",
  "관리": "Manage",
  "실패": "Fail",
  "콘솔": "Console",
  "해제": "Remove",
  "삭제": "Delete",
  "주의": "Warning",
  "시간": " hours",
  "권한": "Privileges",
  "경로": "Path",
  "계정": "Account",
  "분": " minutes",
  "개": " items",
  "초": " seconds",
  "건": " records",
  "총": "Total",
  "시스템 정보": "System information",
  "최대": "up to",
  "로그인이 필요합니다": "Please sign in.",
  "로그인 세션이 없거나 만료되었습니다. 다시 로그인해주세요": "Your login session is missing or expired. Please sign in again.",
  "관리자 계정은 서버에서 생성해야 합니다": "Operator accounts must be created on the server.",
  "아이디는 영문/숫자/._- 3~32자여야 합니다": "Use 3–32 letters, numbers or ._- for the username.",
  "비밀번호는 8~128자여야 합니다": "The password must contain 8–128 characters.",
  "이미 사용 중인 아이디입니다": "This username is already in use.",
  "가입 승인 대기 중인 아이디입니다": "This username is awaiting operator approval.",
  "관리자 승인 대기 중입니다": "Your account is awaiting operator approval.",
  "이미 승인된 계정입니다": "This account is already approved.",
  "가입 신청 (운영자 승인 대기)": "Sign-up requested (awaiting operator approval)",
  "아이디 또는 비밀번호가 올바르지 않습니다": "Incorrect username or password.",
  "참여 세션이 만료되었습니다": "The participant session has expired.",
  "자격증명 유효기간이 지났습니다": "The credentials have expired.",
  "파일 1~20개를 선택해주세요": "Select between 1 and 20 files.",
  "전체 업로드는 8 MB 이하여야 합니다": "Total upload size must not exceed 8 MB.",
  "운영자가 이 데이터 API origin의 허용을 해제해 제공이 중지되었습니다": "Service suspended: the operator removed permission for this API origin.",
  "제공자가 등록에 사용한 VC를 삭제해 제공이 중지되었습니다": "Service suspended: the provider deleted its registration credentials.",
  "제공자 VC가 최근 검증을 통과하지 못해 제공이 중지되었습니다": "Service suspended: the provider credentials failed their latest verification.",
  "제공자 자격증명 유효기간이 지나 제공이 중지되었습니다": "Service suspended: the provider credentials have expired.",
  "제공자 자격증명 유효기간을 확인할 수 없습니다": "The provider credentials' validity period could not be determined.",
  "플랫폼 샘플 서비스는 운영자만 등록할 수 있습니다": "Only operators can register platform sample services.",
  "실제 API는 VC를 연결한 참여자로 등록해야 합니다. 플랫폼 샘플은 demo://weather만 허용합니다": "Register real APIs using a connected participant account. Platform samples only allow demo://weather.",
  "서비스 제공은 VC 검증을 통과해 참여 세션을 연결한 참여자만 할 수 있습니다": "Verify credentials and connect a participant session before providing a service.",
  "서비스가 없습니다": "Service not found.",
  "본인이 제공하는 서비스만 삭제할 수 있습니다": "You can only delete services you provide.",
  "자신이 제공하는 서비스는 계약할 수 없습니다": "You cannot contract a service provided by your own organization.",
  "접근 승인이 만료되었습니다": "Access authorization has expired.",
  "현재 서비스 정책에 맞지 않습니다": "The current service policy is not satisfied.",
  "관리자 권한이 필요합니다": "Operator privileges are required.",
  "본인 계정만 관리할 수 있습니다": "You can only manage your own account.",
  "계정이 없습니다": "Account not found.",
  "연결된 참여 세션이 없습니다": "No participant session is connected.",
  "활성 서비스 계약이 없습니다. 카탈로그에서 계약해주세요": "No active service contract. Establish a contract in the catalog.",
  "서비스 국가 정책 불일치": "The service country policy is not satisfied.",
  "VC 세트를 선택해주세요": "Select a credential set.",
  "VC 검증을 통과해야 세션을 연결할 수 있습니다": "Credential verification must pass before connecting a session.",
  "VC 유효기간이 지났습니다": "The credentials have expired.",
  "회원가입 완료": "Account created",
  "로그인 완료": "Signed in",
  "서비스 오퍼링 등록": "Service offering registered",
  "서비스 오퍼링 삭제": "Service offering deleted",
  "VC 검증 통과": "Credential verification passed",
  "VC 검증: 차단 항목 확인 필요": "Credential verification: review blocking checks",
  "처리 완료": "Operation completed",
  "요청 실패": "Request failed",
  "참여 세션 연결 (최대 24시간)": "Participant session connected (up to 24 hours)",
  "세션·계약 초기화 (접속 주소 유지)": "Session and contracts reset (access URL retained)",
  "VC 삭제 및 연결된 세션·계약 해제": "Credentials deleted; linked session and contracts ended",
  "VC 재검증": "Credentials rechecked",
  "서비스 계약 해지": "Service contract ended",
  "서명": "Signature",
  "발급자": "Issuer",
  "기본 구조": "Basic structure",
  "폐기 상태": "Revocation status",
  "소유자 증명": "Holder proof"
};
let uiLocale='en';
try {uiLocale=localStorage.getItem('blue-x-language')==='ko'?'ko':'en';} catch {}
function t(key,...values){const parts=UI_MESSAGES[key]?.[uiLocale]||UI_MESSAGES[key]?.en;if(!parts)return key;return parts.map((s,i)=>s+(i<values.length?String(values[i]??''):'')).join('')}
function diagnostic(value){const s=String(value??'');return uiLocale==='en'?(DIAGNOSTIC_TRANSLATIONS[s]||s):s}
function applyShellLocale(){document.documentElement.lang=uiLocale;document.querySelectorAll('[data-i18n]').forEach(el=>el.textContent=t(el.dataset.i18n));for(const attr of ['aria-label','placeholder','title'])document.querySelectorAll('[data-i18n-'+attr+']').forEach(el=>el.setAttribute(attr,t(el.getAttribute('data-i18n-'+attr))));document.getElementById('ui-language').value=uiLocale}
function setLanguage(locale){
 if(!['en','ko'].includes(locale)||locale===uiLocale)return;
 if(typeof busy!=='undefined'&&busy){document.getElementById('ui-language').value=uiLocale;return}
 const content=document.getElementById('content');
 const fields=[...content.querySelectorAll('input,select,textarea')].filter(el=>el.id).map(el=>({id:el.id,value:el.value,checked:el.checked,type:el.type,node:el.type==='file'?el:null}));
 const opened=[...content.querySelectorAll('details')].map(el=>el.open);
 const focus=document.activeElement?.id,scroll=window.scrollY;
 uiLocale=locale;try{localStorage.setItem('blue-x-language',locale)}catch{}
 applyShellLocale();document.getElementById('notice').style.display='none';
 const savedResponse=lastResponse;
 if(state)render();else auth();
 lastResponse=savedResponse;
 // Async log/admin renderers only contain filters and configuration forms.
 const restore=()=>{for(const f of fields){const el=document.getElementById(f.id);if(!el)continue;if(f.type==='file'){el.replaceWith(f.node)}else{el.value=f.value;el.checked=f.checked;if(f.type==='password'||f.type==='text')el.type=f.type}}content.querySelectorAll('details').forEach((el,i)=>{if(i<opened.length)el.open=opened[i]});if(focus)document.getElementById(focus)?.focus({preventScroll:true});window.scrollTo(0,scroll)};
 if(state&&(tab==='logs'||tab==='admin')){const obs=new MutationObserver(()=>{if(content.querySelector('#logfilter,#originval')){obs.disconnect();restore()}});obs.observe(content,{childList:true});setTimeout(()=>obs.disconnect(),10000)}else restore();
}
applyShellLocale();document.getElementById('ui-language').addEventListener('change',e=>setLanguage(e.target.value));
