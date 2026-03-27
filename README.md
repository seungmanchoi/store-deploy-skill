# App Store Publisher Skill

Expo + React Native 앱을 App Store / Google Play에 배포하기 위한 Claude Code 스킬입니다.
빌드부터 스크린샷 생성, 메타데이터 업로드, 스토어 폼 작성, AdMob 설정까지 전체 파이프라인을 자동화합니다.

## 주요 기능

| 액션 | 설명 |
|------|------|
| `setup` | 선행 도구 설치 & fastlane 구조 자동 생성 |
| `build` | EAS 빌드 (로컬/클라우드, iOS/Android) |
| `screenshots` | 시뮬레이터 캡처 or AI 생성 + Pillow 후처리 (리사이즈 + 텍스트 오버레이) |
| `metadata` | AI 기반 메타데이터 생성 & fastlane으로 업로드 |
| `store-forms` | 브라우저 자동화로 연령등급, 개인정보, 데이터 안전 등 스토어 폼 입력 |
| `submit` | EAS Submit으로 바이너리 제출 |
| `admob` | AdMob 앱 생성 & 광고 단위 설정 (브라우저 자동화) |
| `full` | 위 모든 작업 순차 실행 |
| `status` | 현재 배포 상태 확인 |

## 설치

```bash
cd /Users/seungmanchoi/works/store-deploy-skill
chmod +x install.sh
./install.sh
```

설치 완료 후:
- `~/.claude/skills/store-deploy/SKILL.md` 심볼릭 링크 생성
- `~/.claude/commands/store-deploy.md` 심볼릭 링크 생성 (하위 호환)
- `scripts/` 디렉토리 복사

## 사전 요구사항

### 필수 도구

| 도구 | 설치 명령 | 용도 |
|------|----------|------|
| [EAS CLI](https://docs.expo.dev/eas/) | `npm install -g eas-cli` | Expo 빌드 & 제출 |
| [Fastlane](https://fastlane.tools/) | `brew install fastlane` | 메타데이터 & 스크린샷 업로드 |
| [Python 3 + Pillow](https://python-pillow.org/) | `pip3 install Pillow` | 스크린샷 리사이즈 & 텍스트 오버레이 |
| [agent-browser](https://github.com/vercel-labs/agent-browser) | `brew install agent-browser && agent-browser install` | 스토어 폼 & AdMob 브라우저 자동화 |

### 선택 도구

| 도구 | 용도 |
|------|------|
| Xcode + iOS Simulator | 시뮬레이터 기반 스크린샷 촬영 |
| nano-banana-mcp | AI 기반 스크린샷 생성 (Gemini) |
| Playwright MCP | Claude Code 내 브라우저 자동화 |

### 인증 정보 (크레덴셜)

#### iOS (App Store Connect)

| 항목 | 값 |
|------|-----|
| API Key 파일 | `~/works/common/AuthKey_6FD6879KFW.p8` |
| Key ID | `6FD6879KFW` |
| Issuer ID | `69a6de87-13e2-47e3-e053-5b8c7c11a4d1` |
| Apple ID | `blue_eng@hanmail.net` |
| Team ID | `6Y6T9LPHH3` |
| ITC Team ID | `117885592` |

#### Android (Google Play)

| 항목 | 값 |
|------|-----|
| 서비스 계정 JSON | `~/works/common/works-488915-4f58ab8044c4.json` |
| 서비스 계정 이메일 | `play-store-deploy@works-488915.iam.gserviceaccount.com` |

#### AdMob (선택)

AdMob REST API 사용 시 Google OAuth 2.0 설정이 필요합니다:

1. [Google API Console](https://console.cloud.google.com/apis) 접속
2. AdMob API 활성화
3. OAuth 2.0 클라이언트 ID 생성 (Desktop app 타입)
4. 클라이언트 ID/Secret을 `~/works/common/admob_credentials.json`에 저장

브라우저 자동화 방식으로도 AdMob 사용 가능하므로, OAuth 설정은 선택사항입니다.

## 사용 방법

### 기본 사용

1. Expo 프로젝트 디렉토리로 이동:
   ```bash
   cd ~/works/my-app
   ```

2. Claude Code에서 슬래시 커맨드 실행:
   ```
   /store-deploy
   ```

3. 원하는 액션 선택 (숫자 또는 이름)

### 특정 액션 직접 실행

```
/store-deploy screenshots
/store-deploy build ios
/store-deploy metadata
/store-deploy full
```

### 전체 파이프라인 (원스톱)

```
/store-deploy full
```

순서: setup → build → screenshots → metadata → submit → store-forms → summary

## 스크린샷 설정

### config.json

프로젝트 루트에 `screenshots/config.json`을 생성하여 텍스트 오버레이를 설정합니다:

```json
{
  "texts": {
    "en-US": [
      "Track Your Calories",
      "Easy Food Logging",
      "Beautiful Charts",
      "Set Your Goals"
    ],
    "ko": [
      "칼로리를 추적하세요",
      "간편한 음식 기록",
      "아름다운 차트",
      "목표를 설정하세요"
    ]
  },
  "fontSize": 56,
  "fontColor": "#FFFFFF",
  "overlayHeight": 200,
  "font": null
}
```

### 스크린샷 크기

| 플랫폼 | 디바이스 | 크기 (px) |
|--------|---------|-----------|
| iOS | iPhone 6.7" (필수) | 1290 × 2796 |
| iOS | iPhone 6.5" (선택) | 1242 × 2688 |
| Android | Phone (권장) | 1080 × 1920 |

### 디렉토리 구조

```
{project}/
  screenshots/
    config.json          # 텍스트 오버레이 설정
    ios/                 # iOS 원본 스크린샷
    android/             # Android 원본 스크린샷
  fastlane/
    screenshots/         # 처리된 iOS 스크린샷 (deliver 형식)
      en-US/
      ko/
    metadata/
      en-US/             # iOS 메타데이터
      ko/
      android/           # Android 메타데이터 + 스크린샷
        en-US/
          images/phoneScreenshots/
        ko-KR/
          images/phoneScreenshots/
```

## 스크린샷 후처리 스크립트 직접 사용

```bash
# 전체 처리 (iOS + Android)
python3 scripts/process_screenshots.py --project /path/to/your/app

# iOS만
python3 scripts/process_screenshots.py --platform ios --project /path/to/your/app

# Android만
python3 scripts/process_screenshots.py --platform android --project /path/to/your/app
```

## Fastlane 자동 설정

`/store-deploy setup` 실행 시 프로젝트에 다음이 자동 생성됩니다:

```
fastlane/
  Appfile          # 앱 식별자 & 팀 정보
  Fastfile         # iOS/Android 레인 (메타데이터, 스크린샷, 바이너리 업로드)
  Deliverfile      # iOS deliver 설정
  keys/            # 심볼릭 링크 (~/works/common/ → fastlane/keys/)
    AuthKey_6FD6879KFW.p8
    play-store-service-account.json
  metadata/        # 메타데이터 파일 구조
```

## 스토어 폼 자동 입력

`store-forms` 액션은 Playwright MCP 또는 agent-browser를 통해 다음을 자동 입력합니다:

### iOS (App Store Connect)
- 연령 등급 질문지
- 개인정보 처리방침 URL
- 앱 심사 정보 (연락처, 테스트 계정)
- 수출 규정 준수
- IDFA 사용 여부
- 개인정보 수집 세부사항

### Android (Google Play Console)
- 콘텐츠 등급 질문지
- 데이터 안전 양식
- 대상 연령층 설정
- 광고 포함 여부

**사전 조건**: 브라우저에서 App Store Connect / Google Play Console에 로그인된 상태여야 합니다.

## 트러블슈팅

### EAS 인증 오류
```bash
eas login
```

### Fastlane Apple ID 인증 실패
API Key 방식을 사용하므로 비밀번호 인증 불필요. `fastlane/keys/AuthKey_6FD6879KFW.p8` 심볼릭 링크가 올바른지 확인.

### Google Play 메타데이터 업로드 실패
첫 AAB/APK가 업로드되기 전에는 메타데이터를 업로드할 수 없음. `submit` → `metadata` 순서로 실행.

### 시뮬레이터 스크린샷 실패
```bash
xcrun simctl list devices available
# iPhone 16 Pro Max가 없으면:
xcodebuild -downloadPlatform iOS
```

### Pillow 폰트 오류
macOS 시스템 폰트를 자동 탐색함. 커스텀 폰트 사용 시 `screenshots/config.json`의 `font` 필드에 절대 경로 지정.

## 관련 링크

- [App Store Connect](https://appstoreconnect.apple.com)
- [Google Play Console](https://play.google.com/console)
- [AdMob Console](https://apps.admob.com)
- [EAS Build 문서](https://docs.expo.dev/build/introduction/)
- [EAS Submit 문서](https://docs.expo.dev/submit/introduction/)
- [Fastlane deliver 문서](https://docs.fastlane.tools/actions/deliver/)
- [Fastlane supply 문서](https://docs.fastlane.tools/actions/supply/)
- [Claude Code Skills 문서](https://code.claude.com/docs/skills)
