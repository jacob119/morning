"""
성능 모니터링 및 최적화 시스템

애플리케이션 성능을 모니터링하고 최적화하는 시스템입니다.
"""

import time
import functools
import logging
import psutil
import threading
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import statistics

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """성능 메트릭"""
    operation: str
    duration: float
    timestamp: datetime
    memory_usage: float
    cpu_usage: float
    success: bool
    error_message: Optional[str] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)


class PerformanceMonitor:
    """성능 모니터"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics: deque = deque(maxlen=max_history)
        self.operation_stats: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.lock = threading.Lock()
        
        # 시스템 리소스 모니터링
        self.system_metrics: deque = deque(maxlen=100)
        self._start_system_monitoring()
    
    def _start_system_monitoring(self) -> None:
        """시스템 모니터링 시작"""
        def monitor_system():
            while True:
                try:
                    cpu_percent = psutil.cpu_percent(interval=1)
                    memory = psutil.virtual_memory()
                    
                    system_metric = {
                        'timestamp': datetime.now(),
                        'cpu_percent': cpu_percent,
                        'memory_percent': memory.percent,
                        'memory_available': memory.available,
                        'memory_used': memory.used
                    }
                    
                    with self.lock:
                        self.system_metrics.append(system_metric)
                    
                    time.sleep(5)  # 5초마다 수집
                except Exception as e:
                    logger.error(f"시스템 모니터링 오류: {e}")
                    time.sleep(10)
        
        thread = threading.Thread(target=monitor_system, daemon=True)
        thread.start()
    
    def record_metric(self, metric: PerformanceMetric) -> None:
        """메트릭 기록"""
        with self.lock:
            self.metrics.append(metric)
            self._update_operation_stats(metric)
    
    def _update_operation_stats(self, metric: PerformanceMetric) -> None:
        """작업 통계 업데이트"""
        operation = metric.operation
        
        if operation not in self.operation_stats:
            self.operation_stats[operation] = {
                'count': 0,
                'total_duration': 0,
                'min_duration': float('inf'),
                'max_duration': 0,
                'success_count': 0,
                'error_count': 0,
                'durations': []
            }
        
        stats = self.operation_stats[operation]
        stats['count'] += 1
        stats['total_duration'] += metric.duration
        stats['min_duration'] = min(stats['min_duration'], metric.duration)
        stats['max_duration'] = max(stats['max_duration'], metric.duration)
        stats['durations'].append(metric.duration)
        
        if metric.success:
            stats['success_count'] += 1
        else:
            stats['error_count'] += 1
        
        # 최근 100개만 유지
        if len(stats['durations']) > 100:
            stats['durations'] = stats['durations'][-100:]
    
    def get_operation_stats(self, operation: str) -> Optional[Dict[str, Any]]:
        """작업 통계 조회"""
        if operation not in self.operation_stats:
            return None
        
        stats = self.operation_stats[operation]
        
        if not stats['durations']:
            return None
        
        return {
            'operation': operation,
            'count': stats['count'],
            'success_rate': stats['success_count'] / stats['count'],
            'error_rate': stats['error_count'] / stats['count'],
            'avg_duration': statistics.mean(stats['durations']),
            'median_duration': statistics.median(stats['durations']),
            'min_duration': stats['min_duration'],
            'max_duration': stats['max_duration'],
            'std_duration': statistics.stdev(stats['durations']) if len(stats['durations']) > 1 else 0
        }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """시스템 통계 조회"""
        if not self.system_metrics:
            return {}
        
        recent_metrics = list(self.system_metrics)[-10:]  # 최근 10개
        
        cpu_values = [m['cpu_percent'] for m in recent_metrics]
        memory_values = [m['memory_percent'] for m in recent_metrics]
        
        return {
            'cpu_avg': statistics.mean(cpu_values),
            'cpu_max': max(cpu_values),
            'memory_avg': statistics.mean(memory_values),
            'memory_max': max(memory_values),
            'memory_available': recent_metrics[-1]['memory_available'],
            'last_updated': recent_metrics[-1]['timestamp']
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """성능 요약 조회"""
        if not self.metrics:
            return {'total_operations': 0}
        
        recent_metrics = list(self.metrics)[-100:]  # 최근 100개
        
        total_operations = len(recent_metrics)
        successful_operations = sum(1 for m in recent_metrics if m.success)
        avg_duration = statistics.mean([m.duration for m in recent_metrics])
        
        return {
            'total_operations': total_operations,
            'success_rate': successful_operations / total_operations if total_operations > 0 else 0,
            'avg_duration': avg_duration,
            'system_stats': self.get_system_stats(),
            'top_operations': self._get_top_operations()
        }
    
    def _get_top_operations(self) -> List[Dict[str, Any]]:
        """가장 많이 실행된 작업들"""
        operation_counts = defaultdict(int)
        
        for metric in self.metrics:
            operation_counts[metric.operation] += 1
        
        top_operations = sorted(
            operation_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        return [
            {
                'operation': op,
                'count': count,
                'stats': self.get_operation_stats(op)
            }
            for op, count in top_operations
        ]


# 전역 성능 모니터
performance_monitor = PerformanceMonitor()


def monitor_performance(operation_name: Optional[str] = None) -> Callable:
    """성능 모니터링 데코레이터"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            start_cpu = psutil.cpu_percent()
            
            try:
                result = func(*args, **kwargs)
                success = True
                error_message = None
            except Exception as e:
                success = False
                error_message = str(e)
                raise
            finally:
                end_time = time.time()
                end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
                end_cpu = psutil.cpu_percent()
                
                duration = end_time - start_time
                memory_usage = end_memory - start_memory
                cpu_usage = end_cpu - start_cpu
                
                metric = PerformanceMetric(
                    operation=op_name,
                    duration=duration,
                    timestamp=datetime.now(),
                    memory_usage=memory_usage,
                    cpu_usage=cpu_usage,
                    success=success,
                    error_message=error_message,
                    additional_data={
                        'args_count': len(args),
                        'kwargs_count': len(kwargs)
                    }
                )
                
                performance_monitor.record_metric(metric)
            
            return result
        return wrapper
    return decorator


class PerformanceOptimizer:
    """성능 최적화기"""
    
    def __init__(self, monitor: PerformanceMonitor):
        self.monitor = monitor
        self.optimization_rules: List[Callable] = []
    
    def add_optimization_rule(self, rule: Callable) -> None:
        """최적화 규칙 추가"""
        self.optimization_rules.append(rule)
    
    def analyze_performance(self) -> Dict[str, Any]:
        """성능 분석"""
        summary = self.monitor.get_performance_summary()
        recommendations = []
        
        # 성능 문제 진단
        if summary.get('avg_duration', 0) > 1.0:  # 1초 이상
            recommendations.append({
                'type': 'slow_operations',
                'message': '평균 실행 시간이 1초를 초과합니다. 최적화가 필요합니다.',
                'severity': 'high'
            })
        
        if summary.get('success_rate', 1.0) < 0.95:  # 95% 미만
            recommendations.append({
                'type': 'error_rate',
                'message': '에러율이 5%를 초과합니다. 에러 처리를 개선해야 합니다.',
                'severity': 'high'
            })
        
        system_stats = summary.get('system_stats', {})
        if system_stats.get('cpu_avg', 0) > 80:  # CPU 80% 이상
            recommendations.append({
                'type': 'high_cpu',
                'message': 'CPU 사용률이 높습니다. 리소스 최적화가 필요합니다.',
                'severity': 'medium'
            })
        
        if system_stats.get('memory_avg', 0) > 80:  # 메모리 80% 이상
            recommendations.append({
                'type': 'high_memory',
                'message': '메모리 사용률이 높습니다. 메모리 누수를 확인하세요.',
                'severity': 'medium'
            })
        
        return {
            'summary': summary,
            'recommendations': recommendations,
            'optimization_opportunities': self._find_optimization_opportunities()
        }
    
    def _find_optimization_opportunities(self) -> List[Dict[str, Any]]:
        """최적화 기회 찾기"""
        opportunities = []
        
        # 느린 작업들 찾기
        for operation in self.monitor.operation_stats:
            stats = self.monitor.get_operation_stats(operation)
            if stats and stats['avg_duration'] > 0.5:  # 0.5초 이상
                opportunities.append({
                    'operation': operation,
                    'type': 'slow_operation',
                    'current_avg': stats['avg_duration'],
                    'suggestion': '캐싱 또는 알고리즘 최적화 고려'
                })
        
        # 자주 호출되는 작업들 찾기
        for operation in self.monitor.operation_stats:
            stats = self.monitor.get_operation_stats(operation)
            if stats and stats['count'] > 100:  # 100회 이상 호출
                opportunities.append({
                    'operation': operation,
                    'type': 'frequent_operation',
                    'count': stats['count'],
                    'suggestion': '결과 캐싱 또는 배치 처리 고려'
                })
        
        return opportunities


class CacheManager:
    """캐시 관리자"""
    
    def __init__(self, max_size: int = 1000, ttl: int = 300):
        self.max_size = max_size
        self.ttl = ttl  # seconds
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.access_times: Dict[str, datetime] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """캐시에서 값 가져오기"""
        if key not in self.cache:
            return None
        
        cache_entry = self.cache[key]
        created_time = cache_entry['created_time']
        
        # TTL 확인
        if datetime.now() - created_time > timedelta(seconds=self.ttl):
            self.delete(key)
            return None
        
        # 접근 시간 업데이트
        self.access_times[key] = datetime.now()
        return cache_entry['value']
    
    def set(self, key: str, value: Any) -> None:
        """캐시에 값 설정"""
        # 캐시 크기 확인
        if len(self.cache) >= self.max_size:
            self._evict_oldest()
        
        self.cache[key] = {
            'value': value,
            'created_time': datetime.now()
        }
        self.access_times[key] = datetime.now()
    
    def delete(self, key: str) -> None:
        """캐시에서 값 삭제"""
        if key in self.cache:
            del self.cache[key]
        if key in self.access_times:
            del self.access_times[key]
    
    def clear(self) -> None:
        """캐시 전체 삭제"""
        self.cache.clear()
        self.access_times.clear()
    
    def _evict_oldest(self) -> None:
        """가장 오래된 항목 제거"""
        if not self.access_times:
            return
        
        oldest_key = min(self.access_times.keys(), 
                        key=lambda k: self.access_times[k])
        self.delete(oldest_key)
    
    def get_stats(self) -> Dict[str, Any]:
        """캐시 통계"""
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hit_rate': 0,  # TODO: 히트율 계산 구현
            'ttl': self.ttl
        }


# 사용 예시
if __name__ == "__main__":
    # 성능 모니터링 예시
    @monitor_performance("test_operation")
    def slow_operation():
        time.sleep(0.1)  # 100ms 지연
        return "result"
    
    @monitor_performance("fast_operation")
    def fast_operation():
        return "quick result"
    
    # 성능 테스트
    for _ in range(10):
        slow_operation()
        fast_operation()
    
    # 성능 분석
    optimizer = PerformanceOptimizer(performance_monitor)
    analysis = optimizer.analyze_performance()
    
    print("성능 분석 결과:")
    print(f"총 작업 수: {analysis['summary']['total_operations']}")
    print(f"성공률: {analysis['summary']['success_rate']:.2%}")
    print(f"평균 실행 시간: {analysis['summary']['avg_duration']:.3f}초")
    
    if analysis['recommendations']:
        print("\n권장사항:")
        for rec in analysis['recommendations']:
            print(f"- {rec['message']} (심각도: {rec['severity']})")
    
    # 캐시 테스트
    cache = CacheManager(max_size=100, ttl=60)
    cache.set("test_key", "test_value")
    print(f"\n캐시에서 값: {cache.get('test_key')}")
    print(f"캐시 통계: {cache.get_stats()}")
