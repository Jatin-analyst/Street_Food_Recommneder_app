# -*- coding: utf-8 -*-
"""
Kiro Client for Delhi Street Food App
Handles communication with Kiro AI agent
"""

import json
import time
import os
import requests
from dataclasses import dataclass


@dataclass
class FoodRecommendation:
    """Individual food recommendation data structure"""
    food_name: str
    location: str
    price_range: str
    crowd_info: str
    local_tip: str
    hygiene_rating: str = "Yellow"  # Default to Yellow if not specified


@dataclass
class RecommendationResponse:
    """Complete recommendation response data structure"""
    area: str
    recommendations: list
    alternative_areas: list
    local_context: str


class KiroClient:
    """Client for communicating with Kiro AI agent"""
    
    def __init__(self, api_key=None, api_url=None):
        """
        Initialize Kiro client
        
        Args:
            api_key: Kiro API key (if None, will try to get from environment)
            api_url: Kiro API URL (if None, will use default)
        """
        self.api_key = api_key or os.getenv('KIRO_API_KEY')
        self.api_url = api_url or os.getenv('KIRO_API_URL', 'https://api.kiro.ai/v1')
        
        # Configuration
        self.timeout = 30  # seconds
        self.max_retries = 3
        self.retry_delay = 1  # seconds
        
        # Response cache for identical queries
        self._response_cache = {}
    
    def query(self, prompt):
        """
        Send query to Kiro AI and get structured response
        
        Args:
            prompt: Complete prompt string for Kiro AI
            
        Returns:
            RecommendationResponse with parsed recommendations
        """
        try:
            # Check cache first
            cache_key = self._get_cache_key(prompt)
            if cache_key in self._response_cache:
                return self._response_cache[cache_key]
            
            # Send request to Kiro
            raw_response = self._send_kiro_request(prompt)
            
            # Parse response
            parsed_response = self._parse_response(raw_response)
            
            # Cache the response
            self._response_cache[cache_key] = parsed_response
            
            return parsed_response
            
        except Exception as e:
            # Return fallback response on error
            return self._create_fallback_response(str(e))
    
    def _send_kiro_request(self, prompt):
        """
        Send HTTP request to Kiro API with retry logic
        
        Args:
            prompt: Prompt to send
            
        Returns:
            Raw response string from Kiro
        """
        if not self.api_key:
            # For development/demo purposes, return mock response
            return self._get_mock_response(prompt)
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'prompt': prompt,
            'max_tokens': 1000,
            'temperature': 0.7
        }
        
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    "{}/chat/completions".format(self.api_url),
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get('choices', [{}])[0].get('message', {}).get('content', '')
                
                elif response.status_code == 429:  # Rate limit
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                        continue
                    else:
                        raise Exception("Rate limit exceeded")
                
                else:
                    raise Exception("API error: {} - {}".format(response.status_code, response.text))
                    
            except requests.exceptions.Timeout:
                last_error = "Request timeout"
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                    
            except requests.exceptions.ConnectionError:
                last_error = "Connection error"
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                    
            except Exception as e:
                last_error = str(e)
                break
        
        raise Exception("Failed to get response from Kiro after {} attempts. Last error: {}".format(self.max_retries, last_error))
    
    def _get_mock_response(self, prompt):
        """
        Generate mock response for development/demo purposes
        
        Args:
            prompt: Original prompt (used to customize response)
            
        Returns:
            Mock JSON response string
        """
        # Extract area from prompt for more realistic mock
        area = "Connaught Place"  # Default
        if "Area:" in prompt:
            try:
                area_line = [line for line in prompt.split('\n') if line.startswith("Area:")][0]
                area = area_line.split("Area:")[1].strip()
            except:
                pass
        
        mock_response = {
            "area": area,
            "recommendations": [
                {
                    "food_name": "Momos",
                    "location": "Janpath Lane",
                    "price_range": "₹70-90",
                    "crowd_info": "High after 6 PM, best before 7 PM",
                    "local_tip": "Avoid the stalls right at metro exit, walk a bit inside for better quality",
                    "hygiene_rating": "Green"
                },
                {
                    "food_name": "Chaat",
                    "location": "Palika Bazaar area",
                    "price_range": "₹60-120",
                    "crowd_info": "Busy throughout evening",
                    "local_tip": "Try the bhel puri, it's fresh and tasty",
                    "hygiene_rating": "Yellow"
                },
                {
                    "food_name": "Kulfi",
                    "location": "Connaught Circus",
                    "price_range": "₹40-80",
                    "crowd_info": "Popular after dinner",
                    "local_tip": "Perfect for ending your street food tour",
                    "hygiene_rating": "Green"
                }
            ],
            "alternative_areas": ["Karol Bagh", "Lajpat Nagar"],
            "local_context": "Bhai, {} is great for street food! Evening time is perfect, just watch out for the crowds. The momos here are famous among locals.".format(area)
        }
        
        return json.dumps(mock_response, indent=2)
    
    def _parse_response(self, raw_response):
        """
        Parse raw Kiro response into structured format
        
        Args:
            raw_response: Raw JSON string from Kiro
            
        Returns:
            Parsed RecommendationResponse object
        """
        try:
            # Clean the response (remove any markdown formatting)
            cleaned_response = raw_response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()
            
            # Parse JSON
            data = json.loads(cleaned_response)
            
            # Validate required fields
            if not isinstance(data, dict):
                raise ValueError("Response is not a JSON object")
            
            # Extract and validate recommendations
            recommendations = []
            raw_recs = data.get('recommendations', [])
            
            for rec_data in raw_recs:
                if not isinstance(rec_data, dict):
                    continue
                
                recommendation = FoodRecommendation(
                    food_name=rec_data.get('food_name', 'Unknown Food'),
                    location=rec_data.get('location', 'Location not specified'),
                    price_range=rec_data.get('price_range', 'Price varies'),
                    crowd_info=rec_data.get('crowd_info', 'Crowd info not available'),
                    local_tip=rec_data.get('local_tip', 'No specific tips'),
                    hygiene_rating=rec_data.get('hygiene_rating', 'Yellow')
                )
                recommendations.append(recommendation)
            
            # Create response object
            response = RecommendationResponse(
                area=data.get('area', 'Unknown Area'),
                recommendations=recommendations,
                alternative_areas=data.get('alternative_areas', []),
                local_context=data.get('local_context', 'No additional context provided')
            )
            
            return response
            
        except json.JSONDecodeError as e:
            raise Exception("Invalid JSON response from Kiro: {}".format(str(e)))
        except Exception as e:
            raise Exception("Error parsing Kiro response: {}".format(str(e)))
    
    def _create_fallback_response(self, error_message):
        """
        Create fallback response when Kiro is unavailable
        
        Args:
            error_message: Error that occurred
            
        Returns:
            Fallback RecommendationResponse
        """
        fallback_rec = FoodRecommendation(
            food_name="Service Temporarily Unavailable",
            location="Please try again later",
            price_range="N/A",
            crowd_info="Our AI expert is taking a chai break",
            local_tip="Error: {}".format(error_message),
            hygiene_rating="Yellow"
        )
        
        return RecommendationResponse(
            area="Error",
            recommendations=[fallback_rec],
            alternative_areas=[],
            local_context="Sorry yaar, our Delhi expert AI is having some technical issues. Please try again in a few minutes!"
        )
    
    def _get_cache_key(self, prompt):
        """Generate cache key for prompt"""
        # Use hash of prompt for caching
        import hashlib
        return hashlib.md5(prompt.encode()).hexdigest()
    
    def clear_cache(self):
        """Clear response cache"""
        self._response_cache.clear()
    
    def health_check(self):
        """
        Check if Kiro API is available
        
        Returns:
            True if API is healthy, False otherwise
        """
        try:
            test_prompt = "Test connection"
            self._send_kiro_request(test_prompt)
            return True
        except:
            return False


# Example usage and testing
if __name__ == "__main__":
    # Test Kiro client
    client = KiroClient()
    
    try:
        # Test with mock response
        test_prompt = """SYSTEM INSTRUCTIONS:
You are a Delhi street food expert.

CONTEXT:
Test context

USER QUERY:
Area: Connaught Place
Time: Evening
Food Preferences: momos
Budget: Budget-friendly"""
        
        response = client.query(test_prompt)
        print("Kiro client test successful!")
        print("Area: {}".format(response.area))
        print("Recommendations: {}".format(len(response.recommendations)))
        print("First recommendation: {}".format(response.recommendations[0].food_name))
        
    except Exception as e:
        print("Error: {}".format(e))