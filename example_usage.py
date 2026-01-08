#!/usr/bin/env python3
"""
Example: How to use the IPO Analyzer with custom stock data
"""

from datetime import date
from ipo_analyzer import IPOStock, IPOAnalyzer


def example_custom_analysis():
    """커스텀 공모주 데이터로 분석하는 예제"""
    
    # 1. 새로운 공모주 데이터 추가
    my_ipo_stocks = [
        IPOStock(
            name="예시기업A",
            listing_date=date(2026, 1, 20),
            ipo_price=30000,
            price_band_min=28000,
            price_band_max=32000,
            mandatory_holding_pct=20.0,  # 의무보유확약 20%
            available_float_pct=25.0,    # 유통가능물량 25%
            sector="IT서비스",
            sector_avg_return_pct=10.0,  # 유사 업종 평균 10%
            expected_return_pct=15.0,    # 예상 수익률 15%
            strengths=[
                "강점 1",
                "강점 2",
                "강점 3"
            ],
            weaknesses=[
                "약점 1",
                "약점 2"
            ]
        ),
        # 더 많은 종목을 추가할 수 있습니다...
    ]
    
    # 2. 분석기 생성
    analyzer = IPOAnalyzer(my_ipo_stocks)
    
    # 3. 개별 종목 적합성 평가
    print("=== 개별 종목 평가 ===")
    for stock in my_ipo_stocks:
        evaluation = analyzer.evaluate_suitability(stock)
        print(f"\n{stock.name}: {evaluation.status.value}")
        print("근거:")
        for reason in evaluation.reasons:
            print(f"  - {reason}")
        if evaluation.warnings:
            print("주의사항:")
            for warning in evaluation.warnings:
                print(f"  ⚠ {warning}")
    
    # 4. 적합 종목만 선정
    print("\n\n=== 단타 적합 종목 목록 ===")
    suitable_stocks = analyzer.select_suitable_stocks()
    for idx, stock in enumerate(suitable_stocks, 1):
        print(f"{idx}. {stock.name} (예상수익: +{stock.expected_return_pct}%)")
    
    # 5. 매도 타이밍 확인
    print("\n\n=== 매도 타이밍 ===")
    for stock in suitable_stocks:
        timing = analyzer.get_sell_timing(stock)
        print(f"\n[{timing.stock_name}]")
        print(f"안전한 매도 타이밍: {timing.safe_period}")
        print(f"위험한 구간: {timing.dangerous_period}")
        print(f"근거: {timing.reason}")
    
    # 6. 전체 보고서 생성
    print("\n\n" + "="*60)
    print("전체 보고서를 생성하려면 analyzer.generate_report()를 사용하세요")
    print("="*60)


if __name__ == "__main__":
    example_custom_analysis()
