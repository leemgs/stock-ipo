#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IPO Stock Short-Term Trading Analysis Program
공모주 청약 단타 수익 분석 프로그램

This program analyzes IPO stocks for same-day trading opportunities,
evaluating suitability based on multiple criteria and providing
optimal sell timing recommendations.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple
from datetime import date
from enum import Enum
import sys

# UTF-8 출력 보장
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')


class SuitabilityStatus(Enum):
    """단타 적합성 상태"""
    SUITABLE = "단타 적합"
    UNSUITABLE = "단타 부적합"


@dataclass
class IPOStock:
    """공모주 정보"""
    name: str  # 종목명
    listing_date: date  # 상장일
    ipo_price: int  # 공모가 (원)
    price_band_min: int  # 희망 공모가 하단 (원)
    price_band_max: int  # 희망 공모가 상단 (원)
    mandatory_holding_pct: float  # 의무보유확약 비율 (%)
    available_float_pct: float  # 유통가능물량 비율 (%)
    sector: str  # 업종
    sector_avg_return_pct: float  # 유사 업종 상장일 평균 수익률 (%)
    expected_return_pct: float  # 예상 수익률 (%)
    strengths: List[str]  # 장점
    weaknesses: List[str]  # 단점


@dataclass
class SuitabilityEvaluation:
    """단타 적합성 평가 결과"""
    stock: IPOStock
    status: SuitabilityStatus
    reasons: List[str]
    warnings: List[str]


@dataclass
class SellTiming:
    """매도 타이밍 정보"""
    stock_name: str
    dangerous_period: str  # 가장 불리한 구간
    safe_period: str  # 가장 안전한 매도 타이밍
    reason: str  # 근거


class IPOAnalyzer:
    """공모주 단타 분석기"""
    
    # 단타 적합성 기준
    MIN_MANDATORY_HOLDING = 10.0  # 의무보유확약 최소 기준 (%)
    MAX_AVAILABLE_FLOAT = 35.0  # 유통가능물량 최대 기준 (%)
    MIN_SECTOR_RETURN = 5.0  # 유사 업종 최소 수익률 기준 (%)
    TARGET_MIN_RETURN = 5.0  # 목표 최소 수익률 (%)
    TARGET_MAX_RETURN = 30.0  # 목표 최대 수익률 (%)
    
    def __init__(self, stocks: List[IPOStock]):
        self.stocks = stocks
    
    def evaluate_suitability(self, stock: IPOStock) -> SuitabilityEvaluation:
        """
        단타 적합성 평가
        
        부적합 조건:
        - 의무보유확약 < 10%
        - 유통가능물량 > 35%
        - 공모가가 밴드 최상단 초과
        - 유사 업종 상장일 평균 수익률 < 5%
        """
        reasons = []
        warnings = []
        status = SuitabilityStatus.SUITABLE
        
        # 1. 의무보유확약 체크
        if stock.mandatory_holding_pct < self.MIN_MANDATORY_HOLDING:
            status = SuitabilityStatus.UNSUITABLE
            reasons.append(
                f"의무보유확약 {stock.mandatory_holding_pct}% (기준: {self.MIN_MANDATORY_HOLDING}% 이상)"
            )
        
        # 2. 유통가능물량 체크
        if stock.available_float_pct > self.MAX_AVAILABLE_FLOAT:
            status = SuitabilityStatus.UNSUITABLE
            reasons.append(
                f"유통가능물량 {stock.available_float_pct}% (기준: {self.MAX_AVAILABLE_FLOAT}% 이하)"
            )
        
        # 3. 공모가 밴드 체크
        if stock.ipo_price > stock.price_band_max:
            status = SuitabilityStatus.UNSUITABLE
            reasons.append(
                f"공모가 {stock.ipo_price:,}원이 밴드 최상단 {stock.price_band_max:,}원 초과"
            )
        
        # 4. 유사 업종 평균 수익률 체크
        if stock.sector_avg_return_pct < self.MIN_SECTOR_RETURN:
            status = SuitabilityStatus.UNSUITABLE
            reasons.append(
                f"유사 업종({stock.sector}) 평균 수익률 {stock.sector_avg_return_pct}% "
                f"(기준: {self.MIN_SECTOR_RETURN}% 이상)"
            )
        
        # 적합 종목에 대한 긍정 정보
        if status == SuitabilityStatus.SUITABLE:
            reasons.append(
                f"의무보유확약 {stock.mandatory_holding_pct}% (우수)"
            )
            reasons.append(
                f"유통가능물량 {stock.available_float_pct}% (양호)"
            )
            reasons.append(
                f"유사 업종 평균 수익률 {stock.sector_avg_return_pct}% (양호)"
            )
            reasons.append(
                f"예상 수익률 {stock.expected_return_pct}% (목표 범위: {self.TARGET_MIN_RETURN}~{self.TARGET_MAX_RETURN}%)"
            )
            
            # 적합하지만 주의가 필요한 사항들
            if stock.available_float_pct > 30.0:
                warnings.append(f"유통가능물량이 {stock.available_float_pct}%로 다소 높은 편이므로 주의 필요")
            if stock.ipo_price > (stock.price_band_min + stock.price_band_max) / 2:
                warnings.append(f"공모가가 희망 밴드 상단에 근접하여 변동성 증가 가능")
            if stock.expected_return_pct > 20.0:
                warnings.append(f"예상 수익률 {stock.expected_return_pct}%로 높아 변동성 클 수 있음")
        
        return SuitabilityEvaluation(
            stock=stock,
            status=status,
            reasons=reasons,
            warnings=warnings
        )
    
    def get_sell_timing(self, stock: IPOStock) -> SellTiming:
        """
        상장일 매도 타이밍 추천
        
        기본 전략:
        - 수급이 강한 종목: 09:30~10:30 초반 급등 후 매도
        - 수급이 약한 종목: 09:00~09:30 조기 매도
        - 불리한 구간: 장 마감 전 (14:30~15:20) - 물량 출회 위험
        """
        # 수급 강도 판단 (의무보유확약이 높고 유통가능물량이 낮을수록 강함)
        supply_strength = stock.mandatory_holding_pct - (stock.available_float_pct / 2)
        
        if supply_strength > 15:  # 강한 수급
            dangerous_period = "14:30~15:20 (장 마감 전 차익실현 물량 출회 위험)"
            safe_period = "09:30~10:30 (초반 급등 후 첫 고점)"
            reason = (
                f"의무보유확약 {stock.mandatory_holding_pct}%로 높고 "
                f"유통가능물량 {stock.available_float_pct}%로 낮아 초반 수급 유리. "
                f"예상 수익률 {stock.expected_return_pct}% 달성 시 즉시 매도 권장."
            )
        elif supply_strength > 5:  # 중간 수급
            dangerous_period = "10:30~11:00, 14:00~15:20 (수급 약화 및 차익실현 구간)"
            safe_period = "09:15~09:45 (시초가 형성 직후)"
            reason = (
                f"중간 수준의 수급. 시초가 형성 직후 빠른 매도가 안전. "
                f"목표가 {stock.expected_return_pct}% 도달 시 분할 매도 권장."
            )
        else:  # 약한 수급
            dangerous_period = "09:30 이후 전 구간 (수급 약화로 지속적 하락 위험)"
            safe_period = "09:00~09:20 (시초가 형성 즉시)"
            reason = (
                f"수급이 약해 조기 매도 필수. "
                f"시초가에서 {stock.expected_return_pct}% 이상 시 즉시 매도, "
                f"미달 시에도 손절 고려."
            )
        
        return SellTiming(
            stock_name=stock.name,
            dangerous_period=dangerous_period,
            safe_period=safe_period,
            reason=reason
        )
    
    def select_suitable_stocks(self) -> List[IPOStock]:
        """단타 적합 종목 선정"""
        suitable = []
        for stock in self.stocks:
            evaluation = self.evaluate_suitability(stock)
            if evaluation.status == SuitabilityStatus.SUITABLE:
                suitable.append(stock)
        # 예상 수익률 기준 내림차순 정렬
        return sorted(suitable, key=lambda s: s.expected_return_pct, reverse=True)
    
    def generate_report(self) -> str:
        """분석 보고서 생성"""
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("공모주 IPO 단타 분석 보고서")
        report_lines.append("=" * 80)
        report_lines.append("")
        
        # 1. 종목 선정
        report_lines.append("■ 1. 2026년 1~2월 공모주 중 단타 적합 종목 선정")
        report_lines.append("-" * 80)
        
        suitable_stocks = self.select_suitable_stocks()
        
        if suitable_stocks:
            for idx, stock in enumerate(suitable_stocks, 1):
                report_lines.append(f"\n[{idx}] {stock.name}")
                report_lines.append(f"  상장일: {stock.listing_date.strftime('%Y년 %m월 %d일')}")
                report_lines.append(f"  공모가: {stock.ipo_price:,}원 (밴드: {stock.price_band_min:,}~{stock.price_band_max:,}원)")
                report_lines.append(f"  예상 수익률: +{stock.expected_return_pct}%")
                report_lines.append(f"  업종: {stock.sector}")
                report_lines.append("")
                report_lines.append("  [장점]")
                for strength in stock.strengths:
                    report_lines.append(f"    • {strength}")
                report_lines.append("")
                report_lines.append("  [단점]")
                for weakness in stock.weaknesses:
                    report_lines.append(f"    • {weakness}")
        else:
            report_lines.append("\n  ⚠ 현재 단타 적합 종목이 없습니다.")
        
        # 2. 단타 적합성 판단
        report_lines.append("\n\n■ 2. 단타 적합성 판단")
        report_lines.append("-" * 80)
        report_lines.append(f"\n목표: 상장일 기준 +{self.TARGET_MIN_RETURN}~{self.TARGET_MAX_RETURN}% 수익")
        report_lines.append("\n[부적합 기준 - 하나라도 해당 시 부적합]")
        report_lines.append(f"  • 의무보유확약 < {self.MIN_MANDATORY_HOLDING}%")
        report_lines.append(f"  • 유통가능물량 > {self.MAX_AVAILABLE_FLOAT}%")
        report_lines.append(f"  • 공모가 밴드 최상단 초과")
        report_lines.append(f"  • 유사 업종 상장일 평균 수익률 < {self.MIN_SECTOR_RETURN}%")
        report_lines.append("")
        
        for stock in self.stocks:
            evaluation = self.evaluate_suitability(stock)
            status_mark = "✓" if evaluation.status == SuitabilityStatus.SUITABLE else "✗"
            report_lines.append(f"\n{status_mark} {stock.name}: {evaluation.status.value}")
            for reason in evaluation.reasons:
                report_lines.append(f"    - {reason}")
            if evaluation.warnings:
                report_lines.append("  [주의사항]")
                for warning in evaluation.warnings:
                    report_lines.append(f"    ⚠ {warning}")
        
        # 3. 매도 타이밍
        report_lines.append("\n\n■ 3. 상장일 매도 타이밍 (오늘 상장 기준)")
        report_lines.append("-" * 80)
        
        for stock in suitable_stocks:
            timing = self.get_sell_timing(stock)
            report_lines.append(f"\n[{timing.stock_name}]")
            report_lines.append(f"  ⚠ 가장 불리한 구간: {timing.dangerous_period}")
            report_lines.append(f"  ✓ 가장 안전한 매도 타이밍: {timing.safe_period}")
            report_lines.append(f"  → 근거: {timing.reason}")
        
        report_lines.append("\n" + "=" * 80)
        report_lines.append("※ 본 분석은 과거 데이터와 수급 구조 기반 판단이며,")
        report_lines.append("   실제 시장 상황에 따라 달라질 수 있습니다.")
        report_lines.append("=" * 80)
        
        return "\n".join(report_lines)


def create_sample_ipo_data() -> List[IPOStock]:
    """2026년 1~2월 예시 공모주 데이터"""
    return [
        IPOStock(
            name="테크이노베이션",
            listing_date=date(2026, 1, 15),
            ipo_price=25000,
            price_band_min=23000,
            price_band_max=27000,
            mandatory_holding_pct=15.5,
            available_float_pct=28.3,
            sector="반도체",
            sector_avg_return_pct=12.8,
            expected_return_pct=18.5,
            strengths=[
                "의무보유확약 15.5%로 높은 편",
                "반도체 업종 평균 수익률 12.8%로 우수",
                "공모가가 희망 밴드 중간 수준으로 적정",
                "최근 반도체 섹터 강세"
            ],
            weaknesses=[
                "유통가능물량 28.3%로 다소 높은 편",
                "경쟁사 대비 기술력 검증 필요",
                "글로벌 반도체 수급 변동성 존재"
            ]
        ),
        IPOStock(
            name="바이오헬스케어",
            listing_date=date(2026, 1, 22),
            ipo_price=18000,
            price_band_min=15000,
            price_band_max=20000,
            mandatory_holding_pct=22.0,
            available_float_pct=18.5,
            sector="바이오",
            sector_avg_return_pct=15.2,
            expected_return_pct=25.0,
            strengths=[
                "의무보유확약 22%로 매우 높음",
                "유통가능물량 18.5%로 낮아 수급 유리",
                "바이오 섹터 최근 상승세",
                "신약 파이프라인 임상 3상 진행 중"
            ],
            weaknesses=[
                "공모가가 밴드 상단에 근접",
                "임상 결과 불확실성",
                "바이오 업종 변동성 높음"
            ]
        ),
        IPOStock(
            name="그린에너지솔루션",
            listing_date=date(2026, 2, 5),
            ipo_price=32000,
            price_band_min=28000,
            price_band_max=32000,
            mandatory_holding_pct=8.5,
            available_float_pct=42.0,
            sector="신재생에너지",
            sector_avg_return_pct=6.5,
            expected_return_pct=8.0,
            strengths=[
                "신재생에너지 정책 수혜 기대",
                "해외 수출 비중 높음"
            ],
            weaknesses=[
                "의무보유확약 8.5%로 매우 낮음 (부적합)",
                "유통가능물량 42%로 과다 (부적합)",
                "공모가가 밴드 최상단 (부적합)",
                "원자재 가격 상승 리스크"
            ]
        ),
        IPOStock(
            name="AI로보틱스",
            listing_date=date(2026, 2, 12),
            ipo_price=45000,
            price_band_min=40000,
            price_band_max=50000,
            mandatory_holding_pct=18.0,
            available_float_pct=25.0,
            sector="AI/로봇",
            sector_avg_return_pct=3.2,
            expected_return_pct=5.5,
            strengths=[
                "의무보유확약 18%로 높음",
                "유통가능물량 25%로 적정",
                "AI 기술 경쟁력 보유",
                "대기업 협력 관계"
            ],
            weaknesses=[
                "유사 업종 평균 수익률 3.2%로 낮음 (부적합)",
                "최근 AI 섹터 조정 국면",
                "수익성 개선 지연"
            ]
        ),
        IPOStock(
            name="스마트모빌리티",
            listing_date=date(2026, 2, 19),
            ipo_price=22000,
            price_band_min=20000,
            price_band_max=24000,
            mandatory_holding_pct=12.5,
            available_float_pct=32.0,
            sector="전기차/모빌리티",
            sector_avg_return_pct=9.5,
            expected_return_pct=12.0,
            strengths=[
                "전기차 시장 성장세",
                "의무보유확약 12.5%로 기준 충족",
                "유통가능물량 32%로 기준 충족",
                "유사 업종 수익률 9.5%로 양호"
            ],
            weaknesses=[
                "유통가능물량이 다소 높은 편",
                "경쟁 심화",
                "배터리 가격 변동 리스크"
            ]
        )
    ]


def main():
    """메인 실행 함수"""
    # 샘플 데이터 생성
    ipo_stocks = create_sample_ipo_data()
    
    # 분석기 생성
    analyzer = IPOAnalyzer(ipo_stocks)
    
    # 보고서 생성 및 출력
    report = analyzer.generate_report()
    print(report)
    
    # 결과를 파일로 저장
    output_file = "ipo_analysis_report.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"\n\n✓ 분석 보고서가 '{output_file}' 파일로 저장되었습니다.")


if __name__ == "__main__":
    main()
