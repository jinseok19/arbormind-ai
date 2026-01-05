"""
ArborMind AI - 공원 탄소흡수 분석 시스템
1단계 Streamlit 프로토타입
"""

import streamlit as st
import os
from datetime import datetime
import json
import numpy as np
from PIL import Image
import cv2
from pathlib import Path
import pandas as pd

# 유틸리티 임포트
from utils.image_processor import ImageProcessor
from utils.area_calculator import AreaCalculator
from utils.carbon_calculator import CarbonCalculator
from utils.report_generator import ReportGenerator

# 페이지 설정
st.set_page_config(
    page_title="ArborMind AI - 공원 탄소흡수 분석",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 세션 상태 초기화
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = []
if 'current_result' not in st.session_state:
    st.session_state.current_result = None


def main():
    """메인 애플리케이션"""
    
    # 헤더
    st.title("🌳 ArborMind AI")
    st.markdown("### 공원 탄소흡수 분석 시스템")
    st.markdown("---")
    
    # 사이드바
    with st.sidebar:
        # 홈페이지 버튼
        st.link_button(
            "🏠 홈페이지로 돌아가기",
            "https://nexuscore.all4fit.co.kr/",
            use_container_width=True
        )
        
        st.markdown("---")
        
        st.header("📋 메뉴")
        page = st.radio(
            "페이지 선택",
            ["새 분석", "분석 결과", "정보"]
        )
        
        st.markdown("---")
        st.markdown("**ArborMind AI v1.0**")
        st.markdown("Streamlit 프로토타입")
    
    # 페이지 라우팅
    if page == "새 분석":
        page_new_analysis()
    elif page == "분석 결과":
        page_results()
    else:
        page_info()


def page_new_analysis():
    """새 분석 페이지"""
    st.header("🆕 새 분석")
    
    # 1. 이미지 업로드
    st.subheader("1. 항공 사진 업로드")
    uploaded_file = st.file_uploader(
        "공원 이미지를 업로드하세요 (JPG, PNG)",
        type=['jpg', 'jpeg', 'png'],
        help="드론 촬영 또는 항공 사진을 업로드하세요"
    )
    
    if uploaded_file:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.image(uploaded_file, caption="업로드된 이미지", use_column_width=True)
    
    # 2. 공원 정보 입력
    st.subheader("2. 공원 정보 입력")
    col1, col2 = st.columns(2)
    
    with col1:
        park_name = st.text_input(
            "공원명 *",
            placeholder="예: 서울숲",
            help="필수 입력"
        )
        total_area = st.number_input(
            "총 면적 (㎡)",
            min_value=0.0,
            value=0.0,
            step=100.0,
            help="공원 전체 면적을 입력하세요 (선택사항)"
        )
    
    with col2:
        location = st.text_input(
            "위치 *",
            placeholder="예: 서울시 성동구",
            help="필수 입력"
        )
        note = st.text_area(
            "메모",
            placeholder="분석 관련 메모 (선택)",
            height=100
        )
    
    # 3. 분석 실행
    st.markdown("---")
    
    # 입력 검증
    can_analyze = uploaded_file and park_name and location
    
    if not can_analyze:
        st.warning("⚠️ 이미지, 공원명, 위치는 필수 입력 항목입니다.")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_btn = st.button("🚀 분석 실행", disabled=not can_analyze, type="primary")
    
    if analyze_btn:
        analyze_park(uploaded_file, park_name, location, total_area, note)
    
    # 현재 분석 결과가 있으면 항상 표시
    if st.session_state.current_result:
        display_results(st.session_state.current_result)


def analyze_park(uploaded_file, park_name, location, total_area, note):
    """공원 분석 실행"""
    
    with st.spinner("🔄 분석 중... 잠시만 기다려주세요."):
        try:
            # 분석 ID 생성
            analysis_id = f"ANL-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            
            # 1. 이미지 저장
            uploads_dir = Path("uploads")
            uploads_dir.mkdir(exist_ok=True)
            
            image_path = uploads_dir / f"{analysis_id}.jpg"
            with open(image_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # 2. 이미지 로드 및 전처리
            pil_image = Image.open(uploaded_file)
            image_array = np.array(pil_image.convert('RGB'))
            
            processor = ImageProcessor()
            preprocessed = processor.preprocess(image_array)
            
            # 3. 세그멘테이션 실행
            st.write("🔍 이미지 분석 중...")
            masks = processor.segment_vegetation(preprocessed)
            
            # 4. 오버레이 이미지 생성
            st.write("🎨 오버레이 이미지 생성 중...")
            overlay = processor.create_overlay(preprocessed, masks)
            overlay_with_legend = processor.add_legend(overlay, masks)
            
            # 원본 이미지 저장 (세그멘테이션용)
            overlays_dir = Path("results/overlays")
            overlays_dir.mkdir(parents=True, exist_ok=True)
            original_path = overlays_dir / f"{analysis_id}_original.jpg"
            cv2.imwrite(str(original_path), cv2.cvtColor(preprocessed, cv2.COLOR_RGB2BGR))
            
            # 오버레이 이미지 저장
            overlay_path = overlays_dir / f"{analysis_id}_overlay.jpg"
            cv2.imwrite(str(overlay_path), cv2.cvtColor(overlay_with_legend, cv2.COLOR_RGB2BGR))
            
            # 5. 면적 계산
            st.write("📐 면적 계산 중...")
            area_calc = AreaCalculator()
            ratios = area_calc.calculate_pixel_ratios(masks)
            areas = area_calc.calculate_areas(ratios, total_area if total_area > 0 else None)
            
            # 6. 탄소 계산
            st.write("🌍 탄소흡수량 계산 중...")
            carbon_calc = CarbonCalculator()
            carbon = carbon_calc.calculate_carbon(areas)
            
            # 7. 결과 데이터 구성
            result = {
                "analysis_id": analysis_id,
                "timestamp": datetime.now().isoformat(),
                "park_info": {
                    "name": park_name,
                    "location": location,
                    "total_area_m2": total_area if total_area > 0 else None,
                    "note": note
                },
                "image_path": str(image_path),
                "original_path": str(original_path),
                "overlay_path": str(overlay_path),
                "segmentation": areas,
                "carbon": carbon
            }
            
            # 결과 JSON 저장
            json_dir = Path("results/json")
            json_dir.mkdir(parents=True, exist_ok=True)
            json_path = json_dir / f"{analysis_id}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            # 세션에 저장
            st.session_state.current_result = result
            st.session_state.analysis_results.append(result)
            
            st.success("✅ 분석 완료!")
            st.balloons()
            
        except Exception as e:
            st.error(f"❌ 분석 실패: {str(e)}")
            import traceback
            st.error(traceback.format_exc())


def display_results(result):
    """분석 결과 표시"""
    
    st.markdown("---")
    st.header("📊 분석 결과")
    
    # 기본 정보
    st.subheader("🏞️ 공원 정보")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("공원명", result["park_info"]["name"])
    with col2:
        st.metric("위치", result["park_info"]["location"])
    with col3:
        if result["park_info"]["total_area_m2"]:
            st.metric("총 면적", f"{result['park_info']['total_area_m2']:,.0f} ㎡")
        else:
            st.metric("총 면적", "미입력")
    
    # 원본 vs 세그멘테이션 비교
    if "original_path" in result and "overlay_path" in result:
        if Path(result["original_path"]).exists() and Path(result["overlay_path"]).exists():
            st.subheader("🖼️ 이미지 분석 결과")
            
            col1, col2 = st.columns(2)
            with col1:
                st.image(result["original_path"], caption="원본 이미지", use_column_width=True)
            with col2:
                st.image(result["overlay_path"], caption="세그멘테이션 결과", use_column_width=True)
    
    # 식생 타입별 면적
    st.subheader("🌿 식생 타입별 면적")
    
    seg_data = result["segmentation"]
    
    # 표 데이터 생성
    import pandas as pd
    table_data = []
    
    type_labels = {
        'BUILDING': '건물',
        'ROAD': '도로',
        'WATER': '물',
        'FOREST': '숲',
        'TREE': '나무',
        'GRASS': '초지',
        'WETLAND': '습지',
        'SOIL': '토양'
    }
    
    for veg_type, data in seg_data.items():
        label = type_labels.get(veg_type, veg_type)
        row = {
            "타입": label,
            "비율": f"{data['ratio_percent']:.1f}%",
        }
        if data['area_m2']:
            row["면적 (㎡)"] = f"{data['area_m2']:,.1f}"
        table_data.append(row)
    
    df = pd.DataFrame(table_data)
    st.dataframe(df, hide_index=True)
    
    # 시각화 차트 (전문적인 디자인)
    st.subheader("📈 비율 시각화")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 전문적인 파이 차트
        from utils.chart_generator import ChartGenerator
        chart_gen = ChartGenerator()
        
        temp_pie = f"temp_pie_{result['analysis_id']}.png"
        chart_gen.create_professional_pie_chart(seg_data, temp_pie)
        st.image(temp_pie, use_column_width=True)
        
        # 임시 파일 정리
        try:
            Path(temp_pie).unlink()
        except:
            pass
    
    with col2:
        # 전문적인 막대 차트
        temp_bar = f"temp_bar_{result['analysis_id']}.png"
        chart_gen.create_professional_bar_chart(seg_data, temp_bar)
        st.image(temp_bar, use_column_width=True)
        
        # 임시 파일 정리
        try:
            Path(temp_bar).unlink()
        except:
            pass
    
    # 탄소 계산 결과
    if result["park_info"]["total_area_m2"] and result["carbon"]["total_tco2_yr"] > 0:
        st.subheader("🌍 연간 탄소흡수량")
        
        # 총 탄소흡수량 (강조)
        st.markdown(f"""
        <div style="background-color: #e8f5e9; padding: 20px; border-radius: 10px; text-align: center;">
            <h2 style="color: #2e7d32; margin: 0;">총 탄소흡수량</h2>
            <h1 style="color: #1b5e20; margin: 10px 0;">{result['carbon']['total_tco2_yr']:.2f} tCO₂/yr</h1>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("")
        
        # 타입별 기여도
        col1, col2, col3 = st.columns(3)
        carbon_by_type = result["carbon"]["by_type"]
        
        with col1:
            if "TREE" in carbon_by_type:
                st.metric("🌳 TREE (교목)", f"{carbon_by_type['TREE']:.2f} tCO₂/yr")
        with col2:
            if "SHRUB" in carbon_by_type:
                st.metric("🌿 SHRUB (관목)", f"{carbon_by_type['SHRUB']:.2f} tCO₂/yr")
        with col3:
            if "GRASS" in carbon_by_type:
                st.metric("🌾 GRASS (초지)", f"{carbon_by_type['GRASS']:.2f} tCO₂/yr")
    
    else:
        st.info("ℹ️ 총 면적을 입력하면 탄소흡수량이 계산됩니다.")
    
    # 리포트 생성 버튼
    st.markdown("---")
    st.subheader("📄 리포트 생성")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # PDF 생성 버튼 (key 추가로 고유하게 만들기)
        pdf_btn_key = f"pdf_btn_{result['analysis_id']}"
        if st.button("📕 PDF 리포트 생성", key=pdf_btn_key):
            try:
                with st.spinner("PDF 생성 중..."):
                    report_gen = ReportGenerator()
                    
                    # PDF 생성
                    pdf_path = report_gen.generate_pdf(
                        analysis_id=result["analysis_id"],
                        park_info=result["park_info"],
                        areas=result["segmentation"],
                        carbon=result["carbon"],
                        original_image_path=result.get("original_path"),
                        overlay_image_path=result.get("overlay_path")
                    )
                    
                    # 세션에 PDF 경로 저장
                    st.session_state[f'pdf_path_{result["analysis_id"]}'] = pdf_path
                    
                    st.success(f"✅ PDF 생성 완료!")
                    st.rerun()
            except Exception as e:
                st.error(f"❌ PDF 생성 실패: {str(e)}")
                import traceback
                st.error(traceback.format_exc())
        
        # PDF 다운로드 버튼 (PDF가 생성된 경우)
        pdf_key = f'pdf_path_{result["analysis_id"]}'
        if pdf_key in st.session_state and Path(st.session_state[pdf_key]).exists():
            with open(st.session_state[pdf_key], "rb") as f:
                st.download_button(
                    label="📥 PDF 다운로드",
                    data=f,
                    file_name=f"{result['park_info']['name']}_리포트.pdf",
                    mime="application/pdf",
                    key=f"pdf_download_{result['analysis_id']}"
                )
    
    with col2:
        # Word 생성 버튼
        word_btn_key = f"word_btn_{result['analysis_id']}"
        if st.button("📘 Word 리포트 생성", key=word_btn_key):
            try:
                with st.spinner("Word 생성 중..."):
                    report_gen = ReportGenerator()
                    
                    # Word 생성
                    word_path = report_gen.generate_word(
                        analysis_id=result["analysis_id"],
                        park_info=result["park_info"],
                        areas=result["segmentation"],
                        carbon=result["carbon"],
                        original_image_path=result.get("original_path"),
                        overlay_image_path=result.get("overlay_path")
                    )
                    
                    # 세션에 Word 경로 저장
                    st.session_state[f'word_path_{result["analysis_id"]}'] = word_path
                    
                    st.success(f"✅ Word 생성 완료!")
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Word 생성 실패: {str(e)}")
                import traceback
                st.error(traceback.format_exc())
        
        # Word 다운로드 버튼 (Word가 생성된 경우)
        word_key = f'word_path_{result["analysis_id"]}'
        if word_key in st.session_state and Path(st.session_state[word_key]).exists():
            with open(st.session_state[word_key], "rb") as f:
                st.download_button(
                    label="📥 Word 다운로드",
                    data=f,
                    file_name=f"{result['park_info']['name']}_리포트.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key=f"word_download_{result['analysis_id']}"
                )


def page_results():
    """분석 결과 페이지"""
    st.header("📂 분석 결과")
    
    if not st.session_state.analysis_results:
        st.info("아직 분석 결과가 없습니다. '새 분석' 페이지에서 분석을 시작하세요.")
        return
    
    st.write(f"총 {len(st.session_state.analysis_results)}개의 분석 결과가 있습니다.")
    
    for i, result in enumerate(reversed(st.session_state.analysis_results)):
        with st.expander(
            f"{result['park_info']['name']} - {result['timestamp'][:19]}",
            expanded=(i == 0)
        ):
            display_results(result)


def page_info():
    """정보 페이지"""
    st.header("ℹ️ ArborMind AI 정보")
    
    st.markdown("""
    ### 🌳 ArborMind AI란?
    
    공원 이미지를 입력하면 식생을 타입 단위로 공간 분해하고,
    면적 기반 탄소흡수량을 추정하여 **PDF + Word 리포트**를 자동 생성하는
    End-to-End 플랫폼입니다.
    
    ### 📋 주요 기능
    
    - ✅ 항공/드론 이미지 업로드
    - ✅ 식생 타입 자동 분류 (TREE, SHRUB, GRASS, NONVEG)
    - ✅ 면적 자동 계산
    - ✅ 탄소흡수량 추정
    - ✅ PDF + Word 리포트 생성
    
    ### 🎯 현재 버전
    
    **v1.0 - Streamlit 프로토타입**
    - 1단계 MVP
    - 기본 기능 검증용
    
    ### 🚀 개발 로드맵
    
    - **1단계** (현재): Streamlit 프로토타입
    - **2단계** (추후): React + FastAPI 풀스택 개발
    
    ### 📞 문의
    
    프로젝트 관련 문의사항이 있으시면 연락주세요.
    """)
    
    st.markdown("---")
    st.markdown("**ArborMind AI** - 공원을 측정 가능한 탄소 자산으로 전환합니다")


if __name__ == "__main__":
    main()

