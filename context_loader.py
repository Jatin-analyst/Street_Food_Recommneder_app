# -*- coding: utf-8 -*-
"""
Context Loader for Delhi Street Food App
Reads and parses the product.md file containing local Delhi street food knowledge
"""

import os
import re
from pathlib import Path
import markdown


class ContextLoader:
    """Loads and parses the product.md file containing Delhi street food knowledge"""
    
    def __init__(self, context_file_path=".kiro/specs/delhi-street-food-app/product.md"):
        self.context_file_path = context_file_path
        self._cached_context = None
        self._file_modified_time = None
    
    def load_product_context(self):
        """
        Load and parse the product.md file
        Returns structured context dictionary with Delhi street food knowledge
        """
        try:
            # Check if file exists
            if not os.path.exists(self.context_file_path):
                raise FileNotFoundError("Product context file not found: {}".format(self.context_file_path))
            
            # Check if we need to reload (file modified or first load)
            current_modified_time = os.path.getmtime(self.context_file_path)
            if (self._cached_context is None or 
                self._file_modified_time != current_modified_time):
                
                self._cached_context = self._parse_context_file()
                self._file_modified_time = current_modified_time
            
            return self._cached_context
            
        except Exception as e:
            raise Exception("Error loading product context: {}".format(str(e)))
    
    def _parse_context_file(self):
        """Parse the markdown file and extract structured data"""
        try:
            with open(self.context_file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            if not content.strip():
                raise ValueError("Product context file is empty")
            
            # Parse different sections
            context = {
                'raw_content': content,
                'areas': self._extract_areas(content),
                'food_options': self._extract_food_options(content),
                'time_recommendations': self._extract_time_recommendations(content),
                'budget_categories': self._extract_budget_categories(content),
                'response_guidelines': self._extract_response_guidelines(content),
                'local_tips': self._extract_local_tips(content)
            }
            
            # Validate required sections
            self._validate_context(context)
            
            return context
            
        except Exception as e:
            raise Exception("Error parsing context file: {}".format(str(e)))
    
    def _extract_areas(self, content):
        """Extract Delhi areas from the content"""
        areas = []
        
        # Look for area sections (### headers with area names)
        area_pattern = r'### ([^#\n]+)'
        matches = re.findall(area_pattern, content)
        
        for match in matches:
            area = match.strip()
            if area and area not in areas:
                areas.append(area)
        
        # Also extract from specific sections
        central_areas = re.findall(r'\*\*([^*]+)\*\*:', content)
        for area in central_areas:
            clean_area = area.strip()
            if clean_area and clean_area not in areas:
                areas.append(clean_area)
        
        return sorted(list(set(areas)))
    
    def _extract_food_options(self, content):
        """Extract food options by area"""
        food_options = {}
        
        # Pattern to match food items with details
        # Looking for patterns like "- **Momos**: Janpath area, ₹70-90"
        food_pattern = r'- \*\*([^*]+)\*\*:([^-\n]+)'
        matches = re.findall(food_pattern, content)
        
        current_area = None
        area_pattern = r'### ([^#\n]+)'
        
        lines = content.split('\n')
        for line in lines:
            # Check if this is an area header
            area_match = re.match(area_pattern, line)
            if area_match:
                current_area = area_match.group(1).strip()
                if current_area not in food_options:
                    food_options[current_area] = []
            
            # Check if this is a food item
            food_match = re.match(food_pattern, line)
            if food_match and current_area:
                food_name = food_match.group(1).strip()
                details = food_match.group(2).strip()
                
                # Extract price if available
                price_match = re.search(r'₹[\d-]+', details)
                price = price_match.group(0) if price_match else "Price varies"
                
                food_options[current_area].append({
                    'name': food_name,
                    'details': details,
                    'price': price
                })
        
        return food_options
    
    def _extract_time_recommendations(self, content):
        """Extract time-based recommendations"""
        time_recs = {}
        
        # Look for time sections
        time_sections = ['Morning', 'Afternoon', 'Evening', 'Late Night']
        
        for time_period in time_sections:
            pattern = rf'### {time_period}[^#]*?\n(.*?)(?=###|\Z)'
            match = re.search(pattern, content, re.DOTALL)
            
            if match:
                section_content = match.group(1)
                
                # Extract best areas
                areas_match = re.search(r'\*\*Best Areas\*\*:([^\n]+)', section_content)
                best_areas = areas_match.group(1).strip() if areas_match else ""
                
                # Extract recommended foods
                rec_match = re.search(r'\*\*Recommended\*\*:([^\n]+)', section_content)
                recommended = rec_match.group(1).strip() if rec_match else ""
                
                time_recs[time_period.lower()] = {
                    'best_areas': best_areas,
                    'recommended_foods': recommended,
                    'raw_content': section_content.strip()
                }
        
        return time_recs
    
    def _extract_budget_categories(self, content):
        """Extract budget category information"""
        budget_cats = {}
        
        # Look for budget sections
        budget_pattern = r'### ([^#\n]*(?:Budget|Range|Premium)[^#\n]*)\n(.*?)(?=###|\Z)'
        matches = re.findall(budget_pattern, content, re.DOTALL)
        
        for category, details in matches:
            # Extract price range
            price_match = re.search(r'₹[\d-]+', details)
            price_range = price_match.group(0) if price_match else ""
            
            budget_cats[category.strip().lower()] = {
                'price_range': price_range,
                'details': details.strip()
            }
        
        return budget_cats
    
    def _extract_response_guidelines(self, content):
        """Extract response guidelines for AI behavior"""
        guidelines = []
        
        # Look for response guidelines section
        guidelines_match = re.search(r'## Response Guidelines\n(.*?)(?=##|\Z)', content, re.DOTALL)
        if guidelines_match:
            guidelines_content = guidelines_match.group(1)
            
            # Extract bullet points
            bullet_pattern = r'- ([^\n]+)'
            guidelines = re.findall(bullet_pattern, guidelines_content)
        
        return guidelines
    
    def _extract_local_tips(self, content):
        """Extract local tips and expressions"""
        tips = []
        
        # Look for tips in various sections
        tip_patterns = [
            r'\*Tip\*:([^\n]+)',
            r'\*Warning\*:([^\n]+)',
            r'\*Note\*:([^\n]+)',
            r'\*Best Practice\*:([^\n]+)'
        ]
        
        for pattern in tip_patterns:
            matches = re.findall(pattern, content)
            tips.extend([tip.strip() for tip in matches])
        
        return tips
    
    def _validate_context(self, context):
        """Validate that the context contains required information"""
        required_fields = ['areas', 'food_options', 'response_guidelines']
        
        for field in required_fields:
            if field not in context or not context[field]:
                raise ValueError("Missing required context field: {}".format(field))
        
        if len(context['areas']) == 0:
            raise ValueError("No Delhi areas found in context")
        
        if len(context['response_guidelines']) == 0:
            raise ValueError("No response guidelines found in context")
    
    def get_areas_list(self):
        """Get list of available Delhi areas"""
        context = self.load_product_context()
        return context['areas']
    
    def get_area_foods(self, area):
        """Get food options for a specific area"""
        context = self.load_product_context()
        return context['food_options'].get(area, [])
    
    def get_time_recommendations(self, time_period):
        """Get recommendations for a specific time period"""
        context = self.load_product_context()
        return context['time_recommendations'].get(time_period.lower(), {})


# Example usage and testing
if __name__ == "__main__":
    loader = ContextLoader()
    try:
        context = loader.load_product_context()
        print("Loaded context with {} areas".format(len(context['areas'])))
        print("Areas: {}...".format(context['areas'][:5]))  # Show first 5 areas
        print("Response guidelines: {}".format(len(context['response_guidelines'])))
    except Exception as e:
        print("Error: {}".format(e))