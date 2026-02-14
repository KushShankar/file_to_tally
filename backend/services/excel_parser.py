"""
Excel file parsing service
"""
import pandas as pd
from pathlib import Path
from typing import Tuple, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ExcelParser:
    """Parse Excel files and extract data"""
    
    @staticmethod
    def detect_header_row(df: pd.DataFrame) -> int:
        """
        Detect the header row by finding the first row with mostly non-null values
        """
        for idx in range(min(10, len(df))):  # Check first 10 rows
            row = df.iloc[idx]
            non_null_count = row.notna().sum()
            if non_null_count >= len(row) * 0.5:  # At least 50% non-null
                return idx
        return 0
    
    @staticmethod
    def parse_file(file_path: Path) -> Tuple[List[str], List[Dict[str, Any]], int]:
        """
        Parse Excel/CSV file and return columns, sample data, and row count
        
        Returns:
            Tuple of (column_names, sample_data, total_rows)
        """
        try:
            # Read file based on extension
            if file_path.suffix.lower() == '.csv':
                df = pd.read_csv(file_path)
            else:
                # Try to detect header row for Excel files
                df_temp = pd.read_excel(file_path, header=None, nrows=10)
                header_row = ExcelParser.detect_header_row(df_temp)
                df = pd.read_excel(file_path, header=header_row)
            
            # Clean column names
            df.columns = df.columns.astype(str).str.strip()
            
            # Remove completely empty rows
            df = df.dropna(how='all')
            
            # Get column names
            columns = df.columns.tolist()
            
            # Get sample data (first 5 rows)
            sample_data = df.head(5).fillna('').to_dict('records')
            
            # Convert all values to strings for JSON serialization
            for row in sample_data:
                for key in row:
                    if pd.isna(row[key]):
                        row[key] = ''
                    else:
                        row[key] = str(row[key])
            
            total_rows = len(df)
            
            logger.info(f"Parsed file: {file_path.name}, Columns: {len(columns)}, Rows: {total_rows}")
            
            return columns, sample_data, total_rows
            
        except Exception as e:
            logger.error(f"Error parsing file {file_path}: {str(e)}")
            raise ValueError(f"Failed to parse Excel file: {str(e)}")
    
    @staticmethod
    def read_all_data(file_path: Path) -> pd.DataFrame:
        """
        Read all data from Excel/CSV file
        
        Returns:
            DataFrame with all data
        """
        try:
            if file_path.suffix.lower() == '.csv':
                df = pd.read_csv(file_path)
            else:
                df_temp = pd.read_excel(file_path, header=None, nrows=10)
                header_row = ExcelParser.detect_header_row(df_temp)
                df = pd.read_excel(file_path, header=header_row)
            
            # Clean column names
            df.columns = df.columns.astype(str).str.strip()
            
            # Remove completely empty rows
            df = df.dropna(how='all')
            
            return df
            
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {str(e)}")
            raise ValueError(f"Failed to read Excel file: {str(e)}")
