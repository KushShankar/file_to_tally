"""
AI-powered column mapping service using OpenRouter
"""
import requests
import json
import logging
from typing import List, Dict
from config import OPENROUTER_API_KEY, OPENROUTER_API_URL, AI_MODEL, TALLY_FIELDS

logger = logging.getLogger(__name__)


class AIMapper:
    """Use AI to intelligently map Excel columns to Tally fields"""
    
    def __init__(self):
        self.api_key = OPENROUTER_API_KEY
        self.api_url = OPENROUTER_API_URL
        self.model = AI_MODEL
    
    def suggest_mappings(self, columns: List[str], voucher_type: str = None) -> Dict[str, Dict]:
        """
        Use AI to suggest column mappings
        
        Args:
            columns: List of Excel column names
            voucher_type: Optional voucher type for context
        
        Returns:
            Dict mapping Excel columns to Tally fields with confidence scores
        """
        try:
            # Create prompt for AI
            prompt = self._create_mapping_prompt(columns, voucher_type)
            
            # Call OpenRouter API
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an expert in Tally ERP and Excel data mapping. You help map Excel columns to Tally fields accurately."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.3,
                }
            )
            
            if response.status_code != 200:
                logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
                return self._fallback_mapping(columns)
            
            result = response.json()
            ai_response = result['choices'][0]['message']['content']
            
            # Parse AI response
            mappings = self._parse_ai_response(ai_response, columns)
            
            logger.info(f"AI suggested {len(mappings)} mappings")
            return mappings
            
        except Exception as e:
            logger.error(f"Error in AI mapping: {str(e)}")
            return self._fallback_mapping(columns)
    
    def _create_mapping_prompt(self, columns: List[str], voucher_type: str = None) -> str:
        """Create prompt for AI mapping"""
        
        tally_field_list = list(TALLY_FIELDS.keys())
        
        prompt = f"""
I have an Excel file with the following columns:
{', '.join(columns)}

I need to map these columns to Tally ERP fields. The available Tally fields are:
{', '.join(tally_field_list)}

"""
        
        if voucher_type:
            prompt += f"\nThe voucher type is: {voucher_type}\n"
        
        prompt += """
Please suggest the best mapping for each Excel column to a Tally field.

Return your response as a JSON object where:
- Keys are the Excel column names (exactly as provided)
- Values are objects with "tally_field" and "confidence" (0.0 to 1.0)

Example format:
{
  "Customer Name": {"tally_field": "party_name", "confidence": 0.95},
  "Invoice Date": {"tally_field": "date", "confidence": 1.0},
  "Total Amount": {"tally_field": "amount", "confidence": 0.9}
}

Only map columns that clearly match a Tally field. If unsure, set confidence below 0.5.
Return ONLY the JSON object, no other text.
"""
        
        return prompt
    
    def _parse_ai_response(self, response: str, columns: List[str]) -> Dict[str, Dict]:
        """Parse AI response and extract mappings"""
        try:
            # Try to extract JSON from response
            response = response.strip()
            
            # Remove markdown code blocks if present
            if response.startswith('```'):
                lines = response.split('\n')
                response = '\n'.join(lines[1:-1])
            
            mappings = json.loads(response)
            
            # Validate and filter mappings
            valid_mappings = {}
            for col, mapping in mappings.items():
                if col in columns and isinstance(mapping, dict):
                    if 'tally_field' in mapping and 'confidence' in mapping:
                        valid_mappings[col] = mapping
            
            return valid_mappings
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {str(e)}")
            return self._fallback_mapping(columns)
    
    def _fallback_mapping(self, columns: List[str]) -> Dict[str, Dict]:
        """
        Fallback mapping using simple string matching
        """
        mappings = {}
        
        for col in columns:
            col_lower = col.lower().strip()
            
            # Try to match against known patterns
            for tally_field, patterns in TALLY_FIELDS.items():
                for pattern in patterns:
                    if pattern in col_lower or col_lower in pattern:
                        mappings[col] = {
                            "tally_field": tally_field,
                            "confidence": 0.7
                        }
                        break
                if col in mappings:
                    break
        
        logger.info(f"Fallback mapping created {len(mappings)} mappings")
        return mappings
