# -*- coding: utf-8 -*-
"""
Simplified backend for Delhi Street Food App
Compatible with older Python versions
"""

import os
import re
import json

class SimpleRecommendationEngine:
    """Simplified recommendation engine for demo purposes"""
    
    def __init__(self):
        self.areas = [
            "Connaught Place", "Lajpat Nagar", "Chandni Chowk", 
            "Karol Bagh", "Greater Kailash", "Alaknanda",
            "Pitampura", "Rohini", "Anand Vihar", "Laxmi Nagar",
            "Rajouri Garden", "Janakpuri"
        ]
        
        # Context caching
        self._context_cache = None
        self._context_file_path = '.kiro/specs/delhi-street-food-app/product.md'
        self._last_modified = None
        
        # Load context if available
        self.context = self._load_simple_context()
    
    def _load_simple_context(self):
        """Load basic context from product.md with caching"""
        try:
            if not os.path.exists(self._context_file_path):
                return {'raw_content': '', 'loaded': False}
            
            # Check if file was modified
            current_modified = os.path.getmtime(self._context_file_path)
            
            if (self._context_cache is None or 
                self._last_modified != current_modified):
                
                # Reload context
                with open(self._context_file_path, 'r') as f:
                    content = f.read()
                
                self._context_cache = {
                    'raw_content': content, 
                    'loaded': True,
                    'last_updated': current_modified
                }
                self._last_modified = current_modified
                
                # Extract areas from content if possible
                try:
                    areas_from_content = re.findall(r'### ([^#\n]+)', content)
                    if areas_from_content:
                        # Update areas list with content from file
                        self.areas = sorted(list(set(areas_from_content + self.areas)))
                except:
                    pass
            
            return self._context_cache
            
        except Exception as e:
            return {'raw_content': '', 'loaded': False, 'error': str(e)}
    
    def refresh_context(self):
        """Force refresh of context cache"""
        self._context_cache = None
        self._last_modified = None
        self.context = self._load_simple_context()
        return self.context.get('loaded', False)
    
    def get_recommendations(self, area, time_preference="Evening", 
                          food_preferences="", budget_category="Mid-range"):
        """Get recommendations for given parameters"""
        
        try:
            # Create mock recommendations based on area
            recommendations = []
            
            if area == "Connaught Place":
                recommendations = [
                    {
                        'food_name': 'Momos',
                        'location': 'Janpath Lane',
                        'price_range': 'Rs.70-90',
                        'crowd_info': 'High after 6 PM, best before 7 PM',
                        'local_tip': 'Avoid the stalls right at metro exit, walk a bit inside for better quality',
                        'hygiene_rating': 'Green'
                    },
                    {
                        'food_name': 'Chaat',
                        'location': 'Palika Bazaar area',
                        'price_range': 'Rs.60-120',
                        'crowd_info': 'Busy throughout evening',
                        'local_tip': 'Try the bhel puri, it\'s fresh and tasty',
                        'hygiene_rating': 'Yellow'
                    },
                    {
                        'food_name': 'Kulfi',
                        'location': 'Connaught Circus',
                        'price_range': 'Rs.40-80',
                        'crowd_info': 'Popular after dinner',
                        'local_tip': 'Perfect for ending your street food tour',
                        'hygiene_rating': 'Green'
                    }
                ]
            elif area == "Lajpat Nagar":
                recommendations = [
                    {
                        'food_name': 'Momos',
                        'location': 'Central Market',
                        'price_range': 'Rs.50-80',
                        'crowd_info': 'Very high after 6 PM',
                        'local_tip': 'Famous Dolma Aunty momos - if you can find her!',
                        'hygiene_rating': 'Green'
                    },
                    {
                        'food_name': 'Chole Bhature',
                        'location': 'Main Market',
                        'price_range': 'Rs.80-120',
                        'crowd_info': 'Morning and evening rush',
                        'local_tip': 'Come hungry, the portions are huge',
                        'hygiene_rating': 'Yellow'
                    }
                ]
            elif area == "Chandni Chowk":
                recommendations = [
                    {
                        'food_name': 'Paranthe',
                        'location': 'Paranthe Wali Gali',
                        'price_range': 'Rs.60-120',
                        'crowd_info': 'Extremely crowded, narrow lanes',
                        'local_tip': 'Go early morning or late evening, watch your belongings',
                        'hygiene_rating': 'Yellow'
                    },
                    {
                        'food_name': 'Jalebis',
                        'location': 'Old Famous Jalebi Wala',
                        'price_range': 'Rs.40-80',
                        'crowd_info': 'Always busy',
                        'local_tip': 'Get them fresh and hot, best in the morning',
                        'hygiene_rating': 'Green'
                    }
                ]
            else:
                # Generic recommendations for other areas
                recommendations = [
                    {
                        'food_name': 'Local Specialties',
                        'location': '{} market area'.format(area),
                        'price_range': 'Rs.50-150',
                        'crowd_info': 'Check local timings',
                        'local_tip': 'Ask locals for the best spots in this area',
                        'hygiene_rating': 'Yellow'
                    }
                ]
            
            # Create response
            response = {
                'area': area,
                'recommendations': recommendations,
                'alternative_areas': [a for a in self.areas if a != area][:3],
                'local_context': 'Bhai, {} is great for street food! {} time is perfect, just watch out for the crowds. The food here is famous among locals.'.format(
                    area, time_preference.lower()
                )
            }
            
            return response
            
        except Exception as e:
            # Return error response
            return {
                'area': area,
                'recommendations': [{
                    'food_name': 'Service Temporarily Unavailable',
                    'location': 'Please try again later',
                    'price_range': 'N/A',
                    'crowd_info': 'Our AI expert is taking a chai break',
                    'local_tip': 'Error: {}'.format(str(e)),
                    'hygiene_rating': 'Red'
                }],
                'alternative_areas': [],
                'local_context': 'Sorry yaar, our Delhi expert AI is having some technical issues. Please try again in a few minutes!'
            }
    
    def get_areas_list(self):
        """Get list of available areas"""
        return self.areas
    
    def validate_user_input(self, area, time_preference, food_preferences, budget_category):
        """Validate user input"""
        errors = []
        
        if not area or area not in self.areas:
            errors.append("Please select a valid area")
        
        valid_times = ["Morning", "Afternoon", "Evening", "Late Night"]
        if time_preference not in valid_times:
            errors.append("Please select a valid time preference")
        
        valid_budgets = ["Budget-friendly", "Mid-range", "Premium"]
        if budget_category not in valid_budgets:
            errors.append("Please select a valid budget category")
        
        return errors

# Create global instance
recommendation_engine = SimpleRecommendationEngine()

# Test function
if __name__ == "__main__":
    engine = SimpleRecommendationEngine()
    
    # Test recommendations
    response = engine.get_recommendations("Connaught Place", "Evening", "momos", "Budget-friendly")
    print("Test successful!")
    print("Area: {}".format(response['area']))
    print("Recommendations: {}".format(len(response['recommendations'])))
    print("First recommendation: {}".format(response['recommendations'][0]['food_name']))