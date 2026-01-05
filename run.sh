#!/bin/bash

echo "========================================"
echo " 🌳 ArborMind AI 실행 스크립트"
echo "========================================"
echo ""

# 가상환경 확인
if [ ! -d "venv" ]; then
    echo "[1/3] 가상환경 생성 중..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ 가상환경 생성 실패. Python3가 설치되어 있는지 확인하세요."
        exit 1
    fi
    echo "✅ 가상환경 생성 완료"
else
    echo "✅ 가상환경 이미 존재"
fi

echo ""
echo "[2/3] 가상환경 활성화 중..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "❌ 가상환경 활성화 실패"
    exit 1
fi

echo ""
echo "[3/3] 패키지 확인 및 설치 중..."
if ! pip list | grep -q streamlit; then
    echo "Streamlit이 설치되어 있지 않습니다. 설치 중..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ 패키지 설치 실패"
        exit 1
    fi
    echo "✅ 패키지 설치 완료"
else
    echo "✅ 패키지 이미 설치됨"
fi

echo ""
echo "========================================"
echo " 🚀 ArborMind AI 시작!"
echo "========================================"
echo ""
echo "브라우저에서 http://localhost:8501 을 열어주세요."
echo "종료하려면 Ctrl+C 를 누르세요."
echo ""

streamlit run app.py

