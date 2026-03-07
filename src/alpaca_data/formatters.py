"""Output formatters for Alpaca Market Data SDK.

This module provides formatters to convert data models into various output formats
including JSON, CSV, and pandas DataFrames.
"""

import json
import csv
import io
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from pathlib import Path

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

from .models import Bar, Quote, Trade, Snapshot, News


class DataFormatter:
    """Base class for data formatters."""
    
    def format(self, data: Any, **kwargs) -> Any:
        """Format data to the desired output format.
        
        Args:
            data: Data to format (models, lists, or API responses)
            **kwargs: Additional formatting options
            
        Returns:
            Formatted data
        """
        raise NotImplementedError


class JSONFormatter(DataFormatter):
    """Format data as JSON."""
    
    def format(self, data: Any, indent: int = 2, sort_keys: bool = False, **kwargs) -> str:
        """Format data as JSON string.
        
        Args:
            data: Data to format
            indent: JSON indentation level
            sort_keys: Whether to sort dictionary keys
            **kwargs: Additional JSON options
            
        Returns:
            JSON formatted string
        """
        def json_serializer(obj):
            """Custom JSON serializer for datetime objects and models."""
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif hasattr(obj, 'to_dict'):
                return obj.to_dict()
            elif isinstance(obj, (Bar, Quote, Trade, Snapshot, News)):
                return obj.to_dict()
            elif isinstance(obj, (list, tuple)):
                return [json_serializer(item) for item in obj]
            elif isinstance(obj, dict):
                return {k: json_serializer(v) for k, v in obj.items()}
            else:
                return obj
        
        return json.dumps(json_serializer(data), indent=indent, sort_keys=sort_keys, **kwargs)


class CSVFormatter(DataFormatter):
    """Format data as CSV."""
    
    def format(self, data: Any, filename: Optional[str] = None, **kwargs) -> str:
        """Format data as CSV string.
        
        Args:
            data: Data to format (lists of models or API responses with lists)
            filename: Optional filename to save to (if provided, returns empty string)
            **kwargs: Additional CSV options (delimiter, quoting, etc.)
            
        Returns:
            CSV formatted string (or empty string if filename provided)
        """
        # Extract data items from various input formats
        items = self._extract_items(data)
        
        if not items:
            return ""
        
        # Get field names from first item
        if hasattr(items[0], 'to_dict'):
            fieldnames = list(items[0].to_dict().keys())
        else:
            fieldnames = list(items[0].keys())
        
        # Create CSV output
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames, **kwargs)
        writer.writeheader()
        
        for item in items:
            if hasattr(item, 'to_dict'):
                writer.writerow(item.to_dict())
            else:
                writer.writerow(item)
        
        csv_content = output.getvalue()
        output.close()
        
        # Save to file if filename provided
        if filename:
            Path(filename).write_text(csv_content, encoding='utf-8')
            return ""
        
        return csv_content
    
    def _extract_items(self, data: Any) -> List[Dict[str, Any]]:
        """Extract data items from various input formats."""
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            # Check for common list fields in API responses
            for field in ['bars', 'quotes', 'trades', 'snapshots', 'news']:
                if field in data and isinstance(data[field], list):
                    return data[field]
            # Return empty list if no list fields found
            return []
        else:
            # Single item - wrap in list
            if hasattr(data, 'to_dict'):
                return [data.to_dict()]
            elif isinstance(data, dict):
                return [data]
            else:
                return []


class DataFrameFormatter(DataFormatter):
    """Format data as pandas DataFrame."""
    
    def __init__(self):
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas is required for DataFrame formatting. Install with: pip install pandas")
    
    def format(self, data: Any, **kwargs) -> 'pd.DataFrame':
        """Format data as pandas DataFrame.
        
        Args:
            data: Data to format (lists of models or API responses with lists)
            **kwargs: Additional pandas DataFrame options
            
        Returns:
            pandas DataFrame
        """
        import pandas as pd
        
        # Extract data items from various input formats
        items = self._extract_items(data)
        
        if not items:
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(items)
        
        # Apply additional formatting options
        return df
    
    def _extract_items(self, data: Any) -> List[Dict[str, Any]]:
        """Extract data items from various input formats."""
        if isinstance(data, list):
            # Check if list contains model objects
            if data and hasattr(data[0], 'to_dict'):
                return [item.to_dict() for item in data]
            return data
        elif isinstance(data, dict):
            # Check for common list fields in API responses
            for field in ['bars', 'quotes', 'trades', 'snapshots', 'news']:
                if field in data and isinstance(data[field], list):
                    items = data[field]
                    # Convert model objects to dictionaries
                    if items and hasattr(items[0], 'to_dict'):
                        return [item.to_dict() for item in items]
                    return items
            return []
        else:
            # Single item
            if hasattr(data, 'to_dict'):
                return [data.to_dict()]
            elif isinstance(data, dict):
                return [data]
            else:
                return []


class OutputFormatter:
    """Main formatter class that delegates to specific formatters."""
    
    def __init__(self):
        self.formatters = {
            'json': JSONFormatter(),
            'csv': CSVFormatter(),
            'dataframe': DataFrameFormatter(),
        }
    
    def format(
        self, 
        data: Any, 
        format_type: str = 'json', 
        filename: Optional[str] = None,
        **kwargs
    ) -> Union[str, Any]:
        """Format data to the specified output format.
        
        Args:
            data: Data to format
            format_type: Output format ('json', 'csv', 'dataframe')
            filename: Optional filename for CSV output
            **kwargs: Additional formatting options
            
        Returns:
            Formatted data (string for JSON/CSV, DataFrame for dataframe)
            
        Raises:
            ValueError: If format_type is not supported
            ImportError: If pandas is required but not available
        """
        format_type = format_type.lower()
        
        if format_type not in self.formatters:
            raise ValueError(f"Unsupported format type: {format_type}. "
                           f"Supported formats: {list(self.formatters.keys())}")
        
        formatter = self.formatters[format_type]
        
        # Handle filename parameter for CSV formatter
        if format_type == 'csv':
            return formatter.format(data, filename=filename, **kwargs)
        else:
            return formatter.format(data, **kwargs)
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported output formats.
        
        Returns:
            List of supported format names
        """
        return list(self.formatters.keys())
    
    def is_format_available(self, format_type: str) -> bool:
        """Check if a format is available (e.g., pandas for DataFrame).
        
        Args:
            format_type: Format to check
            
        Returns:
            True if format is available, False otherwise
        """
        format_type = format_type.lower()
        
        if format_type not in self.formatters:
            return False
        
        if format_type == 'dataframe':
            return PANDAS_AVAILABLE
        
        return True


# Utility functions for easy formatting
def format_output(
    data: Any, 
    format_type: str = 'json', 
    filename: Optional[str] = None,
    **kwargs
) -> Union[str, Any]:
    """Convenience function to format data.
    
    Args:
        data: Data to format
        format_type: Output format ('json', 'csv', 'dataframe')
        filename: Optional filename for CSV output
        **kwargs: Additional formatting options
        
    Returns:
        Formatted data
    """
    formatter = OutputFormatter()
    return formatter.format(data, format_type, filename, **kwargs)


def to_json(data: Any, **kwargs) -> str:
    """Convert data to JSON format.
    
    Args:
        data: Data to format
        **kwargs: Additional JSON options
        
    Returns:
        JSON formatted string
    """
    return format_output(data, 'json', **kwargs)


def to_csv(data: Any, filename: Optional[str] = None, **kwargs) -> str:
    """Convert data to CSV format.
    
    Args:
        data: Data to format
        filename: Optional filename to save to
        **kwargs: Additional CSV options
        
    Returns:
        CSV formatted string (or empty string if filename provided)
    """
    return format_output(data, 'csv', filename=filename, **kwargs)


def to_dataframe(data: Any, **kwargs) -> 'pd.DataFrame':
    """Convert data to pandas DataFrame format.
    
    Args:
        data: Data to format
        **kwargs: Additional DataFrame options
        
    Returns:
        pandas DataFrame
        
    Raises:
        ImportError: If pandas is not available
    """
    return format_output(data, 'dataframe', **kwargs)


# Format detection utilities
def detect_data_type(data: Any) -> str:
    """Detect the type of data being formatted.
    
    Args:
        data: Data to analyze
        
    Returns:
        String representing the data type
    """
    if isinstance(data, list):
        if data and hasattr(data[0], 'to_dict'):
            return f"list_of_{data[0].__class__.__name__.lower()}s"
        return "list"
    elif isinstance(data, dict):
        # Check for API response patterns
        for field in ['bars', 'quotes', 'trades', 'snapshots', 'news']:
            if field in data:
                return f"api_response_with_{field}"
        return "dict"
    elif hasattr(data, 'to_dict'):
        return data.__class__.__name__.lower()
    else:
        return type(data).__name__.lower()


def suggest_format(data: Any) -> str:
    """Suggest the best format for the given data.
    
    Args:
        data: Data to analyze
        
    Returns:
        Suggested format name
    """
    data_type = detect_data_type(data)
    
    # Single objects work well with JSON
    if data_type in ['bar', 'quote', 'trade', 'snapshot', 'news']:
        return 'json'
    
    # Lists work well with CSV or DataFrame
    elif data_type.startswith('list_of_'):
        return 'csv'
    
    # API responses work well with JSON
    elif data_type.startswith('api_response_with_'):
        return 'json'
    
    # Default to JSON
    else:
        return 'json'