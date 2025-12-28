# -*- coding: utf-8 -*-
"""
Recommendation Engine for Delhi Street Food App
Main orchestration class that coordinates all components
"""

import json
from dataclasses import asdict

from context_loader import ContextLoader
from prompt_builder import PromptBuilder, UserQuery
from kiro_client import KiroClient, RecommendationResponse, FoodRecommendation


class RecommendationEngine:
    """Main engine that orchestrates context loading, prompt building, and AI querying"""
    
    def __init__(self, context_file_path=None):
        """
        Initialize the recommendation engine
        
        Args:
            context_file_path: Optional path to product.md file
        """
        self.context_loader = ContextLoader(context_file_path) if context_file_path else ContextLoader()
        self.prompt_builder = PromptBuilder()
        self.kiro_client = KiroClient()
        
        # Cache for loaded context
        self._context_cache = None
    
    def get_recommendations(self, 
                          area, 
                          time_preference="Evening",
                          food_preferences="",
                          budget_category="Mid-range"):
        """
        Get street food recommendations for given parameters
        
        Args:
            area: Delhi area name
            time_preference: Time of day (Morning, Afternoon, Evening, Late Night)
            food_preferences: Specific food preferences or dietary requirements
            budget_category: Budget category (Budget-friendly, Mid-range, Premium)
            
        Returns:
            RecommendationResponse with structured recommendations
        """
        try:
            # Load context
            context = self._get_context()
            
            # Validate and process area
            processed_area = self._process_area_input(area, context)
            
            # Create user query
            user_query = UserQuery(
                area=processed_area,
                time_preference=time_preference,
                food_preferences=food_preferences,
                budget_category=budget_category
            )
            
            # Build prompt
            prompt = self.prompt_builder.build_prompt(context, user_query)
            
            # Get AI response
            response = self.kiro_client.query(prompt)
            
            # Post-process response
            processed_response = self._post_process_response(response, user_query, context)
            
            return processed_response
            
        except Exception as e:
            return self._create_error_response(str(e), area)
    
    def get_areas_list(self):
        """
        Get list of available Delhi areas
        
        Returns:
            List of area names
        """
        try:
            context = self._get_context()
            return context.get('areas', [])
        except Exception:
            # Return default areas if context loading fails
            return [
                "Connaught Place", "Lajpat Nagar", "Chandni Chowk", 
                "Karol Bagh", "Greater Kailash", "Alaknanda"
            ]
    
    def get_area_info(self, area):
        """
        Get detailed information about a specific area
        
        Args:
            area: Area name
            
        Returns:
            Dictionary with area information
        """
        try:
            context = self._get_context()
            
            # Get food options for the area
            food_options = context.get('food_options', {}).get(area, [])
            
            # Get time recommendations
            time_recs = context.get('time_recommendations', {})
            
            return {
                'area': area,
                'available': area in context.get('areas', []),
                'food_options': food_options,
                'time_recommendations': time_recs
            }
            
        except Exception as e:
            return {
                'area': area,
                'available': False,
                'error': str(e),
                'food_options': [],
                'time_recommendations': {}
            }
    
    def validate_user_input(self, area, time_preference, 
                          food_preferences, budget_category):
        """
        Validate user input parameters
        
        Args:
            area: Area name
            time_preference: Time preference
            food_preferences: Food preferences
            budget_category: Budget category
            
        Returns:
            Dictionary with validation results (empty if all valid)
        """
        errors = {}
        
        try:
            context = self._get_context()
            
            # Validate area
            if not area or not area.strip():
                errors['area'] = "Please select an area"
            elif area not in context.get('areas', []):
                # Check for similar areas
                similar_areas = self._find_similar_areas(area, context.get('areas', []))
                if similar_areas:
                    errors['area'] = "Area '{}' not found. Did you mean: {}?".format(area, ', '.join(similar_areas[:3]))
                else:
                    errors['area'] = "Area '{}' not available in our database".format(area)
            
            # Validate time preference
            valid_times = ["Morning", "Afternoon", "Evening", "Late Night"]
            if time_preference not in valid_times:
                errors['time_preference'] = "Time preference must be one of: {}".format(', '.join(valid_times))
            
            # Validate budget category
            valid_budgets = ["Budget-friendly", "Mid-range", "Premium"]
            if budget_category not in valid_budgets:
                errors['budget_category'] = "Budget category must be one of: {}".format(', '.join(valid_budgets))
            
        except Exception as e:
            errors['general'] = "Validation error: {}".format(str(e))
        
        return errors
    
    def _get_context(self):
        """Get context with caching"""
        if self._context_cache is None:
            self._context_cache = self.context_loader.load_product_context()
        return self._context_cache
    
    def _process_area_input(self, area, context):
        """
        Process and validate area input
        
        Args:
            area: Raw area input
            context: Loaded context
            
        Returns:
            Processed area name
        """
        if not area:
            raise ValueError("Area is required")
        
        area = area.strip()
        available_areas = context.get('areas', [])
        
        # Exact match
        if area in available_areas:
            return area
        
        # Case-insensitive match
        for available_area in available_areas:
            if area.lower() == available_area.lower():
                return available_area
        
        # Partial match
        for available_area in available_areas:
            if area.lower() in available_area.lower() or available_area.lower() in area.lower():
                return available_area
        
        # If no match found, return original (let AI handle it)
        return area
    
    def _find_similar_areas(self, area, available_areas):
        """Find similar area names for suggestions"""
        area_lower = area.lower()
        similar = []
        
        for available_area in available_areas:
            available_lower = available_area.lower()
            
            # Check for partial matches
            if (area_lower in available_lower or 
                available_lower in area_lower or
                any(word in available_lower for word in area_lower.split())):
                similar.append(available_area)
        
        return similar
    
    def _post_process_response(self, response, 
                             user_query, context):
        """
        Post-process AI response for quality and consistency
        
        Args:
            response: Raw AI response
            user_query: Original user query
            context: Loaded context
            
        Returns:
            Processed response
        """
        # Ensure we have recommendations
        if not response.recommendations:
            return self._create_fallback_recommendations(user_query, context)
        
        # Validate and clean recommendations
        cleaned_recommendations = []
        for rec in response.recommendations:
            # Ensure all fields are present and reasonable
            cleaned_rec = FoodRecommendation(
                food_name=rec.food_name or "Street Food Item",
                location=rec.location or "Near {}".format(user_query.area),
                price_range=rec.price_range or "Price varies",
                crowd_info=rec.crowd_info or "Crowd info not available",
                local_tip=rec.local_tip or "Enjoy the local flavors!",
                hygiene_rating=rec.hygiene_rating if rec.hygiene_rating in ["Green", "Yellow", "Red"] else "Yellow"
            )
            cleaned_recommendations.append(cleaned_rec)
        
        # Update response
        response.recommendations = cleaned_recommendations
        
        # Ensure area is set correctly
        if not response.area or response.area == "Unknown Area":
            response.area = user_query.area
        
        return response
    
    def _create_fallback_recommendations(self, user_query, context):
        """Create fallback recommendations when AI doesn't provide any"""
        
        # Try to get area-specific recommendations from context
        area_foods = context.get('food_options', {}).get(user_query.area, [])
        
        recommendations = []
        if area_foods:
            # Use context data to create recommendations
            for food_data in area_foods[:3]:  # Limit to 3
                rec = FoodRecommendation(
                    food_name=food_data.get('name', 'Local Specialty'),
                    location="{} area".format(user_query.area),
                    price_range=food_data.get('price', 'Price varies'),
                    crowd_info="Popular during {}".format(user_query.time_preference.lower()),
                    local_tip=food_data.get('details', 'A local favorite!'),
                    hygiene_rating="Yellow"
                )
                recommendations.append(rec)
        else:
            # Generic fallback
            rec = FoodRecommendation(
                food_name="Local Street Food",
                location="{} market area".format(user_query.area),
                price_range="Rs.50-150",
                crowd_info="Check local timings",
                local_tip="Ask locals for the best spots in this area",
                hygiene_rating="Yellow"
            )
            recommendations.append(rec)
        
        return RecommendationResponse(
            area=user_query.area,
            recommendations=recommendations,
            alternative_areas=self._get_nearby_areas(user_query.area, context),
            local_context="Limited information available for {}. These are general recommendations.".format(user_query.area)
        )
    
    def _get_nearby_areas(self, area, context):
        """Get nearby areas as alternatives"""
        all_areas = context.get('areas', [])
        
        # Simple logic: return first few areas that aren't the current one
        nearby = [a for a in all_areas if a != area][:3]
        
        return nearby
    
    def _create_error_response(self, error_message, area):
        """Create error response"""
        error_rec = FoodRecommendation(
            food_name="Error",
            location="Service unavailable",
            price_range="N/A",
            crowd_info="Please try again",
            local_tip="Error: {}".format(error_message),
            hygiene_rating="Red"
        )
        
        return RecommendationResponse(
            area=area,
            recommendations=[error_rec],
            alternative_areas=[],
            local_context="Sorry, we're having technical difficulties. Please try again later."
        )
    
    def refresh_context(self):
        """Refresh the context cache (for hot reloading)"""
        self._context_cache = None
        self.kiro_client.clear_cache()
    
    def to_dict(self, response):
        """Convert response to dictionary for JSON serialization"""
        return {
            'area': response.area,
            'recommendations': [asdict(rec) for rec in response.recommendations],
            'alternative_areas': response.alternative_areas,
            'local_context': response.local_context
        }


# Example usage and testing
if __name__ == "__main__":
    # Test recommendation engine
    engine = RecommendationEngine()
    
    try:
        # Test getting areas
        areas = engine.get_areas_list()
        print("Available areas: {}".format(len(areas)))
        print("First few areas: {}".format(areas[:5]))
        
        # Test validation
        errors = engine.validate_user_input("Connaught Place", "Evening", "momos", "Budget-friendly")
        print("Validation errors: {}".format(errors))
        
        # Test recommendations
        response = engine.get_recommendations(
            area="Connaught Place",
            time_preference="Evening",
            food_preferences="momos and chaat",
            budget_category="Budget-friendly"
        )
        
        print("\nRecommendations for {}:".format(response.area))
        for i, rec in enumerate(response.recommendations, 1):
            print("{}. {} at {} ({})".format(i, rec.food_name, rec.location, rec.price_range))
        
        print("\nLocal context: {}".format(response.local_context))
        
    except Exception as e:
        print("Error: {}".format(e))