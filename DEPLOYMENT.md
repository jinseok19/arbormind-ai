# 🚀 ArborMind AI 배포 가이드

## Streamlit Community Cloud 배포

### 1단계: GitHub 레포지토리 준비

#### 1. GitHub 레포지토리 생성
1. [GitHub](https://github.com) 접속 및 로그인
2. 우측 상단 `+` → `New repository` 클릭
3. Repository 이름: `arbormind-ai`
4. Public 또는 Private 선택
5. `Create repository` 클릭

#### 2. 로컬 Git 초기화 및 푸시

터미널에서 다음 명령어 실행:

```bash
# Git 초기화
git init

# 모든 파일 추가
git add .

# 커밋
git commit -m "Initial commit: ArborMind AI MVP"

# GitHub 레포지토리 연결 (본인의 레포지토리 URL로 변경)
git remote add origin https://github.com/YOUR_USERNAME/arbormind-ai.git

# 푸시
git branch -M main
git push -u origin main
```

---

### 2단계: Streamlit Community Cloud 배포

#### 1. Streamlit Cloud 접속
1. [share.streamlit.io](https://share.streamlit.io) 접속
2. GitHub 계정으로 로그인

#### 2. 앱 배포
1. `New app` 버튼 클릭
2. 설정 입력:
   - **Repository**: `YOUR_USERNAME/arbormind-ai`
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **App URL**: 원하는 URL 설정 (예: `arbormind-ai`)

3. `Deploy!` 클릭

#### 3. 배포 완료
- 2~5분 후 배포 완료
- URL: `https://arbormind-ai.streamlit.app` (또는 설정한 URL)

---

### 3단계: 배포 확인

#### 체크리스트
- [ ] 앱이 정상 실행되는가?
- [ ] 이미지 업로드가 작동하는가?
- [ ] 세그멘테이션 결과가 표시되는가?
- [ ] 차트가 정상 표시되는가?
- [ ] PDF 다운로드가 작동하는가?
- [ ] Word 다운로드가 작동하는가?

---

## 문제 해결

### 폰트 문제 (한글 깨짐)
Streamlit Cloud는 Linux 기반이므로 `packages.txt`에 한글 폰트가 설치됩니다:
- 나눔고딕 (`fonts-nanum`)
- 파일에 이미 포함됨 ✅

### OpenCV 문제
`opencv-python-headless` 사용 (GUI 없는 버전) ✅

### 메모리 제한
무료 플랜: 1GB RAM
- 이미지 크기를 1024x1024로 제한 (현재 구현됨) ✅

---

## 배포 URL 공유

배포 완료 후:
```
https://arbormind-ai.streamlit.app
```

이 URL을 공유하면 누구나 접속해서 사용 가능합니다!

---

## 업데이트 방법

코드 수정 후:

```bash
git add .
git commit -m "Update: [수정 내용]"
git push
```

자동으로 Streamlit Cloud에 재배포됩니다 (1~2분 소요).

---

## 비용

**무료 플랜**
- Public 앱 무제한
- 1GB RAM
- Community 지원

**충분합니다!** MVP는 무료 플랜으로 완벽하게 작동합니다.

