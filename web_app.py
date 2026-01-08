#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IPO Analyzer Web Application
웹 기반 공모주 분석 도구
"""

from flask import Flask, render_template, request, jsonify
from datetime import date, datetime
from ipo_analyzer import IPOStock, IPOAnalyzer, create_sample_ipo_data
import os
import sys
import json as json_module

# UTF-8 인코딩 강제 설정
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

app = Flask(__name__)

# Flask JSON 인코딩 설정: UTF-8로 한글이 깨지지 않도록 설정
# ensure_ascii=False로 설정하여 유니코드 이스케이프 방지
app.json.ensure_ascii = False
app.json.sort_keys = False

# 템플릿 디렉토리가 없으면 생성
if not os.path.exists('templates'):
    os.makedirs('templates')


@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """분석 실행 API"""
    try:
        # Validate request has JSON body
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': '유효하지 않은 요청입니다.'
            }), 400
        
        # 샘플 데이터 사용 또는 사용자 데이터 사용
        use_sample = request.json.get('use_sample', True)
        
        if use_sample:
            stocks = create_sample_ipo_data()
        else:
            # 사용자가 입력한 데이터로 IPOStock 생성
            stocks_data = request.json.get('stocks', [])
            stocks = []
            for stock_data in stocks_data:
                stock = IPOStock(
                    name=stock_data['name'],
                    listing_date=datetime.strptime(stock_data['listing_date'], '%Y-%m-%d').date(),
                    ipo_price=int(stock_data['ipo_price']),
                    price_band_min=int(stock_data['price_band_min']),
                    price_band_max=int(stock_data['price_band_max']),
                    mandatory_holding_pct=float(stock_data['mandatory_holding_pct']),
                    available_float_pct=float(stock_data['available_float_pct']),
                    sector=stock_data['sector'],
                    sector_avg_return_pct=float(stock_data['sector_avg_return_pct']),
                    expected_return_pct=float(stock_data['expected_return_pct']),
                    strengths=stock_data.get('strengths', []),
                    weaknesses=stock_data.get('weaknesses', [])
                )
                stocks.append(stock)
        
        # 분석 실행
        analyzer = IPOAnalyzer(stocks)
        
        # 적합 종목 선정
        suitable_stocks = analyzer.select_suitable_stocks()
        
        # 모든 종목 평가
        all_evaluations = []
        for stock in stocks:
            evaluation = analyzer.evaluate_suitability(stock)
            timing = analyzer.get_sell_timing(stock) if evaluation.status.value == "단타 적합" else None
            
            all_evaluations.append({
                'name': stock.name,
                'listing_date': stock.listing_date.strftime('%Y년 %m월 %d일'),
                'ipo_price': stock.ipo_price,
                'price_band': f"{stock.price_band_min:,}~{stock.price_band_max:,}원",
                'expected_return': stock.expected_return_pct,
                'sector': stock.sector,
                'status': evaluation.status.value,
                'reasons': evaluation.reasons,
                'warnings': evaluation.warnings,
                'strengths': stock.strengths,
                'weaknesses': stock.weaknesses,
                'timing': {
                    'safe_period': timing.safe_period if timing else None,
                    'dangerous_period': timing.dangerous_period if timing else None,
                    'reason': timing.reason if timing else None
                } if timing else None
            })
        
        # 적합 종목만 추출
        suitable_evaluations = [e for e in all_evaluations if e['status'] == '단타 적합']
        unsuitable_evaluations = [e for e in all_evaluations if e['status'] == '단타 부적합']
        
        return jsonify({
            'success': True,
            'suitable_count': len(suitable_evaluations),
            'total_count': len(all_evaluations),
            'suitable_stocks': suitable_evaluations,
            'unsuitable_stocks': unsuitable_evaluations
        })
        
    except Exception as e:
        # Log the error for debugging but don't expose details to user
        app.logger.error(f"Analysis error: {str(e)}")
        return jsonify({
            'success': False,
            'error': '분석 중 오류가 발생했습니다. 입력 데이터를 확인해주세요.'
        }), 400


@app.route('/api/sample-data', methods=['GET'])
def get_sample_data():
    """샘플 데이터 반환"""
    stocks = create_sample_ipo_data()
    sample_data = []
    
    for stock in stocks:
        sample_data.append({
            'name': stock.name,
            'listing_date': stock.listing_date.strftime('%Y-%m-%d'),
            'ipo_price': stock.ipo_price,
            'price_band_min': stock.price_band_min,
            'price_band_max': stock.price_band_max,
            'mandatory_holding_pct': stock.mandatory_holding_pct,
            'available_float_pct': stock.available_float_pct,
            'sector': stock.sector,
            'sector_avg_return_pct': stock.sector_avg_return_pct,
            'expected_return_pct': stock.expected_return_pct,
            'strengths': stock.strengths,
            'weaknesses': stock.weaknesses
        })
    
    return jsonify({
        'success': True,
        'stocks': sample_data
    })


if __name__ == '__main__':
    print("=" * 80)
    print("공모주 IPO 단타 분석 웹 애플리케이션")
    print("=" * 80)
    print("\n웹 브라우저에서 다음 주소로 접속하세요:")
    print("  http://localhost:5701")
    print("\n종료하려면 Ctrl+C를 누르세요.\n")
    print("=" * 80)
    print("\n⚠️  주의: 이 서버는 개발용입니다. 실제 운영 환경에서는 사용하지 마세요.")
    print("   운영 환경에서는 Gunicorn, uWSGI 등의 WSGI 서버를 사용하세요.\n")
    
    # Get debug mode from environment variable, default to True for development
    import os
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    app.run(debug=debug_mode, host='0.0.0.0', port=5701)
