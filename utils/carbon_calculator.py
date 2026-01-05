"""탄소흡수량 계산 모듈"""

import pandas as pd
from typing import Dict, Optional
from pathlib import Path


class CarbonCalculator:
    """탄소흡수량 계산 클래스"""
    
    def __init__(self, coefficients_path: str = "data/carbon_coefficients.csv"):
        """
        초기화
        
        Args:
            coefficients_path: 탄소 계수 CSV 파일 경로
        """
        self.coefficients_path = Path(coefficients_path)
        self.coefficients = self._load_coefficients()
    
    def _load_coefficients(self) -> Dict[str, Dict]:
        """탄소 계수 로드"""
        if not self.coefficients_path.exists():
            raise FileNotFoundError(f"계수 파일을 찾을 수 없습니다: {self.coefficients_path}")
        
        df = pd.read_csv(self.coefficients_path)
        
        coefficients = {}
        for _, row in df.iterrows():
            coefficients[row['vegetation_type']] = {
                'coef_kgco2_m2_yr': row['coef_kgco2_m2_yr'],
                'source_name': row['source_name'],
                'version': row['version']
            }
        
        return coefficients
    
    def calculate_carbon(
        self,
        areas: Dict[str, Dict[str, float]]
    ) -> Dict[str, any]:
        """
        탄소흡수량 계산
        
        Args:
            areas: 타입별 면적 정보 (AreaCalculator.calculate_areas 결과)
        
        Returns:
            탄소흡수량 결과
        """
        # 면적이 없으면 계산 불가
        if not any(data.get('area_m2') for data in areas.values()):
            return {
                'total_tco2_yr': None,
                'by_type': {},
                'coefficients_used': {},
                'method': 'sum(area_m2 * coef_kgco2_m2_yr) / 1000'
            }
        
        carbon_by_type = {}
        coefficients_used = {}
        total_carbon_kg = 0
        
        for veg_type, area_data in areas.items():
            # NONVEG는 제외
            if veg_type == 'NONVEG':
                carbon_by_type[veg_type] = 0.0
                continue
            
            # 계수가 없으면 스킵
            if veg_type not in self.coefficients:
                continue
            
            area_m2 = area_data.get('area_m2')
            if area_m2 is None:
                continue
            
            # 계수 가져오기
            coef_data = self.coefficients[veg_type]
            coef = coef_data['coef_kgco2_m2_yr']
            
            # 탄소흡수량 계산 (kgCO2/yr)
            carbon_kg = area_m2 * coef
            total_carbon_kg += carbon_kg
            
            # tCO2/yr로 변환
            carbon_by_type[veg_type] = carbon_kg / 1000
            
            # 사용된 계수 기록
            coefficients_used[veg_type] = coef_data
        
        return {
            'total_tco2_yr': round(total_carbon_kg / 1000, 2),
            'by_type': carbon_by_type,
            'coefficients_used': coefficients_used,
            'method': 'sum(area_m2 * coef_kgco2_m2_yr) / 1000'
        }
    
    def get_coefficient_info(self, veg_type: str) -> Optional[Dict]:
        """특정 식생 타입의 계수 정보 조회"""
        return self.coefficients.get(veg_type)
    
    def get_all_coefficients(self) -> Dict[str, Dict]:
        """모든 계수 정보 조회"""
        return self.coefficients.copy()

