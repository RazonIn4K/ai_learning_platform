"""
Learning metrics tracking module for AI learning platform.
"""

class LearningMetrics:
    """
    Tracks and analyzes learning metrics for the AI learning platform.
    """
    
    def __init__(self):
        """Initialize the learning metrics tracker."""
        self.metrics = {}
        
    def record_metric(self, metric_name: str, value: float) -> None:
        """
        Record a metric value.
        
        Args:
            metric_name: Name of the metric
            value: Value to record
        """
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        
        self.metrics[metric_name].append(value)
        
    def get_metric(self, metric_name: str) -> list:
        """
        Get all recorded values for a metric.
        
        Args:
            metric_name: Name of the metric
            
        Returns:
            List of recorded values
        """
        return self.metrics.get(metric_name, [])
        
    def get_average(self, metric_name: str) -> float:
        """
        Get the average value for a metric.
        
        Args:
            metric_name: Name of the metric
            
        Returns:
            Average value or 0 if no values recorded
        """
        values = self.get_metric(metric_name)
        return sum(values) / len(values) if values else 0