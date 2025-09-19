"""
Data retention policies for touchpoint monitoring data.

This module defines retention policies to prevent database bloat
while maintaining useful historical data for analysis.
"""

from django.conf import settings
from datetime import timedelta


class TouchpointRetentionPolicies:
    """
    Configurable retention policies for touchpoint monitoring data.
    
    These policies balance storage costs with operational needs:
    - Detailed events: Short retention (high volume, low long-term value)
    - Aggregated metrics: Medium retention (medium volume, high analytical value)
    - Alerts: Medium retention (low volume, high operational value)
    """
    
    # Default retention periods (can be overridden in settings)
    DEFAULT_RETENTION_DAYS = {
        'detailed_events': 90,      # 3 months of detailed events
        'aggregated_metrics': 365,  # 1 year of aggregated metrics
        'cache_metrics': 180,       # 6 months of cache metrics
        'health_records': 90,       # 3 months of health records
        'resolved_alerts': 180,     # 6 months of resolved alerts
        'dismissed_alerts': 30,     # 1 month of dismissed alerts
        'active_alerts': None,      # Keep active alerts indefinitely
    }
    
    @classmethod
    def get_retention_days(cls, data_type: str) -> int:
        """
        Get retention period in days for a specific data type.
        
        Args:
            data_type: Type of data ('detailed_events', 'aggregated_metrics', etc.)
            
        Returns:
            Number of days to retain the data
        """
        # Check if custom retention is configured in settings
        custom_retention = getattr(settings, 'TOUCHPOINT_RETENTION_DAYS', {})
        
        return custom_retention.get(data_type, cls.DEFAULT_RETENTION_DAYS[data_type])
    
    @classmethod
    def get_retention_timedelta(cls, data_type: str) -> timedelta:
        """
        Get retention period as timedelta for a specific data type.
        
        Args:
            data_type: Type of data
            
        Returns:
            Timedelta object representing the retention period
        """
        days = cls.get_retention_days(data_type)
        return timedelta(days=days)
    
    @classmethod
    def get_all_policies(cls) -> dict:
        """
        Get all retention policies.
        
        Returns:
            Dictionary mapping data types to retention periods in days
        """
        return {
            data_type: cls.get_retention_days(data_type)
            for data_type in cls.DEFAULT_RETENTION_DAYS.keys()
        }


# Retention policy recommendations for different environments
class RetentionRecommendations:
    """
    Recommended retention policies for different environments and use cases.
    """
    
    # Development environment (minimal retention for cost savings)
    DEVELOPMENT = {
        'detailed_events': 7,       # 1 week
        'aggregated_metrics': 30,   # 1 month
        'cache_metrics': 14,        # 2 weeks
        'health_records': 7,        # 1 week
        'resolved_alerts': 30,      # 1 month
        'dismissed_alerts': 7,      # 1 week
    }
    
    # Staging environment (moderate retention for testing)
    STAGING = {
        'detailed_events': 30,      # 1 month
        'aggregated_metrics': 90,   # 3 months
        'cache_metrics': 60,        # 2 months
        'health_records': 30,       # 1 month
        'resolved_alerts': 90,      # 3 months
        'dismissed_alerts': 14,     # 2 weeks
    }
    
    # Production environment (balanced retention)
    PRODUCTION = {
        'detailed_events': 90,      # 3 months
        'aggregated_metrics': 365,  # 1 year
        'cache_metrics': 180,       # 6 months
        'health_records': 90,       # 3 months
        'resolved_alerts': 180,     # 6 months
        'dismissed_alerts': 30,     # 1 month
    }
    
    # High-compliance environment (extended retention)
    COMPLIANCE = {
        'detailed_events': 365,     # 1 year
        'aggregated_metrics': 1095, # 3 years
        'cache_metrics': 365,       # 1 year
        'health_records': 365,      # 1 year
        'resolved_alerts': 365,     # 1 year
        'dismissed_alerts': 90,     # 3 months
    }
    
    # High-volume environment (aggressive retention for cost control)
    HIGH_VOLUME = {
        'detailed_events': 30,      # 1 month
        'aggregated_metrics': 180,  # 6 months
        'cache_metrics': 90,        # 3 months
        'health_records': 30,       # 1 month
        'resolved_alerts': 90,      # 3 months
        'dismissed_alerts': 7,      # 1 week
    }


# Storage cost estimates (rough calculations)
class StorageEstimates:
    """
    Rough estimates of storage costs for touchpoint monitoring data.
    """
    
    # Estimated bytes per record
    BYTES_PER_RECORD = {
        'detailed_events': 500,     # ~500 bytes per event
        'aggregated_metrics': 200,  # ~200 bytes per metric record
        'cache_metrics': 150,       # ~150 bytes per cache metric
        'health_records': 100,      # ~100 bytes per health record
        'alerts': 300,              # ~300 bytes per alert
    }
    
    @classmethod
    def estimate_storage_mb(cls, records_per_day: dict, retention_days: dict) -> dict:
        """
        Estimate storage requirements in MB.
        
        Args:
            records_per_day: Dictionary mapping data types to daily record counts
            retention_days: Dictionary mapping data types to retention periods
            
        Returns:
            Dictionary with storage estimates in MB
        """
        estimates = {}
        
        for data_type, daily_count in records_per_day.items():
            retention = retention_days.get(data_type, 0)
            bytes_per_record = cls.BYTES_PER_RECORD.get(data_type, 200)
            
            total_records = daily_count * retention
            total_bytes = total_records * bytes_per_record
            total_mb = total_bytes / (1024 * 1024)
            
            estimates[data_type] = {
                'daily_records': daily_count,
                'retention_days': retention,
                'total_records': total_records,
                'storage_mb': round(total_mb, 2)
            }
        
        return estimates
    
    @classmethod
    def estimate_total_storage_mb(cls, records_per_day: dict, retention_days: dict) -> float:
        """
        Estimate total storage requirements in MB.
        
        Args:
            records_per_day: Dictionary mapping data types to daily record counts
            retention_days: Dictionary mapping data types to retention periods
            
        Returns:
            Total storage estimate in MB
        """
        estimates = cls.estimate_storage_mb(records_per_day, retention_days)
        return sum(estimate['storage_mb'] for estimate in estimates.values())
