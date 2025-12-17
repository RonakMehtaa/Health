import httpx
import json
from typing import Dict, List


class OllamaClient:
    """Client for interacting with local Ollama LLM"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3"):
        self.base_url = base_url
        self.model = model
    
    async def generate_insights(self, context: Dict) -> Dict:
        """Generate health insights from structured data"""
        
        # Build the prompt
        prompt = self._build_prompt(context)
        
        # Call Ollama API
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.3,  # Lower temperature for more factual output
                            "top_p": 0.9
                        }
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    generated_text = result.get("response", "")
                    
                    # Parse the response into structured insights
                    insights = self._parse_llm_response(generated_text, context)
                    return insights
                else:
                    return {
                        "error": f"Ollama API error: {response.status_code}",
                        "insights": [],
                        "summary": "Unable to generate insights at this time."
                    }
        
        except Exception as e:
            return {
                "error": str(e),
                "insights": [],
                "summary": "Unable to connect to local LLM. Ensure Ollama is running."
            }
    
    def _build_prompt(self, context: Dict) -> str:
        """Build a structured prompt for the LLM"""
        
        sleep_summary = context.get("sleep_summary", {})
        activity_summary = context.get("activity_summary", {})
        notable_patterns = context.get("notable_patterns", [])
        correlations = context.get("correlations", {})
        
        prompt = """You are a neutral data analyst. Explain patterns and trends in the following health metrics using factual, neutral language.

RULES:
- Do not provide medical advice or diagnosis
- Do not use motivational or coaching language
- Do not say "you should" or give recommendations
- Use phrases like "data shows", "compared to baseline", "trend indicates"
- Be factual and analytical

DATA:
"""
        
        # Add sleep data
        if sleep_summary:
            last_night = sleep_summary.get("last_night", {})
            avg_7day = sleep_summary.get("7_day_average", {})
            avg_30day = sleep_summary.get("30_day_average", {})
            
            prompt += f"\nSLEEP DATA:\n"
            prompt += f"Last night ({last_night.get('date', 'N/A')}):\n"
            prompt += f"  - Sleep duration: {last_night.get('time_asleep_hours', 0)} hours\n"
            prompt += f"  - REM sleep: {last_night.get('rem_percentage', 0)}%\n"
            prompt += f"  - Deep sleep: {last_night.get('deep_percentage', 0)}%\n"
            prompt += f"  - Time awake: {last_night.get('awake_minutes', 0)} minutes\n"
            prompt += f"  - Bedtime: {last_night.get('bedtime', 'N/A')}\n"
            prompt += f"  - Wake time: {last_night.get('wake_time', 'N/A')}\n"
            
            prompt += f"\n7-day average:\n"
            prompt += f"  - Sleep duration: {avg_7day.get('time_asleep_hours', 0)} hours\n"
            prompt += f"  - REM sleep: {avg_7day.get('rem_percentage', 0)}%\n"
            prompt += f"  - Deep sleep: {avg_7day.get('deep_percentage', 0)}%\n"
            
            if avg_30day:
                prompt += f"\n30-day average:\n"
                prompt += f"  - Sleep duration: {avg_30day.get('time_asleep_hours', 0)} hours\n"
                prompt += f"  - REM sleep: {avg_30day.get('rem_percentage', 0)}%\n"
                prompt += f"  - Deep sleep: {avg_30day.get('deep_percentage', 0)}%\n"
        
        # Add activity data
        if activity_summary:
            yesterday = activity_summary.get("yesterday", {})
            avg_7day = activity_summary.get("7_day_average", {})
            
            prompt += f"\nACTIVITY DATA:\n"
            prompt += f"Yesterday ({yesterday.get('date', 'N/A')}):\n"
            prompt += f"  - Steps: {yesterday.get('steps', 0):,}\n"
            prompt += f"  - Active calories: {yesterday.get('move_calories', 0)}\n"
            prompt += f"  - Stand hours: {yesterday.get('stand_hours', 0)}\n"
            
            prompt += f"\n7-day average:\n"
            prompt += f"  - Steps: {avg_7day.get('steps', 0):,}\n"
            prompt += f"  - Active calories: {avg_7day.get('move_calories', 0)}\n"
            prompt += f"  - Stand hours: {avg_7day.get('stand_hours', 0)}\n"
        
        # Add notable patterns
        if notable_patterns:
            prompt += f"\nNOTABLE PATTERNS:\n"
            for pattern in notable_patterns:
                prompt += f"  - {pattern}\n"
        
        # Add correlations
        if correlations:
            prompt += f"\nCORRELATIONS:\n"
            for key, value in correlations.items():
                prompt += f"  - {key}: {value}\n"
        
        prompt += """\n
Provide 3-4 brief observations about the data. Focus on:
1. How recent data compares to averages
2. Any notable deviations or patterns
3. Potential relationships between activity and sleep (if correlation data is available)

Format each observation as a single paragraph. Be concise and factual.
"""
        
        return prompt
    
    def _parse_llm_response(self, response_text: str, context: Dict) -> Dict:
        """Parse LLM response into structured format"""
        
        # Split response into paragraphs
        paragraphs = [p.strip() for p in response_text.split('\n\n') if p.strip()]
        
        insights = []
        categories = ['sleep_duration', 'sleep_stages', 'activity_correlation', 'general_pattern']
        
        for i, paragraph in enumerate(paragraphs[:4]):  # Take up to 4 paragraphs
            if len(paragraph) > 20:  # Filter out very short lines
                insights.append({
                    'category': categories[i] if i < len(categories) else 'general_pattern',
                    'observation': paragraph
                })
        
        # Generate a brief summary
        summary = paragraphs[0] if paragraphs else "Insufficient data for analysis."
        
        return {
            'insights': insights,
            'summary': summary,
            'model': self.model
        }
    
    async def check_connection(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except:
            return False
