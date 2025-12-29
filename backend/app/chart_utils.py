"""차트 데이터 생성 유틸리티"""

from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

def generate_chart_data(columns: List[str], rows: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    SQL 결과를 분석하여 적절한 차트 데이터 생성
    
    Args:
        columns: 컬럼 이름 리스트
        rows: 데이터 행 리스트
        
    Returns:
        chart_data: Chart.js 형식의 차트 데이터 또는 None
    """
    if not columns or not rows or len(rows) == 0:
        return None
    
    # 컬럼 분석
    date_columns = []
    text_columns = []
    number_columns = []
    
    for col in columns:
        col_lower = col.lower()
        # 날짜/시간 컬럼 감지
        if any(keyword in col_lower for keyword in ['date', 'month', 'year', 'day', 'time', '일', '월', '년']):
            date_columns.append(col)
        # 숫자 컬럼 감지
        elif rows[0].get(col) is not None:
            val = rows[0][col]
            if isinstance(val, (int, float)):
                number_columns.append(col)
            elif isinstance(val, str):
                try:
                    float(val)
                    number_columns.append(col)
                except:
                    text_columns.append(col)
            else:
                text_columns.append(col)
        else:
            text_columns.append(col)
    
    logger.info(f"컬럼 분석 - 날짜: {date_columns}, 텍스트: {text_columns}, 숫자: {number_columns}")
    
    # 차트 생성 가능 여부 확인
    if not number_columns:
        logger.info("숫자 컬럼이 없어 차트 생성 불가")
        return None
    
    # 레이블(X축) 결정
    label_column = None
    if date_columns:
        label_column = date_columns[0]
    elif text_columns:
        label_column = text_columns[0]
    else:
        # 첫 번째 컬럼을 레이블로 사용
        label_column = columns[0]
    
    # 차트 타입 자동 선택
    chart_type = _determine_chart_type(date_columns, text_columns, number_columns, len(rows))
    
    # 레이블 추출
    labels = [str(row.get(label_column, '')) for row in rows]
    
    # 데이터셋 생성
    datasets = []
    colors = [
        'rgb(102, 126, 234)',  # 보라
        'rgb(255, 99, 132)',   # 빨강
        'rgb(75, 192, 192)',   # 청록
        'rgb(255, 159, 64)',   # 주황
        'rgb(153, 102, 255)',  # 보라
        'rgb(255, 205, 86)',   # 노랑
    ]
    
    for idx, num_col in enumerate(number_columns[:6]):  # 최대 6개 데이터셋
        data = []
        for row in rows:
            val = row.get(num_col)
            if val is None:
                data.append(0)
            elif isinstance(val, (int, float)):
                data.append(val)
            else:
                try:
                    data.append(float(val))
                except:
                    data.append(0)
        
        color = colors[idx % len(colors)]
        
        dataset = {
            'label': num_col,
            'data': data,
            'borderColor': color,
            'backgroundColor': color.replace('rgb', 'rgba').replace(')', ', 0.2)') if chart_type != 'pie' else [
                c.replace('rgb', 'rgba').replace(')', ', 0.6)') for c in colors[:len(data)]
            ],
            'tension': 0.3 if chart_type == 'line' else 0,
        }
        
        datasets.append(dataset)
    
    chart_data = {
        'type': chart_type,
        'labels': labels,
        'datasets': datasets
    }
    
    logger.info(f"차트 생성 완료 - 타입: {chart_type}, 데이터셋: {len(datasets)}개")
    return chart_data


def _determine_chart_type(date_columns: List[str], text_columns: List[str], 
                          number_columns: List[str], row_count: int) -> str:
    """
    데이터 특성을 기반으로 적절한 차트 타입 선택
    
    Returns:
        'line', 'bar', 'pie' 중 하나
    """
    # 시계열 데이터 → 라인 차트
    if date_columns:
        return 'line'
    
    # 항목이 적고 숫자 컬럼이 1개 → 파이 차트
    if row_count <= 7 and len(number_columns) == 1:
        return 'pie'
    
    # 기본 → 바 차트
    return 'bar'
