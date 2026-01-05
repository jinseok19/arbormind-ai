"""이미지 처리 모듈"""

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from typing import Tuple, Dict


class ImageProcessor:
    """이미지 전처리 및 세그멘테이션 클래스"""
    
    def __init__(self):
        self.target_size = (1024, 1024)
    
    def load_image(self, image_path: str) -> np.ndarray:
        """이미지 로드"""
        img = cv2.imread(image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img
    
    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """이미지 전처리"""
        # 리사이즈
        image = cv2.resize(image, self.target_size, interpolation=cv2.INTER_LINEAR)
        return image
    
    def segment_vegetation(self, image: np.ndarray) -> Dict[str, np.ndarray]:
        """
        식생 타입 세그멘테이션 (개선 버전)
        
        분류: FOREST(숲), TREE(나무), GRASS(초지), WETLAND(습지), 
              WATER(물), BUILDING(건물), ROAD(도로), SOIL(토양)
        
        TODO: 실제 AI 모델로 교체 필요
        현재는 개선된 컬러 기반 분류 사용
        """
        # RGB 이미지 준비
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        
        # HSV 변환
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        
        # LAB 변환 (색상 구분에 더 좋음)
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        
        # 그레이스케일
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # 1. BUILDING (건물): 밝은 회색/흰색/청록색 지붕
        # 채도가 낮고 밝기가 높은 영역
        mask_building_1 = cv2.inRange(hsv, np.array([0, 0, 180]), np.array([180, 50, 255]))
        # 청록색 지붕
        mask_building_2 = cv2.inRange(hsv, np.array([80, 100, 100]), np.array([100, 255, 255]))
        mask_building = cv2.bitwise_or(mask_building_1, mask_building_2)
        
        # 2. ROAD (도로): 어두운 회색/검은색
        mask_road = cv2.inRange(hsv, np.array([0, 0, 0]), np.array([180, 50, 100]))
        
        # 3. WATER (물): 진한 파란색
        mask_water = cv2.inRange(hsv, np.array([90, 80, 50]), np.array([130, 255, 200]))
        
        # 4. FOREST (숲): 진한 녹색
        mask_forest = cv2.inRange(hsv, np.array([35, 70, 30]), np.array([85, 255, 150]))
        
        # 5. TREE (나무): 중간 녹색
        mask_tree = cv2.inRange(hsv, np.array([30, 40, 40]), np.array([85, 180, 200]))
        mask_tree = cv2.bitwise_and(mask_tree, cv2.bitwise_not(mask_forest))
        
        # 6. GRASS (초지): 밝은 녹색/연두색
        mask_grass = cv2.inRange(hsv, np.array([25, 30, 100]), np.array([85, 200, 255]))
        mask_grass = cv2.bitwise_and(mask_grass, cv2.bitwise_not(mask_forest))
        mask_grass = cv2.bitwise_and(mask_grass, cv2.bitwise_not(mask_tree))
        
        # 7. WETLAND (습지): 어두운 청록색
        mask_wetland = cv2.inRange(hsv, np.array([80, 30, 20]), np.array([100, 150, 100]))
        
        # 8. SOIL (토양): 갈색/베이지
        mask_soil = cv2.inRange(hsv, np.array([10, 20, 80]), np.array([30, 150, 200]))
        
        # 우선순위 적용 (겹치는 부분 제거)
        # 건물과 도로가 다른 것들보다 우선
        mask_tree = cv2.bitwise_and(mask_tree, cv2.bitwise_not(mask_building))
        mask_tree = cv2.bitwise_and(mask_tree, cv2.bitwise_not(mask_road))
        
        mask_grass = cv2.bitwise_and(mask_grass, cv2.bitwise_not(mask_building))
        mask_grass = cv2.bitwise_and(mask_grass, cv2.bitwise_not(mask_road))
        
        mask_forest = cv2.bitwise_and(mask_forest, cv2.bitwise_not(mask_building))
        mask_forest = cv2.bitwise_and(mask_forest, cv2.bitwise_not(mask_road))
        
        mask_soil = cv2.bitwise_and(mask_soil, cv2.bitwise_not(mask_building))
        mask_soil = cv2.bitwise_and(mask_soil, cv2.bitwise_not(mask_road))
        mask_soil = cv2.bitwise_and(mask_soil, cv2.bitwise_not(mask_grass))
        mask_soil = cv2.bitwise_and(mask_soil, cv2.bitwise_not(mask_tree))
        mask_soil = cv2.bitwise_and(mask_soil, cv2.bitwise_not(mask_forest))
        
        mask_water = cv2.bitwise_and(mask_water, cv2.bitwise_not(mask_building))
        
        # 노이즈 제거 (작은 점들 제거)
        kernel = np.ones((3, 3), np.uint8)
        mask_building = cv2.morphologyEx(mask_building, cv2.MORPH_OPEN, kernel)
        mask_road = cv2.morphologyEx(mask_road, cv2.MORPH_OPEN, kernel)
        mask_forest = cv2.morphologyEx(mask_forest, cv2.MORPH_OPEN, kernel)
        mask_tree = cv2.morphologyEx(mask_tree, cv2.MORPH_OPEN, kernel)
        mask_grass = cv2.morphologyEx(mask_grass, cv2.MORPH_OPEN, kernel)
        
        return {
            'BUILDING': mask_building,
            'ROAD': mask_road,
            'WATER': mask_water,
            'FOREST': mask_forest,
            'TREE': mask_tree,
            'GRASS': mask_grass,
            'WETLAND': mask_wetland,
            'SOIL': mask_soil
        }
    
    def create_overlay(
        self,
        original_image: np.ndarray,
        masks: Dict[str, np.ndarray],
        alpha: float = 0.5
    ) -> np.ndarray:
        """오버레이 이미지 생성"""
        
        # 컬러 정의 (RGB) - 명확한 구분을 위한 대비색
        colors = {
            'BUILDING': (255, 100, 100),   # 연한 빨강 (건물)
            'ROAD': (64, 64, 64),          # 어두운 회색 (도로)
            'WATER': (0, 128, 255),        # 파란색 (물)
            'FOREST': (0, 100, 0),         # 진한 녹색 (숲)
            'TREE': (34, 139, 34),         # 녹색 (나무)
            'GRASS': (144, 238, 144),      # 연한 녹색 (초지)
            'WETLAND': (0, 191, 191),      # 청록색 (습지)
            'SOIL': (160, 82, 45)          # 갈색 (토양)
        }
        
        overlay = original_image.copy()
        
        # 우선순위대로 적용 (나중에 그려질수록 위에 표시)
        priority_order = ['SOIL', 'GRASS', 'WETLAND', 'TREE', 'FOREST', 'WATER', 'ROAD', 'BUILDING']
        
        for veg_type in priority_order:
            if veg_type in masks and veg_type in colors:
                mask = masks[veg_type]
                color = colors[veg_type]
                # 마스크 영역에 컬러 적용
                overlay[mask > 0] = overlay[mask > 0] * (1 - alpha) + np.array(color) * alpha
        
        return overlay.astype(np.uint8)
    
    def add_legend(self, image: np.ndarray, masks: Dict[str, np.ndarray]) -> np.ndarray:
        """범례 추가 (한글 지원)"""
        
        colors = {
            'BUILDING': (255, 100, 100),
            'ROAD': (64, 64, 64),
            'WATER': (0, 128, 255),
            'FOREST': (0, 100, 0),
            'TREE': (34, 139, 34),
            'GRASS': (144, 238, 144),
            'WETLAND': (0, 191, 191),
            'SOIL': (160, 82, 45)
        }
        
        labels = {
            'BUILDING': '건물',
            'ROAD': '도로',
            'WATER': '물',
            'FOREST': '숲',
            'TREE': '나무',
            'GRASS': '초지',
            'WETLAND': '습지',
            'SOIL': '토양'
        }
        
        # 범례 영역 생성 (충분히 크게)
        legend_height = 160
        legend = np.ones((legend_height, image.shape[1], 3), dtype=np.uint8) * 255
        
        # numpy를 PIL Image로 변환 (한글 텍스트를 위해)
        legend_pil = Image.fromarray(legend)
        draw = ImageDraw.Draw(legend_pil)
        
        # 한글 폰트 로드 시도 (여러 경로)
        font = None
        font_paths = [
            "malgun.ttf",
            "malgunbd.ttf",
            "C:/Windows/Fonts/malgun.ttf",
            "C:/Windows/Fonts/malgunbd.ttf",
            "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
            "/System/Library/Fonts/AppleGothic.ttf",
        ]
        
        for font_path in font_paths:
            try:
                font = ImageFont.truetype(font_path, 18)
                break
            except:
                continue
        
        # 모든 폰트 로드 실패 시 기본 폰트
        if font is None:
            font = ImageFont.load_default()
        
        # 모든 항목을 한 줄씩 표시
        y_offset = 15
        row_height = 35
        
        all_items = ['BUILDING', 'ROAD', 'WATER', 'FOREST', 'TREE', 'GRASS', 'WETLAND', 'SOIL']
        
        # 2열로 배치
        col1_items = all_items[:4]
        col2_items = all_items[4:]
        
        # 왼쪽 열
        x_start = 30
        for i, veg_type in enumerate(col1_items):
            if veg_type in colors:
                color = colors[veg_type]
                y_pos = y_offset + i * row_height
                
                # 컬러 박스
                draw.rectangle(
                    [(x_start, y_pos), (x_start + 40, y_pos + 25)],
                    fill=color,
                    outline=(0, 0, 0),
                    width=1
                )
                
                # 라벨
                draw.text(
                    (x_start + 50, y_pos + 3),
                    labels[veg_type],
                    fill=(0, 0, 0),
                    font=font
                )
        
        # 오른쪽 열
        x_offset = image.shape[1] // 2 + 50
        for i, veg_type in enumerate(col2_items):
            if veg_type in colors:
                color = colors[veg_type]
                y_pos = y_offset + i * row_height
                
                # 컬러 박스
                draw.rectangle(
                    [(x_offset, y_pos), (x_offset + 40, y_pos + 25)],
                    fill=color,
                    outline=(0, 0, 0),
                    width=1
                )
                
                # 라벨
                draw.text(
                    (x_offset + 50, y_pos + 3),
                    labels[veg_type],
                    fill=(0, 0, 0),
                    font=font
                )
        
        # PIL을 다시 numpy로 변환
        legend = np.array(legend_pil)
        
        # 이미지와 범례 합치기
        result = np.vstack([image, legend])
        return result

