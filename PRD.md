# ArborMind AI - Product Requirements Document (PRD)

> 공원 이미지를 식생 타입으로 공간 분해하고, 면적 기반 탄소흡수 리포트를 자동 생성하는 End-to-End MVP

---

## 📋 목차

1. [프로젝트 개요](#프로젝트-개요)
2. [MVP 범위 정의](#mvp-범위-정의)
3. [사용자 시나리오](#사용자-시나리오)
4. [핵심 기능 명세](#핵심-기능-명세)
5. [기술 스택](#기술-스택)
6. [시스템 아키텍처](#시스템-아키텍처)
7. [API 명세](#api-명세)
8. [데이터 모델](#데이터-모델)
9. [개발 로드맵](#개발-로드맵)
10. [완료 기준](#완료-기준)

---

## 🎯 프로젝트 개요

### 핵심 가치 제안

**"공원을 측정 가능한 탄소 자산으로 전환합니다"**

ArborMind AI는 공원 이미지를 입력하면 식생을 **타입 단위로 공간 분해(면적 산출)** 하고, 그 결과를 기반으로 **탄소흡수량 추정 및 리포트(PDF + Word) 자동 생성**까지 이어지는 End-to-End 플랫폼입니다.

### 개발 단계

**🎯 1단계: Streamlit 프로토타입** (현재 문서 기준)
- 혼자 개발 가능한 구조
- Streamlit으로 빠른 MVP 구축
- 핵심 기능 검증 및 시연

**🚀 2단계: 완전 개발** (추후)
- React + FastAPI 풀스택
- 멀티 유저, 권한 관리
- 상용화 수준 배포

### 해결하는 문제

1. **데이터 부재**: 공원 식생의 정량적 데이터가 없음
2. **탄소 증명 불가**: ESG 경영 시대에 탄소 자산으로서의 가치를 증명하지 못함
3. **비효율적 운영**: 경험·수작업 중심의 관리 방식
4. **행정 부담**: ESG 리포트 작성에 과도한 인력/시간 소요

### MVP 성공 기준

```
✅ 정확도 X → 공간 분해 결과(면적)가 숫자로 산출되는가?
✅ 연구 수준 X → 리포트 결과물이 자동 생성되는가?
✅ 완벽함 X → 파이프라인이 안정적으로 작동하는가?
```

---

## 🔰 MVP 범위 정의

### ✅ 포함 (MUST HAVE)

| 카테고리 | 기능 |
|---------|------|
| **입력** | 이미지 업로드 (JPG/PNG 1장) |
| **메타데이터** | 공원명, 위치, 총 면적(선택) 입력 |
| **공간 분해** | 식생 타입 세그멘테이션 (4개 클래스) |
| **면적 산출** | 타입별 면적(㎡) 및 비율(%) 계산 |
| **시각화** | 오버레이 이미지 생성 |
| **탄소 계산** | 면적 × 계수 기반 탄소흡수량 산정 |
| **리포트** | PDF 자동 생성 및 다운로드 |
| **데이터** | 결과 JSON 저장 및 조회 API |

### ❌ 제외 (OUT OF SCOPE)

- 수종(종) 분류
- 수령/생장 모델
- 센서·IoT 연동
- 탄소 크레딧 인증 수준의 정확도
- 실측 데이터 기반 검정
- 정사영상 제작 자동화
- 고정밀 정확도 경쟁 (mIoU 등)

---

## 👤 사용자 시나리오

### 타겟 사용자

1. **지자체 공원 관리자**: 행정 보고용 데이터 필요
2. **ESG 담당자**: K-ESG 공시 대응 자료 필요
3. **대학 캠퍼스 관리자**: 그린 캠퍼스 인증 자료 필요
4. **민간 기업**: 사옥 조경 ESG 성과 증명 필요

### 사용 흐름 (30초 시연)

```
1. 이미지 업로드 (드론/항공/샘플 이미지)
   ↓
2. 공원 정보 입력 (공원명, 위치, 총 면적)
   ↓
3. [분석 실행] 클릭
   ↓
4. 결과 화면 확인
   - 타입별 면적 (㎡, %)
   - 오버레이 이미지
   - 연간 탄소흡수량 (tCO₂/yr)
   ↓
5. [PDF 다운로드] → 보고서 완성
```

---

## 🔧 핵심 기능 명세

### FR-01. 이미지 업로드

**입력**
- 파일 형식: JPG, PNG
- 권장 크기: 1024px 이상
- 최대 용량: 10MB

**완료 기준**
- [x] 업로드 성공/실패 메시지 표시
- [x] 업로드된 파일 미리보기
- [x] 지원하지 않는 형식 에러 처리

---

### FR-02. 공원 메타데이터 입력

**필수 입력**
- `park_name`: 공원명 (string, required)
- `location_text`: 위치/지자체 (string, required)

**선택 입력**
- `total_area_m2`: 총 공원 면적 (number, optional but recommended)
- `analysis_note`: 분석 메모 (string, optional)

**완료 기준**
- [x] 필수 항목 미입력 시 분석 실행 불가
- [x] 입력값 검증 (최소 길이, 유효성)
- [x] 자동 생성: 입력 일시

---

### FR-03. 식생 타입 공간 분해 (세그멘테이션)

**분류 클래스 (고정 4종)**

| 클래스 | 설명 | 컬러 코드 (시각화) |
|--------|------|-------------------|
| `TREE` | 교목 | #228B22 (Forest Green) |
| `SHRUB` | 관목 | #90EE90 (Light Green) |
| `GRASS` | 초지/잔디 | #7CFC00 (Lawn Green) |
| `NONVEG` | 비식생 (포장/시설/토양/수면) | #808080 (Gray) |

**처리 과정**
1. 이미지 입력 → 전처리 (리사이즈, 정규화)
2. AI 모델 추론 → 픽셀 단위 분류
3. 타입별 마스크 생성
4. 오버레이 이미지 생성 (원본 + 컬러 마스크)

**완료 기준**
- [x] 타입별 픽셀 분포 계산
- [x] 오버레이 이미지 PNG 생성
- [x] 동일 입력에서 재현 가능한 결과

---

### FR-04. 타입별 면적 산출

**산출 방식**

```python
# 1. 픽셀 비율 계산
type_ratio = type_pixel_count / total_pixel_count

# 2. 실제 면적 계산 (총 면적 입력 시)
if total_area_m2:
    type_area_m2 = total_area_m2 * type_ratio
else:
    type_area_m2 = None  # 비율만 제공
```

**출력**
- 각 타입별 `ratio` (%)
- 총 면적 입력 시 `area_m2` (㎡)

**완료 기준**
- [x] ratio 합계 = 100% (±1% 오차 허용)
- [x] 면적 합계 검증 (sanity check)
- [x] NONVEG 제외한 식생 면적 합계 계산

---

### FR-05. 탄소흡수량 계산

**기본 공식 (MVP)**

```
연간 탄소흡수량 (tCO₂/yr) = Σ [면적(㎡) × 타입계수(kgCO₂/㎡·yr)] ÷ 1000
```

**계수 구조**
- CSV 또는 DB 테이블로 관리
- 타입별 대표 계수 1개 (`coef_mid`)
- 버전, 출처 필드 포함

**완료 기준**
- [x] TREE, SHRUB, GRASS에 대해 탄소흡수량 계산
- [x] 타입별 기여도 및 총합 출력
- [x] 계산 근거(계수, 면적) 함께 반환

---

### FR-06. 리포트 자동 생성 (PDF + Word)

**출력 형식: 2종 필수**
- ✅ PDF 파일 (.pdf)
- ✅ Word 파일 (.docx)

**🔴 필수 포함 내용 (반드시 들어가야 함)**
1. **탄소 계산량** (tCO₂/yr)
   - 총 탄소흡수량
   - 타입별 탄소 기여도
   - 계산 근거 (면적 × 계수)
   
2. **항공 사진 분석 이미지**
   - 원본 이미지
   - 오버레이 이미지 (세그멘테이션 결과)
   - 컬러 범례 (TREE/SHRUB/GRASS/NONVEG)

---

**리포트 구성 (2~3 페이지)**

#### 페이지 1: 표지 및 요약
```
[ArborMind AI 공원 탄소흡수 추정 리포트]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 기본 정보
   - 공원명: ___
   - 위치: ___
   - 분석일: YYYY-MM-DD HH:MM
   - 총 면적: ___ ㎡

2. 식생 타입별 면적 요약
   ┌─────────┬──────────┬────────┬────────────┐
   │ 타입    │ 면적(㎡) │ 비율   │ 탄소흡수량 │
   ├─────────┼──────────┼────────┼────────────┤
   │ TREE    │  3,840   │  32%   │  9.87 tCO₂ │
   │ SHRUB   │    960   │   8%   │  0.56 tCO₂ │
   │ GRASS   │  5,400   │  45%   │  1.91 tCO₂ │
   │ NONVEG  │  1,800   │  15%   │  0.00 tCO₂ │
   └─────────┴──────────┴────────┴────────────┘

3. 🔴 연간 탄소흡수량 총계 (필수)
   ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
   ┃  총 탄소흡수량: 12.34 tCO₂/yr   ┃
   ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
   
   * 타입별 기여도 차트 (파이/바 차트)
```

#### 페이지 2: 🔴 항공 사진 분석 이미지 (필수)
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[원본 항공 사진]
(입력 이미지 삽입)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[식생 타입 분석 결과]
(오버레이 이미지 삽입)

범례:
🟢 TREE (교목) - 3,840㎡ (32%)
🟩 SHRUB (관목) - 960㎡ (8%)
🟨 GRASS (초지) - 5,400㎡ (45%)
⬜ NONVEG (비식생) - 1,800㎡ (15%)
```

#### 페이지 3: 산정 방법 및 근거
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. 탄소흡수량 산정 방법

본 리포트의 탄소흡수량은 다음과 같이 산정되었습니다:

[산정 공식]
연간 탄소흡수량(tCO₂/yr) = Σ [면적(㎡) × 타입별 계수(kgCO₂/㎡·yr)] ÷ 1000

[적용 계수]
- TREE (교목): 2.57 kgCO₂/㎡·yr
- SHRUB (관목): 0.58 kgCO₂/㎡·yr
- GRASS (초지): 0.35 kgCO₂/㎡·yr
(출처: MVP_ASSUMPTION_V1)

[계산 예시]
TREE: 3,840㎡ × 2.57 = 9,868.8 kgCO₂/yr = 9.87 tCO₂/yr

5. 데이터 품질 및 한계

본 수치는 MVP 단계의 대표값 기반 추정치입니다.
향후 다음 요소를 반영하여 정확도를 개선할 예정입니다:
- 수종별 세부 분류
- 수령 및 생육 상태
- 지역별 기후 특성
- 실측 데이터 검증

6. 고도화 계획

- 2단계: 수종 식별 및 개별 탄소계수 적용
- 3단계: IoT 센서 연동 실시간 모니터링
- 4단계: 탄소크레딧 인증 수준 정밀도 확보
```

---

**완료 기준**
- [x] PDF 파일 생성 및 다운로드
- [x] Word 파일 생성 및 다운로드
- [x] 🔴 탄소 계산량 (총량 + 타입별) 반드시 포함
- [x] 🔴 항공 사진 분석 이미지 (원본 + 오버레이) 반드시 포함
- [x] 표/차트 정상 렌더링
- [x] 컬러 범례 표시
- [x] 행정 언어 문장 템플릿
- [x] 페이지 번호 및 생성 일시 표시

---

### FR-07. 결과 저장 및 조회

**저장 데이터**
- 분석 ID (unique)
- 입력 메타데이터
- 면적/탄소 계산 결과 (JSON)
- 오버레이 이미지 경로
- PDF 파일 경로
- 생성 일시

**완료 기준**
- [x] 분석 결과 JSON 저장 (파일 or DB)
- [x] ID 기반 결과 조회 API
- [x] 최근 결과 리스트 조회 (옵션)

---

## 🛠 기술 스택

### 🎯 1단계 (프로토타입 - 혼자 개발)

#### All-in-One Platform
```
- Streamlit (Frontend + Backend 통합)
  * 빠른 프로토타입 개발
  * 별도 Frontend 개발 불필요
  * Python만으로 전체 구현
```

#### Backend & Processing
```
- Python 3.10+
- OpenCV (이미지 처리)
- Pillow (이미지 조작)
- NumPy, Pandas (데이터 처리)
```

#### AI/ML
```
- PyTorch or TensorFlow (선택)
- 경량 세그멘테이션 모델
- scikit-image (이미지 분석)
```

#### Storage
```
- SQLite (로컬 DB)
- 로컬 파일 시스템 (results/, uploads/, reports/)
```

#### Report Generation (필수 2종)
```
- PDF 생성: ReportLab or FPDF
- Word 생성: python-docx
- 차트: matplotlib or plotly
```

#### Deployment
```
- Local: streamlit run app.py
- Production: Docker (옵션)
```

---

### 🚀 2단계 (완전 개발 - 추후)

#### Frontend
```
- React 18+ or Next.js
- Tailwind CSS
- Recharts (차트)
```

#### Backend
```
- FastAPI
- PostgreSQL
- Redis (캐싱)
```

#### Deployment
```
- Docker + Kubernetes
- AWS/GCP
- CI/CD 파이프라인
```

---

## 🏗 시스템 아키텍처

### 🎯 1단계 아키텍처 (Streamlit 프로토타입)

```
┌──────────────────────────────────────────────────────────────┐
│                    Streamlit App (app.py)                    │
│                  Frontend + Backend 통합                     │
├──────────────────────────────────────────────────────────────┤
│  ┌────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   Upload   │  │ Segmentation │  │    Carbon    │        │
│  │   Module   │→│    Module    │→│    Module    │        │
│  └────────────┘  └──────────────┘  └──────────────┘        │
│         │                │                  │               │
│         ↓                ↓                  ↓               │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   Image    │  │   Overlay    │  │    Report    │        │
│  │  Storage   │  │   Generator  │  │   Generator  │        │
│  └────────────┘  └──────────────┘  └──────────────┘        │
│                                          │                   │
│                                          ↓                   │
│                                   ┌──────────────┐           │
│                                   │ PDF + Word   │           │
│                                   │  Generator   │           │
│                                   └──────────────┘           │
└──────────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
┌───────▼──────┐  ┌────────▼────────┐  ┌─────▼──────┐
│   SQLite     │  │  File Storage   │  │   Models   │
│   (DB)       │  │  uploads/       │  │  weights/  │
│              │  │  results/       │  │            │
│              │  │  reports/       │  │            │
└──────────────┘  └─────────────────┘  └────────────┘
```

### 폴더 구조 (1단계)

```
park/
├── app.py                          # 🎯 메인 Streamlit 앱
├── requirements.txt                # 패키지 목록
├── PRD.md                          # 프로젝트 문서
│
├── models/                         # AI 모델
│   ├── __init__.py
│   ├── segmentation.py            # 세그멘테이션 모델
│   └── weights/                   # 모델 가중치
│
├── utils/                          # 유틸리티
│   ├── __init__.py
│   ├── area_calculator.py         # 면적 계산
│   ├── carbon_calculator.py       # 탄소 계산
│   ├── image_processor.py         # 이미지 처리
│   └── report_generator.py        # PDF + Word 생성
│
├── data/                           # 데이터
│   ├── carbon_coefficients.csv    # 탄소 계수
│   └── arbormind.db               # SQLite DB
│
├── uploads/                        # 업로드 이미지 저장
├── results/                        # 분석 결과 저장
│   ├── overlays/                  # 오버레이 이미지
│   └── json/                      # 결과 JSON
│
└── reports/                        # 생성된 리포트
    ├── pdf/                       # PDF 파일
    └── word/                      # Word 파일
```

---

### 🚀 2단계 아키텍처 (완전 개발 - 추후)

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React/Next.js)                 │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP/REST
┌───────────────────────▼─────────────────────────────────────┐
│                   API Gateway (Nginx)                       │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                 Backend API (FastAPI)                       │
│  ┌────────────┬──────────────┬──────────────┬────────────┐ │
│  │  Upload    │ Segmentation │   Carbon     │   Report   │ │
│  │  Service   │   Service    │   Service    │   Service  │ │
│  └────────────┴──────────────┴──────────────┴────────────┘ │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐
│  PostgreSQL  │ │     S3     │ │   Redis    │
│   (Main DB)  │ │  (Storage) │ │  (Cache)   │
└──────────────┘ └────────────┘ └────────────┘
```

---

### 데이터 흐름 (1단계)

```
[사용자]
   ↓
[이미지 업로드] → Streamlit file_uploader
   ↓
[전처리] → OpenCV resize, normalize
   ↓
[AI 추론] → Segmentation Model
   ↓
[후처리] → 마스크 생성, 오버레이 이미지
   ↓
[면적 계산] → 픽셀 카운트 → ㎡ 변환
   ↓
[탄소 계산] ← carbon_coefficients.csv
   ↓
[결과 저장] → SQLite + JSON
   ↓
[리포트 생성] → PDF + Word
   ↓
[다운로드] → Streamlit download_button
```

---

## 📡 API 명세

> **참고**: 1단계 Streamlit 프로토타입에서는 API가 필요 없습니다.  
> 아래 API 명세는 **2단계 완전 개발** 시 참고용입니다.

### Base URL (2단계)
```
http://localhost:8000/api/v1
```

### 공통 규칙
- 모든 응답은 JSON 형식
- 파일 업로드는 `multipart/form-data`
- 날짜/시간은 ISO 8601 형식 (KST)

---

### 1. 분석 실행 (원샷 API)

**요청**
```http
POST /api/v1/analyze
Content-Type: multipart/form-data

image: file (required)
park_name: string (required)
location_text: string (required)
total_area_m2: number (optional, recommended)
analysis_note: string (optional)
```

**응답 (200 OK)**
```json
{
  "analysis_id": "ANL-20250104-0001",
  "park": {
    "park_name": "서울숲",
    "location_text": "서울시 성동구",
    "total_area_m2": 12000
  },
  "classes": ["TREE", "SHRUB", "GRASS", "NONVEG"],
  "segmentation": {
    "overlay_image_url": "/files/ANL-20250104-0001/overlay.png",
    "mask_summary": {
      "TREE": { "pixel_ratio": 0.32 },
      "SHRUB": { "pixel_ratio": 0.08 },
      "GRASS": { "pixel_ratio": 0.45 },
      "NONVEG": { "pixel_ratio": 0.15 }
    }
  },
  "areas": {
    "unit": "m2",
    "TREE": 3840,
    "SHRUB": 960,
    "GRASS": 5400,
    "NONVEG": 1800
  },
  "carbon": {
    "unit": "tCO2/yr",
    "total": 12.34,
    "by_type": {
      "TREE": 9.87,
      "SHRUB": 0.56,
      "GRASS": 1.91,
      "NONVEG": 0.0
    },
    "coefficients_used": {
      "TREE": {
        "coef_kgco2_m2_yr": 2.57,
        "source_name": "MVP_ASSUMPTION_V1"
      },
      "SHRUB": {
        "coef_kgco2_m2_yr": 0.58,
        "source_name": "MVP_ASSUMPTION_V1"
      },
      "GRASS": {
        "coef_kgco2_m2_yr": 0.35,
        "source_name": "MVP_ASSUMPTION_V1"
      }
    },
    "method": "sum(area_m2 * coef_kgco2_m2_yr) / 1000"
  },
  "artifacts": {
    "result_json_url": "/files/ANL-20250104-0001/result.json"
  },
  "created_at": "2025-01-04T16:00:00+09:00"
}
```

**에러 응답**
```json
// 400 Bad Request
{
  "error": "MISSING_REQUIRED_FIELD",
  "message": "park_name is required"
}

// 415 Unsupported Media Type
{
  "error": "INVALID_FILE_FORMAT",
  "message": "Only JPG and PNG files are supported"
}

// 500 Internal Server Error
{
  "error": "PROCESSING_FAILED",
  "message": "Failed to process image"
}
```

---

### 2. PDF 리포트 생성

**요청**
```http
POST /api/v1/report
Content-Type: application/json

{
  "analysis_id": "ANL-20250104-0001",
  "report_template": "ARBORMIND_V1",
  "language": "ko",
  "include_overlay": true
}
```

**응답 (200 OK)**
```json
{
  "analysis_id": "ANL-20250104-0001",
  "pdf_url": "/files/ANL-20250104-0001/report.pdf",
  "generated_at": "2025-01-04T16:03:00+09:00"
}
```

---

### 3. 분석 결과 조회

**요청**
```http
GET /api/v1/analysis/{analysis_id}
```

**응답**: `POST /analyze`와 동일 구조

---

### 4. 분석 목록 조회 (옵션)

**요청**
```http
GET /api/v1/analysis?limit=10&offset=0
```

**응답**
```json
{
  "total": 42,
  "limit": 10,
  "offset": 0,
  "results": [
    {
      "analysis_id": "ANL-20250104-0001",
      "park_name": "서울숲",
      "location_text": "서울시 성동구",
      "created_at": "2025-01-04T16:00:00+09:00"
    }
  ]
}
```

---

### 5. 파일 제공 (정적)

**요청**
```http
GET /files/{analysis_id}/{filename}
```

**파일 종류**
- `overlay.png`: 오버레이 이미지
- `result.json`: 결과 JSON
- `report.pdf`: PDF 리포트

---

## 💾 데이터 모델

### 1. carbon_coefficients (CSV/DB)

**테이블 구조**
```sql
CREATE TABLE carbon_coefficients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vegetation_type VARCHAR(20) NOT NULL,  -- TREE, SHRUB, GRASS
    coef_kgco2_m2_yr FLOAT NOT NULL,
    source_name VARCHAR(100),
    version VARCHAR(20),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**CSV 예시**
```csv
vegetation_type,coef_kgco2_m2_yr,source_name,version,updated_at
TREE,2.57,MVP_ASSUMPTION_V1,v1,2025-01-04
SHRUB,0.58,MVP_ASSUMPTION_V1,v1,2025-01-04
GRASS,0.35,MVP_ASSUMPTION_V1,v1,2025-01-04
```

> ⚠️ **참고**: 계수 값은 MVP 임시값(placeholder)이며 추후 근거 기반으로 업데이트 예정

---

### 2. analysis_results (DB)

**테이블 구조**
```sql
CREATE TABLE analysis_results (
    analysis_id VARCHAR(50) PRIMARY KEY,
    park_name VARCHAR(200) NOT NULL,
    location_text VARCHAR(500) NOT NULL,
    total_area_m2 FLOAT,
    mask_summary_json TEXT,           -- JSON 형태
    areas_json TEXT,                  -- JSON 형태
    carbon_json TEXT,                 -- JSON 형태
    overlay_path VARCHAR(500),
    pdf_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### 3. JSON 데이터 구조

**result.json 예시**
```json
{
  "analysis_id": "ANL-20250104-0001",
  "park": {
    "park_name": "서울숲",
    "location_text": "서울시 성동구",
    "total_area_m2": 12000
  },
  "segmentation": {
    "model_version": "v1.0",
    "mask_summary": {
      "TREE": { "pixel_ratio": 0.32, "pixel_count": 327680 },
      "SHRUB": { "pixel_ratio": 0.08, "pixel_count": 81920 },
      "GRASS": { "pixel_ratio": 0.45, "pixel_count": 460800 },
      "NONVEG": { "pixel_ratio": 0.15, "pixel_count": 153600 }
    }
  },
  "areas": {
    "unit": "m2",
    "TREE": 3840,
    "SHRUB": 960,
    "GRASS": 5400,
    "NONVEG": 1800
  },
  "carbon": {
    "unit": "tCO2/yr",
    "total": 12.34,
    "by_type": {
      "TREE": 9.87,
      "SHRUB": 0.56,
      "GRASS": 1.91,
      "NONVEG": 0.0
    },
    "coefficients_used": {
      "TREE": { "coef_kgco2_m2_yr": 2.57, "source_name": "MVP_ASSUMPTION_V1" },
      "SHRUB": { "coef_kgco2_m2_yr": 0.58, "source_name": "MVP_ASSUMPTION_V1" },
      "GRASS": { "coef_kgco2_m2_yr": 0.35, "source_name": "MVP_ASSUMPTION_V1" }
    },
    "method": "sum(area_m2 * coef_kgco2_m2_yr) / 1000"
  },
  "created_at": "2025-01-04T16:00:00+09:00"
}
```

---

## 🗓 개발 로드맵 (1단계 - Streamlit 프로토타입)

### Phase 1: 기초 세팅 (1주차)

**목표**: 프로젝트 골격 완성 + Streamlit 기본 구조

- [ ] 프로젝트 폴더 구조 생성
- [ ] `requirements.txt` 작성 (streamlit, opencv, pillow, numpy, pandas)
- [ ] 타입 클래스 확정 (TREE/SHRUB/GRASS/NONVEG)
- [ ] 계수 CSV 생성 (`carbon_coefficients.csv`)
- [ ] SQLite DB 스키마 설계
- [ ] Streamlit 기본 UI 구성
  - 페이지 레이아웃 (사이드바, 메인 영역)
  - 업로드 위젯
  - 입력 폼 (공원명, 위치, 면적)

**산출물**
- [ ] `app.py` (Streamlit 메인 앱)
- [ ] `carbon_coefficients.csv`
- [ ] 폴더 구조 완성
- [ ] 가상환경 설정

---

### Phase 2: 공간 분해 + 면적 산출 (2~3주차)

**목표**: 핵심 AI 기능 구현

- [ ] 세그멘테이션 구현
  - **초기 권장**: 컬러 기반 단순 분류 (빠른 프로토타입)
  - **선택**: 경량 딥러닝 모델 (MobileNet, U-Net Lite)
- [ ] 이미지 전처리 (`utils/image_processor.py`)
  - 리사이즈, 정규화
  - 노이즈 제거
- [ ] 타입별 픽셀 분류 및 마스크 생성
- [ ] 오버레이 이미지 생성 (OpenCV)
  - 원본 + 반투명 컬러 마스크
  - 컬러 범례 추가
- [ ] 면적 산출 로직 (`utils/area_calculator.py`)
  - 픽셀 카운트 → 비율(%) 계산
  - 총 면적 입력 시 → ㎡ 계산
- [ ] 결과 검증 (ratio 합계 100% 확인)

**Streamlit UI**
- [ ] 분석 실행 버튼
- [ ] 진행 상태 표시 (st.progress)
- [ ] 오버레이 이미지 표시 (st.image)
- [ ] 면적 결과 표 (st.dataframe)

**산출물**
- [ ] `models/segmentation.py`
- [ ] `utils/area_calculator.py`
- [ ] `utils/image_processor.py`
- [ ] 오버레이 이미지 샘플 3개

---

### Phase 3: 탄소 산정 연결 (4주차)

**목표**: 탄소 계산 및 결과 화면

- [ ] 계수 CSV 로딩 (`carbon_coefficients.csv`)
- [ ] 탄소 계산 로직 (`utils/carbon_calculator.py`)
  - 면적 × 계수 계산
  - 타입별 기여도
  - 총 탄소흡수량
- [ ] 결과 JSON 생성 및 저장 (`results/json/`)
- [ ] SQLite DB 저장

**Streamlit UI**
- [ ] 탄소 계산 결과 표시
  - 총 탄소흡수량 (큰 글씨, 강조)
  - 타입별 테이블 (면적 + 탄소)
- [ ] 차트 시각화 (matplotlib or plotly)
  - 파이 차트 (타입별 면적 비율)
  - 바 차트 (타입별 탄소 기여도)
- [ ] 계산 근거 표시 (expander 안에)

**산출물**
- [ ] `utils/carbon_calculator.py`
- [ ] 결과 화면 완성

---

### Phase 4: 리포트 생성 (PDF + Word) (5주차)

**목표**: 🔴 PDF + Word 리포트 자동 생성

- [ ] 리포트 템플릿 디자인 (2~3페이지)
- [ ] **PDF 생성** (`utils/report_generator.py`)
  - ReportLab or FPDF 사용
  - 표지, 표, 이미지 삽입
  - 차트 이미지 임베드
- [ ] **Word 생성** (`utils/report_generator.py`)
  - python-docx 사용
  - 동일 내용 구성
  - 표, 이미지, 차트 삽입
- [ ] 🔴 필수 내용 포함 확인
  - 탄소 계산량 (총량 + 타입별)
  - 항공 사진 분석 이미지 (원본 + 오버레이)
- [ ] 행정 언어 템플릿 문장 작성

**Streamlit UI**
- [ ] 리포트 생성 버튼
- [ ] 진행 상태 표시
- [ ] PDF 다운로드 버튼 (st.download_button)
- [ ] Word 다운로드 버튼 (st.download_button)
- [ ] 리포트 미리보기 (옵션)

**산출물**
- [ ] `utils/report_generator.py`
- [ ] PDF 템플릿 샘플
- [ ] Word 템플릿 샘플

---

### Phase 5: 시연 패키징 및 검증 (6주차)

**목표**: 안정화 및 시연 준비

- [ ] 공원 샘플 이미지 3~5개로 테스트
  - 다양한 크기, 구도, 구성
- [ ] 전체 플로우 반복 테스트
  - 업로드 → 분석 → 결과 → 리포트 다운로드
- [ ] 에러 핸들링
  - 잘못된 이미지 형식
  - 필수 입력 누락
  - 모델 처리 실패
- [ ] 성능 최적화
  - 이미지 리사이즈 적정 크기
  - 캐싱 활용 (st.cache_data, st.cache_resource)
- [ ] 로깅 추가
- [ ] 30초 데모 시나리오 고정
- [ ] README 작성
  - 설치 방법
  - 실행 방법
  - 사용 가이드

**산출물**
- [ ] 테스트 리포트
- [ ] README.md
- [ ] 데모 스크립트
- [ ] 실행 가능한 프로토타입

---

## ✅ 완료 기준

### 기능 체크리스트 (1단계 Streamlit 프로토타입)

**입력 및 검증**
- [ ] 이미지 업로드 가능 (JPG/PNG)
- [ ] 파일 미리보기 표시
- [ ] 공원명/위치 필수 입력 검증
- [ ] 총 공원 면적(㎡) 입력 필드 존재
- [ ] 파일 형식/크기 검증 및 에러 메시지

**분석 및 처리**
- [ ] [분석 실행] 버튼 클릭 시 처리 시작
- [ ] 진행 상태 표시 (progress bar or spinner)
- [ ] 타입별 분해 결과 생성 (TREE/SHRUB/GRASS/NONVEG)
- [ ] 타입별 비율(%) 계산 및 표시
- [ ] 총 면적 입력 시 타입별 면적(㎡) 계산 및 표시
- [ ] 오버레이 이미지 생성 및 화면 표시
- [ ] 컬러 범례 표시

**탄소 계산**
- [ ] 탄소흡수량 총합(tCO₂/yr) 큰 글씨로 강조 표시
- [ ] 타입별 탄소 기여도 표/차트로 표시
- [ ] 계산 근거(계수, 출처) 표시
- [ ] 차트 시각화 (파이 차트, 바 차트 중 1개 이상)

**🔴 리포트 생성 (필수 2종)**
- [ ] **PDF 생성 버튼** 작동
- [ ] **Word 생성 버튼** 작동
- [ ] PDF 파일 다운로드 가능 (st.download_button)
- [ ] Word 파일 다운로드 가능 (st.download_button)
- [ ] 🔴 **탄소 계산량** (총량 + 타입별) 반드시 포함
- [ ] 🔴 **항공 사진 분석 이미지** (원본 + 오버레이) 반드시 포함
- [ ] 표, 차트 정상 렌더링
- [ ] 컬러 범례 포함
- [ ] 행정 언어 문장 템플릿 적용
- [ ] 페이지 번호 및 생성 일시 표시

**데이터 관리**
- [ ] 결과 JSON 파일 저장 (`results/json/`)
- [ ] SQLite DB 저장
- [ ] 이전 분석 결과 조회 가능 (사이드바 선택)
- [ ] 업로드 이미지 저장 (`uploads/`)
- [ ] 오버레이 이미지 저장 (`results/overlays/`)
- [ ] 리포트 파일 저장 (`reports/pdf/`, `reports/word/`)

---

### 품질 체크리스트

**안정성**
- [ ] 샘플 이미지 3장 이상에서 동일 플로우로 결과 생성
- [ ] 동일 입력에서 재현 가능한 결과
- [ ] 에러 발생 시 적절한 에러 메시지

**성능**
- [ ] 샘플 이미지 기준 20초 이내 응답
- [ ] 서버 재시작 후 저장된 결과 조회 가능

**로깅**
- [ ] 요청/응답 로그 기록
- [ ] 에러 로그 상세 기록
- [ ] 분석 소요 시간 로그

---

### 시연 검증 기준

**30초 데모 시나리오 (Streamlit)**
1. 브라우저에서 `localhost:8501` 접속 → 2초
2. 샘플 이미지 업로드 (drag & drop) → 3초
3. 공원 정보 입력 (공원명, 위치, 면적) → 5초
4. [분석 실행] 버튼 클릭 → 10초
5. 결과 확인 (오버레이, 면적, 탄소) → 5초
6. PDF + Word 다운로드 → 5초

**심사자 체크 포인트**
- [ ] "이게 뭐 하는 건지" 직관적으로 이해됨
  - UI가 깔끔하고 흐름이 명확함
  - 버튼/입력 필드가 잘 보임
- [ ] "어떻게 계산했는지" 설명 가능함
  - 계수 출처 표시됨
  - 계산 근거 명시됨
- [ ] "이 결과물을 지자체 보고서에 붙여도 되겠다" 신뢰감
  - 🔴 탄소 계산량이 명확히 표시됨
  - 🔴 항공 사진 분석 이미지가 포함됨
  - 행정 언어로 작성됨
  - PDF + Word 모두 제공됨

---

## 📚 참고 자료

### 기술 문서 (1단계)
- [Streamlit 공식 문서](https://docs.streamlit.io/)
- [python-docx 문서](https://python-docx.readthedocs.io/)
- [ReportLab 사용 가이드](https://www.reportlab.com/docs/reportlab-userguide.pdf)
- [OpenCV Python 튜토리얼](https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html)

### 필수 패키지 (requirements.txt 예시)

```txt
# Streamlit
streamlit>=1.30.0

# 이미지 처리
opencv-python>=4.8.0
Pillow>=10.0.0
numpy>=1.24.0
scikit-image>=0.21.0

# 데이터 처리
pandas>=2.0.0

# 리포트 생성
reportlab>=4.0.0
python-docx>=1.0.0

# 차트
matplotlib>=3.7.0
plotly>=5.17.0

# AI/ML (선택)
# torch>=2.0.0
# torchvision>=0.15.0

# 기타
python-dateutil>=2.8.2
```

### 탄소 계수 참고
- 산림청 국가산림자원조사
- 환경부 탄소흡수원 가이드라인
- IPCC 온실가스 인벤토리 가이드라인

---

## 🚨 주의사항 및 리스크

### 개발 시 주의점 (1단계 Streamlit)

1. **정확도 논쟁 회피**
   - MVP는 "정확도 경쟁"이 아니라 "결과물 생성"이 목적
   - 리포트와 발표에서 선제적으로 명시
   - "한계 및 고도화 방향" 섹션 필수 포함

2. **범위 확대 주의**
   - 수종 분류, 센서 연동은 후속 확장으로만 문서에 남기기
   - 이번 범위에 절대 넣지 말 것
   - "이것만 되면 MVP 완성"에 집중

3. **설득력 확보 포인트**
   - 🔴 **탄소 계산량 + 항공 사진 이미지**가 필수
   - 오버레이 이미지 1장만 있어도 심사 설득력 크게 상승
   - PDF + Word 모두 제공하면 완성도 UP
   - 계수 값은 placeholder이며, 구조만 맞추는 것이 1차 목표

4. **Streamlit 개발 팁**
   - `st.cache_data` 활용해서 반복 계산 방지
   - `st.session_state`로 상태 관리
   - 이미지 크기 적절히 리사이즈 (메모리 관리)
   - 진행 상태 표시로 UX 개선 (`st.progress`, `st.spinner`)

5. **혼자 개발 시 우선순위**
   - ① 오버레이 이미지 생성 (가장 중요)
   - ② 탄소 계산 로직
   - ③ PDF + Word 리포트 생성
   - ④ UI 예쁘게 만들기 (마지막)

---

## 🎯 성공 지표 (KPI)

### 기술적 KPI
- 파이프라인 완결성: 업로드→분해→면적→탄소→PDF 끊김 없이 생성
- 응답 시간: 평균 15초 이내
- 에러율: 5% 미만

### 비즈니스 KPI
- 설명 가능성: 리포트에 산정 근거/한계/확장 계획 명시
- 재현성: 샘플 이미지 3개 이상에서 동일 흐름 결과 생성
- 확장성: 후속 고도화 지점이 구조적으로 열려 있음

---

## 📞 문의 및 지원

- **프로젝트 Owner**: [대표님 이름]
- **개발 파트너**: 클레브온 (ClevOn Inc.)
- **문의**: [이메일 주소]

---

**최종 한 줄**

> ArborMind AI 1단계 프로토타입은 "Streamlit 기반으로 공원 이미지를 식생 타입으로 공간 분해하고, 탄소 계산량과 항공 사진 분석 이미지가 포함된 PDF + Word 리포트를 자동 생성하는 흐름"을 증명한다.

---

**개발 목표 요약**

✅ **필수 출력**: PDF + Word 리포트 (2종)  
✅ **필수 내용**: 탄소 계산량 + 항공 사진 분석 이미지  
✅ **기술 스택**: Streamlit (All-in-One)  
✅ **개발 기간**: 6주 (Phase 1~5)  
✅ **성공 기준**: 30초 시연 가능

---

*Last Updated: 2025-01-04*  
*Version: 1.1 - Streamlit 프로토타입 버전*

