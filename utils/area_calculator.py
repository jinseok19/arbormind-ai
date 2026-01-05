"""면적 계산 모듈"""

import numpy as np
from typing import Dict, Optional


class AreaCalculator:
    """면적 계산 클래스"""
    
    @staticmethod
    def calculate_pixel_ratios(masks: Dict[str, np.ndarray]) -> Dict[str, float]:
        """
        픽셀 비율 계산
        
        Args:
            masks: 타입별 마스크 딕셔너리
        
        Returns:
            타입별 비율 딕셔너리 (0~1)
        """
        total_pixels = masks[list(masks.keys())[0]].size
        ratios = {}
        
        for veg_type, mask in masks.items():
            pixel_count = np.count_nonzero(mask)
            ratios[veg_type] = pixel_count / total_pixels
        
        return ratios
    
    @staticmethod
    def calculate_areas(
        ratios: Dict[str, float],
        total_area_m2: Optional[float] = None
    ) -> Dict[str, Dict[str, float]]:
        """
        면적 계산
        
        Args:
            ratios: 타입별 비율
            total_area_m2: 총 면적 (㎡)
        
        Returns:
            타입별 면적 및 비율 정보
        """
        results = {}
        
        for veg_type, ratio in ratios.items():
            results[veg_type] = {
                'ratio': ratio,
                'ratio_percent': ratio * 100,
                'area_m2': total_area_m2 * ratio if total_area_m2 else None
            }
        
        return results
    
    @staticmethod
    def validate_ratios(ratios: Dict[str, float], tolerance: float = 0.01) -> bool:
        """
        비율 합계 검증
        
        Args:
            ratios: 타입별 비율
            tolerance: 허용 오차
        
        Returns:
            검증 통과 여부
        """
        total = sum(ratios.values())
        return abs(total - 1.0) <= tolerance
    
    @staticmethod
    def get_vegetation_area(results: Dict[str, Dict]) -> Optional[float]:
        """
        식생 면적 합계 (NONVEG 제외)
        
        Args:
            results: calculate_areas 결과
        
        Returns:
            식생 면적 합계 (㎡)
        """
        veg_area = 0
        has_area = False
        
        for veg_type, data in results.items():
            if veg_type != 'NONVEG' and data['area_m2'] is not None:
                veg_area += data['area_m2']
                has_area = True
        
        return veg_area if has_area else None

