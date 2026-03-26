# store-deploy-skill

Expo + React Native 앱을 App Store / Google Play에 배포하기 위한 Claude Code 슬래시 커맨드 스킬입니다.

## 이 스킬이 하는 일

현재 프로젝트의 `app.json`을 읽어 앱 정보를 자동으로 파악하고, 아래 작업들을 대화형으로 진행합니다:

- **build** — EAS Build로 프로덕션 바이너리 빌드 (`eas build --profile production`)
- **submit** — EAS Submit으로 스토어에 바이너리 제출 (`eas submit --profile production`)
- **metadata** — Fastlane으로 스토어 메타데이터(앱 이름, 설명, 키워드 등) 업로드
- **screenshots** — app-publisher-mcp로 스토어 스크린샷 생성 후 Fastlane으로 업로드
- **full** — 위 모든 작업을 순서대로 실행하는 전체 파이프라인

### 자동화되는 것들

- `fastlane/` 디렉토리가 없으면 자동으로 생성 (Appfile, Fastfile, 메타데이터 폴더 구조)
- App Store Connect API Key 및 Google Play 서비스 계정 JSON 경로 자동 설정
- `eas.json`에 submit 프로파일이 없으면 추가 안내

### 지원 플랫폼

- iOS (App Store)
- Android (Google Play)
- 양쪽 동시 실행

## 설치 방법

```bash
cd /Users/seungmanchoi/works/store-deploy-skill
chmod +x install.sh
./install.sh
```

설치가 완료되면 `~/.claude/commands/store-deploy.md`로 심볼릭 링크가 생성됩니다.

## 사용 방법

1. 터미널에서 배포할 Expo 프로젝트 디렉토리로 이동합니다:
   ```bash
   cd ~/works/my-app
   ```

2. Claude Code를 실행하고 슬래시 커맨드를 입력합니다:
   ```
   /store-deploy
   ```

3. Claude가 `app.json`에서 앱 정보를 읽고, 플랫폼과 작업을 물어봅니다. 원하는 옵션을 선택하면 됩니다.

## 사전 요구사항

- [EAS CLI](https://docs.expo.dev/eas/) 설치: `npm install -g eas-cli`
- [Fastlane](https://fastlane.tools/) 설치: `brew install fastlane`
- EAS 로그인 상태: `eas login`
- `~/works/common/AuthKey_6FD6879KFW.p8` 파일 존재 (iOS)
- `~/works/common/works-488915-4f58ab8044c4.json` 파일 존재 (Android)

## 관련 링크

- [App Store Connect](https://appstoreconnect.apple.com)
- [Google Play Console](https://play.google.com/console)
- [EAS Build 문서](https://docs.expo.dev/build/introduction/)
- [EAS Submit 문서](https://docs.expo.dev/submit/introduction/)
- [Fastlane deliver 문서](https://docs.fastlane.tools/actions/deliver/)
- [Fastlane supply 문서](https://docs.fastlane.tools/actions/supply/)
