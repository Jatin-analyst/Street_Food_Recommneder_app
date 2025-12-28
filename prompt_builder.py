# -*- coding: utf-8 -*-
"""
Prompt Builder for Delhi Street Food App
Constructs structured prompts for Kiro AI integration
"""

from dataclasses import dataclass


@dataclass
class UserQuery:
    """User query data structure"""
    area: str
    time_preference: str
    food_preferences: str
    budget_category: str


class PromptBuilder:
    """Builds structured prompts for Kiro AI agent"""
    
    def __init__(self):
        self.system_instructions = self._get_system_instructions()
    
    def build_prompt(self, context, user_query):
        """
        Build a complete prompt combining context and user query
        
        Args:
            context: Loaded product.md context from ContextLoader
            user_query: User's preferences and requirements
            
        Returns:
            Formatted prompt string for Kiro AI
        """
        try:
            # Validate inputs
            self._validate_inputs(context, user_query)
            
            # Build prompt sections
            prompt_parts = [
                self._build_system_section(),
                self._build_context_section(context),
                self._build_user_query_section(user_query),
                self._build_response_format_section()
            ]
            
            # Join all parts
            full_prompt = "\n\n".join(prompt_parts)
            
            return full_prompt
            
        except Exception as e:
            raise Exception("Error building prompt: {}".format(str(e)))
    
    def _get_system_instructions(self):
        """Core system instructions for AI behavior"""
        return """You are a Delhi street food expert and local guide. You have deep knowledge of Delhi's street food scene and speak like a local Delhiite. Your job is to provide authentic, practical recommendations based ONLY on the local knowledge provided to you.

CRITICAL RULES:
- Use ONLY the information provided in the CONTEXT section below
- Never use external knowledge or make up information
- Respond like a friendly local Delhi person who knows the real street food scene
- Include practical tips about timing, crowds, and hygiene
- Use local expressions and slang when appropriate
- Always mention prices in Indian Rupees (₹)
- If you don't have information about a specific area or food, say so honestly"""
    
    def _build_system_section(self):
        """Build the system instruction section"""
        return "SYSTEM INSTRUCTIONS:\n{}".format(self.system_instructions)
    
    def _build_context_section(self, context):
        """Build the context section with all local knowledge"""
        context_parts = []
        
        # Add raw content (most comprehensive)
        if 'raw_content' in context:
            context_parts.append("=== COMPLETE LOCAL KNOWLEDGE BASE ===")
            context_parts.append(context['raw_content'])
        
        # Add structured summaries for easy access
        context_parts.append("\n=== QUICK REFERENCE ===")
        
        # Areas
        if 'areas' in context and context['areas']:
            context_parts.append("Available Areas: {}".format(', '.join(context['areas'])))
        
        # Response guidelines
        if 'response_guidelines' in context and context['response_guidelines']:
            context_parts.append("Response Guidelines:")
            for guideline in context['response_guidelines']:
                context_parts.append("- {}".format(guideline))
        
        # Local tips
        if 'local_tips' in context and context['local_tips']:
            context_parts.append("Local Tips:")
            for tip in context['local_tips'][:5]:  # Limit to first 5 tips
                context_parts.append("- {}".format(tip))
        
        return "CONTEXT:\n{}".format(chr(10).join(context_parts))
    
    def _build_user_query_section(self, user_query):
        """Build the user query section"""
        query_parts = [
            "USER QUERY:",
            "Area: {}".format(user_query.area),
            "Time: {}".format(user_query.time_preference),
            "Food Preferences: {}".format(user_query.food_preferences),
            "Budget: {}".format(user_query.budget_category)
        ]
        
        # Create natural language query
        natural_query = self._create_natural_query(user_query)
        query_parts.append("Natural Query: {}".format(natural_query))
        
        return "\n".join(query_parts)
    
    def _create_natural_query(self, user_query):
        """Convert structured query to natural language"""
        query_parts = []
        
        # Add area and time
        if user_query.area and user_query.time_preference:
            query_parts.append("Street food recommendations for {} during {}".format(user_query.area, user_query.time_preference.lower()))
        elif user_query.area:
            query_parts.append("Street food recommendations for {}".format(user_query.area))
        
        # Add preferences
        if user_query.food_preferences:
            query_parts.append("looking for {}".format(user_query.food_preferences))
        
        # Add budget
        if user_query.budget_category:
            query_parts.append("with {} budget".format(user_query.budget_category.lower()))
        
        return ", ".join(query_parts) if query_parts else "General street food recommendations"
    
    def _build_response_format_section(self):
        """Build the response format requirements"""
        return """RESPONSE FORMAT:
Please provide your recommendations in the following JSON structure:

{
  "area": "requested area name",
  "recommendations": [
    {
      "food_name": "name of the food item",
      "location": "specific location or area within the locality",
      "price_range": "price in ₹ format (e.g., ₹70-90)",
      "crowd_info": "timing and crowd information",
      "local_tip": "practical local advice",
      "hygiene_rating": "Green/Yellow/Red signal based on local knowledge"
    }
  ],
  "alternative_areas": ["list of nearby areas if no good options in requested area"],
  "local_context": "additional local insights and practical advice"
}

IMPORTANT:
- Respond ONLY with valid JSON
- Include 3-5 recommendations if available
- Use local Delhi expressions and tone in the text fields
- Base everything on the provided context
- If information is not available, mention it honestly"""
    
    def _validate_inputs(self, context, user_query):
        """Validate prompt building inputs"""
        if not context:
            raise ValueError("Context cannot be empty")
        
        if not isinstance(user_query, UserQuery):
            raise ValueError("user_query must be a UserQuery instance")
        
        if not user_query.area:
            raise ValueError("User query must include an area")
        
        # Check if area exists in context
        if 'areas' in context and context['areas']:
            if user_query.area not in context['areas']:
                # This is not an error - we'll let the AI handle unknown areas
                pass
    
    def build_simple_prompt(self, context, area, preferences=""):
        """
        Build a simple prompt for quick queries
        
        Args:
            context: Loaded context
            area: Delhi area name
            preferences: Optional food preferences
            
        Returns:
            Simple prompt string
        """
        user_query = UserQuery(
            area=area,
            time_preference="Evening",  # Default
            food_preferences=preferences,
            budget_category="Mid-range"  # Default
        )
        
        return self.build_prompt(context, user_query)


# Example usage and testing
if __name__ == "__main__":
    from context_loader import ContextLoader
    
    # Test prompt building
    try:
        loader = ContextLoader()
        context = loader.load_product_context()
        
        builder = PromptBuilder()
        
        # Test query
        query = UserQuery(
            area="Connaught Place",
            time_preference="Evening",
            food_preferences="momos and chaat",
            budget_category="Budget-friendly"
        )
        
        prompt = builder.build_prompt(context, query)
        print("Prompt built successfully!")
        print("Prompt length: {} characters".format(len(prompt)))
        print("\n--- PROMPT PREVIEW ---")
        print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
        
    except Exception as e:
        print("Error: {}".format(e))