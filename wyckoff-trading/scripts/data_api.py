import akshare as ak  # pip install akshare
import pandas as pd
import json

def get_realtime_quote(stock_code):
    """获取实时报价"""
    try:
        df = ak.stock_zh_a_spot_em()
        stock_data = df[df['代码'] == stock_code]
        if not stock_data.empty:
            row = stock_data.iloc[0]
            return {
                'code': stock_code,
                'name': row.get('名称'),
                'price': row.get('最新价'),
                'open': row.get('今开'),
                'high': row.get('最高'),
                'low': row.get('最低'),
                'volume': row.get('成交量'),
                'amount': row.get('成交额'),
                'change_pct': row.get('涨跌幅'),
                'timestamp': str(pd.Timestamp.now())
            }
    except Exception as e:
        return {'error': str(e)}
    return None

def get_kline_data(stock_code, period='daily', limit=200):
    """获取K线数据用于威科夫分析"""
    try:
        end_date = pd.Timestamp.now().strftime('%Y%m%d')
        start_date = (pd.Timestamp.now() - pd.Timedelta(days=limit*2)).strftime('%Y%m%d')
        
        df = ak.stock_zh_a_hist(
            symbol=stock_code,
            period=period,
            start_date=start_date,
            end_date=end_date,
            adjust=""
        )
        if df is not None and not df.empty:
            df = df.rename(columns={
                '日期': 'trade_time', '开盘': 'open', '收盘': 'close',
                '最高': 'high', '最低': 'low', '成交量': 'volume',
                '成交额': 'amount', '振幅': 'amplitude', '涨跌幅': 'pct_chg',
                '涨跌额': 'change', '换手率': 'turnover'
            })
            return df.to_dict('records')
    except Exception as e:
        return []
    return []

def get_index_quote(index_code='000001'):
    """获取大盘指数行情（上证指数）"""
    try:
        df = ak.index_zh_a_spot_em(symbol="sh")
        index_data = df[df['代码'] == index_code]
        if not index_data.empty:
            row = index_data.iloc[0]
            return {
                'code': index_code,
                'name': row.get('名称'),
                'price': row.get('最新价'),
                'change_pct': row.get('涨跌幅')
            }
    except Exception as e:
        return {'error': str(e)}
    return None

def get_index_kline(index_code='000001', period='daily', limit=200):
    """获取指数K线数据"""
    try:
        end_date = pd.Timestamp.now().strftime('%Y%m%d')
        start_date = (pd.Timestamp.now() - pd.Timedelta(days=limit*2)).strftime('%Y%m%d')
        
        symbol_map = {'000001': 'sh', '399001': 'sz'}
        symbol = symbol_map.get(index_code, 'sh')
        
        df = ak.stock_zh_a_hist(
            symbol=symbol,
            period=period,
            start_date=start_date,
            end_date=end_date,
            adjust=""
        )
        if df is not None and not df.empty:
            df = df.rename(columns={
                '日期': 'trade_time', '开盘': 'open', '收盘': 'close',
                '最高': 'high', '最低': 'low', '成交量': 'volume'
            })
            return df.to_dict('records')
    except Exception as e:
        return []
    return []

def calculate_ma(data, period=20):
    """计算移动平均线"""
    if len(data) < period:
        return None
    prices = [bar['close'] for bar in data[-period:]]
    return sum(prices) / period

def identify_support_resistance(data, lookback=50):
    """识别支撑位和阻力位"""
    if len(data) < lookback:
        lookback = len(data)
    
    recent = data[-lookback:]
    highs = [bar['high'] for bar in recent]
    lows = [bar['low'] for bar in recent]
    
    resistance = max(highs)
    support = min(lows)
    
    return {
        'resistance': resistance,
        'support': support,
        'range': resistance - support,
        'midpoint': (resistance + support) / 2
    }

def identify_sc(data):
    """识别Selling Climax (SC) - 恐慌抛售"""
    if len(data) < 30:
        return None
    
    for i in range(len(data) - 5, 10, -1):
        current_vol = data[i].get('volume', 0)
        prev_vols = [data[j].get('volume', 0) for j in range(max(0, i-5), i)]
        avg_prev_vol = sum(prev_vols) / len(prev_vols) if prev_vols else 0
        
        if avg_prev_vol > 0 and current_vol > avg_prev_vol * 1.5:
            if data[i]['close'] < data[i-5]['low'] * 0.98:
                return {
                    'type': 'SC',
                    'date': str(data[i].get('trade_time', '')),
                    'low': data[i]['low'],
                    'close': data[i]['close'],
                    'volume': current_vol,
                    'significance': 'high' if current_vol > avg_prev_vol * 2 else 'medium'
                }
    return None

def identify_bc(data):
    """识别Buying Climax (BC) - 疯狂买入"""
    if len(data) < 30:
        return None
    
    for i in range(len(data) - 5, 10, -1):
        current_vol = data[i].get('volume', 0)
        prev_vols = [data[j].get('volume', 0) for j in range(max(0, i-5), i)]
        avg_prev_vol = sum(prev_vols) / len(prev_vols) if prev_vols else 0
        
        if avg_prev_vol > 0 and current_vol > avg_prev_vol * 1.5:
            if data[i]['close'] > data[i-5]['high'] * 1.02:
                return {
                    'type': 'BC',
                    'date': str(data[i].get('trade_time', '')),
                    'high': data[i]['high'],
                    'close': data[i]['close'],
                    'volume': current_vol,
                    'significance': 'high' if current_vol > avg_prev_vol * 2 else 'medium'
                }
    return None

def identify_spring(kline_data):
    """识别Spring信号 - 弹簧效应"""
    if len(kline_data) < 30:
        return None
    
    sr = identify_support_resistance(kline_data)
    support = sr['support']
    recent = kline_data[-30:]
    
    for i in range(10, len(recent) - 3):
        current = recent[i]
        next_bar = recent[i + 1]
        
        if (current['low'] < support * 0.99 and
            next_bar['close'] > support and
            next_bar['close'] > current['close']):
            vol_ratio = next_bar.get('volume', 1) / current.get('volume', 1) if current.get('volume', 1) > 0 else 1
            return {
                'type': 'Spring',
                'date': str(current.get('trade_time', '')),
                'break_low': current['low'],
                'recovery_close': next_bar['close'],
                'volume_confirmed': vol_ratio < 0.8,
                'strength': 'strong' if vol_ratio < 0.5 else 'normal'
            }
    return None

def identify_jac(kline_data):
    """识别JAC信号 - 跳跃小溪"""
    if len(kline_data) < 40:
        return None
    
    recent = kline_data[-40:]
    
    for i in range(15, len(recent) - 8):
        breakout = recent[i]
        if breakout['close'] > breakout['open'] * 1.03:
            for j in range(i+1, min(i+8, len(recent))):
                pullback = recent[j]
                pullback_vol = pullback.get('volume', 1)
                breakout_vol = breakout.get('volume', 1)
                if (pullback['close'] < breakout['close'] and
                    pullback['close'] > breakout['open'] and
                    breakout_vol > 0 and pullback_vol < breakout_vol * 0.6):
                    return {
                        'type': 'JAC',
                        'breakout_date': str(breakout.get('trade_time', '')),
                        'breakout_price': breakout['close'],
                        'breakout_volume': breakout.get('volume'),
                        'pullback_date': str(pullback.get('trade_time', '')),
                        'pullback_price': pullback['close'],
                        'pullback_volume': pullback.get('volume'),
                        'strength': 'strong' if pullback_vol < breakout_vol * 0.3 else 'normal'
                    }
    return None

def identify_sos(kline_data):
    """识别SOS信号 - 强势信号"""
    if len(kline_data) < 20:
        return None
    
    recent = kline_data[-20:]
    ma20 = calculate_ma(kline_data, 20)
    
    for i in range(5, len(recent) - 1):
        current = recent[i]
        avg_vol = sum([bar.get('volume', 0) for bar in recent[i-5:i]]) / 5
        
        if (current['close'] > current['open'] * 1.02 and
            current.get('volume', 0) > avg_vol * 1.5 and
            current['close'] > current['open'] * 0.95):
            return {
                'type': 'SOS',
                'date': str(current.get('trade_time', '')),
                'close': current['close'],
                'high': current['high'],
                'volume': current.get('volume'),
                'volume_ratio': current.get('volume', 0) / avg_vol if avg_vol > 0 else 0,
                'above_ma20': ma20 and current['close'] > ma20
            }
    return None

def identify_sow(kline_data):
    """识别SOW信号 - 弱势信号"""
    if len(kline_data) < 20:
        return None
    
    recent = kline_data[-20:]
    ma20 = calculate_ma(kline_data, 20)
    
    for i in range(5, len(recent) - 1):
        current = recent[i]
        avg_vol = sum([bar.get('volume', 0) for bar in recent[i-5:i]]) / 5
        
        if (current['close'] < current['open'] * 0.98 and
            current.get('volume', 0) > avg_vol * 1.5):
            return {
                'type': 'SOW',
                'date': str(current.get('trade_time', '')),
                'close': current['close'],
                'low': current['low'],
                'volume': current.get('volume'),
                'volume_ratio': current.get('volume', 0) / avg_vol if avg_vol > 0 else 0,
                'below_ma20': ma20 and current['close'] < ma20
            }
    return None

def identify_lps(kline_data):
    """识别LPS信号 - 最后支撑点"""
    if len(kline_data) < 30:
        return None
    
    recent = kline_data[-30:]
    
    for i in range(10, len(recent) - 3):
        current = recent[i]
        avg_vol = sum([bar.get('volume', 0) for bar in recent[i-5:i]]) / 5
        
        if (current.get('volume', 0) < avg_vol * 0.6 and
            current['close'] > current['low'] * 1.01):
            if i > 1 and current['low'] > recent[i-1]['low']:
                return {
                    'type': 'LPS',
                    'date': str(current.get('trade_time', '')),
                    'low': current['low'],
                    'close': current['close'],
                    'volume': current.get('volume'),
                    'volume_shrink': True
                }
    return None

def identify_ut(kline_data):
    """识别UT信号 - 上冲回落"""
    if len(kline_data) < 30:
        return None
    
    sr = identify_support_resistance(kline_data)
    resistance = sr['resistance']
    recent = kline_data[-30:]
    
    for i in range(10, len(recent) - 1):
        current = recent[i]
        next_bar = recent[i + 1]
        
        if (current['high'] > resistance * 0.99 and
            next_bar['close'] < current['close']):
            return {
                'type': 'UT',
                'date': str(current.get('trade_time', '')),
                'high': current['high'],
                'close': current['close'],
                'rejection': True,
                'follow_up_needed': True
            }
    return None

def identify_st(kline_data):
    """识别ST信号 - 二次测试"""
    if len(kline_data) < 30:
        return None
    
    sc = identify_sc(kline_data)
    if not sc:
        return None
    
    recent = kline_data[-30:]
    sc_low = sc['low']
    
    for i in range(len(recent) - 10, len(recent) - 2):
        current = recent[i]
        if (abs(current['low'] - sc_low) / sc_low < 0.02 and
            current.get('volume', 0) < 1000000):
            return {
                'type': 'ST',
                'date': str(current.get('trade_time', '')),
                'test_price': current['low'],
                'volume': current.get('volume'),
                'volume_confirmed': True
            }
    return None

def determine_market_phase(kline_data):
    """判断市场阶段"""
    if len(kline_data) < 50:
        return {'phase': 'unknown', 'confidence': 'low'}
    
    sr = identify_support_resistance(kline_data)
    recent = kline_data[-20:]
    current_price = recent[-1]['close']
    
    avg_volume = sum([bar.get('volume', 0) for bar in recent]) / len(recent)
    
    if current_price < sr['midpoint']:
        if recent[-1].get('volume', 0) > avg_volume * 1.5:
            return {'phase': 'Accumulation', 'confidence': 'medium', 'details': '低位缩量横盘'}
        return {'phase': 'Accumulation', 'confidence': 'low', 'details': '可能吸筹中'}
    else:
        if recent[-1].get('volume', 0) > avg_volume * 1.5 and recent[-1]['close'] < recent[-1]['open']:
            return {'phase': 'Distribution', 'confidence': 'medium', 'details': '高位放量滞涨'}
        return {'phase': 'Markup', 'confidence': 'low', 'details': '可能上涨中'}
    
    return {'phase': 'unknown', 'confidence': 'low'}

def analyze_volume_price(kline_data):
    """量价关系分析"""
    if len(kline_data) < 20:
        return None
    
    recent = kline_data[-20:]
    up_days = [bar for bar in recent if bar['close'] > bar['open']]
    down_days = [bar for bar in recent if bar['close'] < bar['open']]
    
    avg_up_vol = sum([bar.get('volume', 0) for bar in up_days]) / len(up_days) if up_days else 0
    avg_down_vol = sum([bar.get('volume', 0) for bar in down_days]) / len(down_days) if down_days else 0
    
    trend = 'healthy' if avg_up_vol > avg_down_vol else 'weak'
    
    return {
        'trend': trend,
        'avg_up_volume': avg_up_vol,
        'avg_down_volume': avg_down_vol,
        'up_days': len(up_days),
        'down_days': len(down_days),
        'interpretation': '量价配合健康' if trend == 'healthy' else '量价背离，注意风险'
    }

def analyze_wyckoff(stock_code, period='daily'):
    """综合威科夫分析"""
    quote = get_realtime_quote(stock_code)
    kline = get_kline_data(stock_code, period=period, limit=200)
    
    if not kline:
        return {'error': '无法获取K线数据'}
    
    signals = []
    phases = []
    
    spring = identify_spring(kline)
    if spring:
        signals.append(spring)
    
    jac = identify_jac(kline)
    if jac:
        signals.append(jac)
    
    ut = identify_ut(kline)
    if ut:
        signals.append(ut)
    
    sos = identify_sos(kline)
    if sos:
        signals.append(sos)
    
    sow = identify_sow(kline)
    if sow:
        signals.append(sow)
    
    lps = identify_lps(kline)
    if lps:
        signals.append(lps)
    
    st = identify_st(kline)
    if st:
        signals.append(st)
    
    sc = identify_sc(kline)
    if sc:
        phases.append(sc)
    
    bc = identify_bc(kline)
    if bc:
        phases.append(bc)
    
    market_phase = determine_market_phase(kline)
    sr_levels = identify_support_resistance(kline)
    vp_analysis = analyze_volume_price(kline)
    
    index_quote = get_index_quote('000001')
    
    return {
        'stock_code': stock_code,
        'quote': quote,
        'market_phase': market_phase,
        'support_resistance': sr_levels,
        'signals': signals,
        'key_phases': phases,
        'volume_price': vp_analysis,
        'signal_count': len(signals),
        'index': index_quote
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        stock = sys.argv[1]
        period = sys.argv[2] if len(sys.argv) > 2 else 'daily'
        result = analyze_wyckoff(stock, period)
        print(json.dumps(result, indent=2, ensure_ascii=False))
