"""전문적인 차트 생성 모듈"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import font_manager
import numpy as np
from typing import Dict, List
from pathlib import Path


class ChartGenerator:
    """전문적인 분석 차트 생성 클래스"""
    
    def __init__(self):
        # 한글 폰트 설정 (여러 옵션 시도)
        font_candidates = [
            'Malgun Gothic',
            'NanumGothic',
            'NanumBarunGothic',
            'AppleGothic',
            'DejaVu Sans'
        ]
        
        for font_name in font_candidates:
            try:
                plt.rcParams['font.family'] = font_name
                # 테스트
                fig, ax = plt.subplots(1, 1, figsize=(1, 1))
                ax.text(0.5, 0.5, '테스트', fontsize=10)
                plt.close(fig)
                break
            except:
                continue
        
        plt.rcParams['axes.unicode_minus'] = False
        plt.rcParams['font.size'] = 10
        
        # 전문적인 컬러 팔레트 (Seaborn 스타일)
        self.colors = {
            'BUILDING': '#E74C3C',  # 빨강
            'ROAD': '#34495E',      # 진한 회색
            'WATER': '#3498DB',     # 파랑
            'FOREST': '#27AE60',    # 녹색
            'TREE': '#2ECC71',      # 밝은 녹색
            'GRASS': '#A9DFBF',     # 연한 녹색
            'WETLAND': '#1ABC9C',   # 청록색
            'SOIL': '#8D6E63'       # 갈색
        }
        
        self.labels_kr = {
            'BUILDING': '건물',
            'ROAD': '도로',
            'WATER': '물',
            'FOREST': '숲',
            'TREE': '나무',
            'GRASS': '초지',
            'WETLAND': '습지',
            'SOIL': '토양'
        }
    
    def create_professional_pie_chart(
        self,
        areas: Dict,
        save_path: str,
        title: str = "식생 타입별 면적 비율"
    ) -> str:
        """전문적인 파이 차트 생성"""
        
        fig, ax = plt.subplots(figsize=(10, 8), facecolor='white')
        
        # 데이터 준비
        labels = []
        sizes = []
        colors_list = []
        
        for veg_type, data in areas.items():
            if data['ratio_percent'] > 0.1:  # 0.1% 이상만 표시
                labels.append(self.labels_kr.get(veg_type, veg_type))
                sizes.append(data['ratio_percent'])
                colors_list.append(self.colors.get(veg_type, '#95A5A6'))
        
        # 파이 차트 생성
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            autopct='%1.1f%%',
            startangle=90,
            colors=colors_list,
            textprops={'fontsize': 11, 'weight': 'bold'},
            pctdistance=0.85
        )
        
        # 텍스트 스타일 개선
        for text in texts:
            text.set_fontsize(12)
            text.set_weight('bold')
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(10)
            autotext.set_weight('bold')
        
        # 제목
        ax.set_title(title, fontsize=16, weight='bold', pad=20)
        
        # 정원 그리기 (도넛 차트 효과)
        centre_circle = plt.Circle((0, 0), 0.70, fc='white')
        ax.add_artist(centre_circle)
        
        ax.axis('equal')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return save_path
    
    def create_professional_bar_chart(
        self,
        areas: Dict,
        save_path: str,
        title: str = "식생 타입별 면적 비율"
    ) -> str:
        """전문적인 가로 막대 차트 생성"""
        
        fig, ax = plt.subplots(figsize=(10, 8), facecolor='white')
        
        # 데이터 준비
        labels = []
        sizes = []
        colors_list = []
        
        for veg_type, data in areas.items():
            labels.append(self.labels_kr.get(veg_type, veg_type))
            sizes.append(data['ratio_percent'])
            colors_list.append(self.colors.get(veg_type, '#95A5A6'))
        
        # 정렬 (비율 높은 순)
        sorted_data = sorted(zip(labels, sizes, colors_list), key=lambda x: x[1], reverse=True)
        labels, sizes, colors_list = zip(*sorted_data)
        
        y_pos = np.arange(len(labels))
        
        # 막대 그래프
        bars = ax.barh(y_pos, sizes, color=colors_list, height=0.7, edgecolor='white', linewidth=2)
        
        # 막대 끝에 값 표시
        for i, (bar, size) in enumerate(zip(bars, sizes)):
            width = bar.get_width()
            ax.text(
                width + 0.5,
                bar.get_y() + bar.get_height() / 2,
                f'{size:.1f}%',
                ha='left',
                va='center',
                fontsize=11,
                weight='bold'
            )
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels, fontsize=12, weight='bold')
        ax.invert_yaxis()
        
        ax.set_xlabel('비율 (%)', fontsize=12, weight='bold')
        ax.set_title(title, fontsize=16, weight='bold', pad=20)
        
        # 그리드 스타일
        ax.grid(axis='x', alpha=0.3, linestyle='--', linewidth=0.7)
        ax.set_axisbelow(True)
        
        # 테두리 제거
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return save_path
    
    def create_carbon_chart(
        self,
        carbon_data: Dict,
        save_path: str,
        title: str = "식생 타입별 탄소흡수량"
    ) -> str:
        """탄소흡수량 막대 차트"""
        
        fig, ax = plt.subplots(figsize=(10, 6), facecolor='white')
        
        # 식생 타입만 필터링 (건물, 도로 제외)
        vegetation_types = ['FOREST', 'TREE', 'GRASS', 'WETLAND', 'WATER', 'SOIL']
        
        labels = []
        values = []
        colors_list = []
        
        for veg_type in vegetation_types:
            if veg_type in carbon_data['by_type'] and carbon_data['by_type'][veg_type] > 0:
                labels.append(self.labels_kr.get(veg_type, veg_type))
                values.append(carbon_data['by_type'][veg_type])
                colors_list.append(self.colors.get(veg_type, '#95A5A6'))
        
        if not values:
            # 데이터가 없으면 빈 차트
            ax.text(0.5, 0.5, '탄소흡수 데이터 없음', ha='center', va='center', fontsize=14)
            plt.tight_layout()
            plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            return save_path
        
        x_pos = np.arange(len(labels))
        
        # 막대 그래프
        bars = ax.bar(x_pos, values, color=colors_list, width=0.6, edgecolor='white', linewidth=2)
        
        # 막대 위에 값 표시
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height + max(values) * 0.02,
                f'{value:.2f}',
                ha='center',
                va='bottom',
                fontsize=10,
                weight='bold'
            )
        
        ax.set_xticks(x_pos)
        ax.set_xticklabels(labels, fontsize=11, weight='bold')
        ax.set_ylabel('탄소흡수량 (tCO₂/yr)', fontsize=12, weight='bold')
        ax.set_title(title, fontsize=16, weight='bold', pad=20)
        
        # 그리드
        ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.7)
        ax.set_axisbelow(True)
        
        # 테두리
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return save_path

