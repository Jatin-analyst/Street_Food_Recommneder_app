# -*- coding: utf-8 -*-
"""
Delhi Street Food Recommender App
Main Streamlit application for authentic local street food recommendations
"""

import streamlit as st
import os
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Page configuration
st.set_page_config(
    page_title="Delhi Street Food Guide",
    page_icon="🍛",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Delhi street food vibes
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #ff6b35, #f7931e, #ffd23f);
        background-attachment: fixed;
    }
    
    .stApp {
        background: linear-gradient(135deg, #ff6b35, #f7931e, #ffd23f);
    }
    
    .title {
        text-align: center;
        color: white;
        font-size: 3rem;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        margin-bottom: 2rem;
    }
    
    .subtitle {
        text-align: center;
        color: white;
        font-size: 1.2rem;
        margin-bottom: 3rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }
    
    .food-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        animation: slideInUp 0.6s ease-out;
        position: relative;
        overflow: hidden;
    }
    
    .food-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 12px 25px rgba(0,0,0,0.15);
    }
    
    .food-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
        transition: left 0.5s;
    }
    
    .food-card:hover::before {
        left: 100%;
    }
    
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .food-name {
        font-size: 1.5rem;
        font-weight: bold;
        color: #ff6b35;
        margin-bottom: 10px;
        animation: pulse 2s infinite;
    }
    
    .food-location {
        color: #666;
        font-size: 1rem;
        margin-bottom: 8px;
    }
    
    .food-price {
        color: #f7931e;
        font-weight: bold;
        font-size: 1.1rem;
        margin-bottom: 8px;
    }
    
    .food-tip {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 10px;
        margin: 10px 0;
        border-radius: 5px;
        font-style: italic;
    }
    
    .hygiene-green { color: #28a745; font-weight: bold; }
    .hygiene-yellow { color: #ffc107; font-weight: bold; }
    .hygiene-red { color: #dc3545; font-weight: bold; }
    
    .local-context {
        background: rgba(255,255,255,0.9);
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
        border-left: 5px solid #ff6b35;
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .title {
            font-size: 2rem;
        }
        
        .subtitle {
            font-size: 1rem;
        }
        
        .food-card {
            margin: 15px 0;
            padding: 15px;
        }
        
        .food-name {
            font-size: 1.3rem;
        }
        
        .local-context {
            padding: 15px;
            margin: 15px 0;
        }
    }
    
    @media (max-width: 480px) {
        .title {
            font-size: 1.8rem;
        }
        
        .food-card {
            padding: 12px;
        }
        
        .food-name {
            font-size: 1.2rem;
        }
    }
</style>
""", unsafe_allow_html=True)

def load_areas():
    """Load available areas from context"""
    try:
        # Simple area list for now (can be enhanced with context loader later)
        return [
            "Connaught Place", "Lajpat Nagar", "Chandni Chowk", 
            "Karol Bagh", "Greater Kailash", "Alaknanda",
            "Pitampura", "Rohini", "Anand Vihar", "Laxmi Nagar",
            "Rajouri Garden", "Janakpuri"
        ]
    except:
        return ["Connaught Place", "Lajpat Nagar", "Chandni Chowk"]

def render_food_card(recommendation):
    """Render a food recommendation card"""
    
    # Determine hygiene class
    hygiene_class = "hygiene-yellow"  # default
    if hasattr(recommendation, 'hygiene_rating'):
        if recommendation.hygiene_rating == "Green":
            hygiene_class = "hygiene-green"
        elif recommendation.hygiene_rating == "Red":
            hygiene_class = "hygiene-red"
    
    # Get emoji based on food name
    food_emoji = "🍽️"  # default
    food_name = getattr(recommendation, 'food_name', 'Food Item')
    if 'momo' in food_name.lower():
        food_emoji = "🥟"
    elif 'chaat' in food_name.lower():
        food_emoji = "🥗"
    elif 'kulfi' in food_name.lower():
        food_emoji = "🍦"
    elif 'roll' in food_name.lower():
        food_emoji = "🌯"
    elif 'samosa' in food_name.lower():
        food_emoji = "🥟"
    
    card_html = """
    <div class="food-card">
        <div class="food-name">{} {}</div>
        <div class="food-location">📍 {}</div>
        <div class="food-price">💰 {}</div>
        <div style="margin: 10px 0;">
            <strong>🕐 Crowd Info:</strong> {}
        </div>
        <div class="food-tip">
            <strong>💡 Local Tip:</strong> {}
        </div>
        <div style="margin-top: 10px;">
            <span class="{}">🛡️ Hygiene: {}</span>
        </div>
    </div>
    """.format(
        food_emoji,
        food_name,
        getattr(recommendation, 'location', 'Location not specified'),
        getattr(recommendation, 'price_range', 'Price varies'),
        getattr(recommendation, 'crowd_info', 'Check local timings'),
        getattr(recommendation, 'local_tip', 'Enjoy the local flavors!'),
        hygiene_class,
        getattr(recommendation, 'hygiene_rating', 'Yellow')
    )
    
    st.markdown(card_html, unsafe_allow_html=True)

def validate_user_input(area, time_preference, food_preferences, budget_category):
    """Validate user input and return errors if any"""
    errors = []
    
    # Validate area
    if not area or not area.strip():
        errors.append("Please select an area")
    
    # Validate time preference
    valid_times = ["Morning", "Afternoon", "Evening", "Late Night"]
    if time_preference not in valid_times:
        errors.append("Please select a valid time preference")
    
    # Validate budget category
    valid_budgets = ["Budget-friendly", "Mid-range", "Premium"]
    if budget_category not in valid_budgets:
        errors.append("Please select a valid budget category")
    
    # Food preferences are optional, so no validation needed
    
    return errors

def create_mock_recommendation(food_name, location, price, tip):
    """Create a mock recommendation object for demo"""
    class MockRec:
        def __init__(self, food_name, location, price_range, local_tip):
            self.food_name = food_name
            self.location = location
            self.price_range = price_range
            self.local_tip = local_tip
            self.crowd_info = "Popular in evenings"
            self.hygiene_rating = "Green"
    
    return MockRec(food_name, location, price, tip)

def main():
    """Main application function"""
    
    # Title and subtitle
    st.markdown('<h1 class="title">🍛 Delhi Street Food Guide</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Authentic local recommendations from a Delhi expert</p>', unsafe_allow_html=True)
    
    # Main form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("street_food_form"):
            st.markdown("### 🗺️ Tell us your preferences")
            
            # Area selector
            areas = load_areas()
            selected_area = st.selectbox(
                "📍 Select Area",
                areas,
                help="Choose the Delhi area where you want to explore street food"
            )
            
            # Time preference
            time_preference = st.radio(
                "🕐 Time Preference",
                ["Morning", "Afternoon", "Evening", "Late Night"],
                index=2,  # Default to Evening
                help="When are you planning to visit?"
            )
            
            # Food preferences
            food_preferences = st.text_input(
                "🍽️ Food Preferences",
                placeholder="e.g., momos, chaat, budget-friendly, spicy food",
                help="Tell us what you're craving or any dietary preferences"
            )
            
            # Budget category
            budget_category = st.select_slider(
                "💰 Budget Range",
                options=["Budget-friendly", "Mid-range", "Premium"],
                value="Mid-range",
                help="Choose your preferred price range"
            )
            
            # Submit button
            submitted = st.form_submit_button(
                "🔍 Find Street Food",
                use_container_width=True
            )
            
            if submitted:
                # Validate input
                validation_errors = validate_user_input(
                    selected_area, time_preference, food_preferences, budget_category
                )
                
                if validation_errors:
                    # Show validation errors
                    for error in validation_errors:
                        st.error("❌ {}".format(error))
                else:
                    # Show loading spinner
                    with st.spinner("🤔 Consulting our Delhi street food expert..."):
                        try:
                            # For now, show demo recommendations
                            st.success("🎉 Found some great recommendations for you!")
                            
                            # Demo recommendations based on area
                            if selected_area == "Connaught Place":
                                recommendations = [
                                    create_mock_recommendation(
                                        "Momos", "Janpath Lane", "Rs.70-90",
                                        "Avoid the stalls right at metro exit, walk a bit inside for better quality"
                                    ),
                                    create_mock_recommendation(
                                        "Chaat", "Palika Bazaar area", "Rs.60-120",
                                        "Try the bhel puri, it's fresh and tasty"
                                    ),
                                    create_mock_recommendation(
                                        "Kulfi", "Connaught Circus", "Rs.40-80",
                                        "Perfect for ending your street food tour"
                                    )
                                ]
                            elif selected_area == "Lajpat Nagar":
                                recommendations = [
                                    create_mock_recommendation(
                                        "Momos", "Central Market", "Rs.50-80",
                                        "Famous Dolma Aunty momos - if you can find her!"
                                    ),
                                    create_mock_recommendation(
                                        "Chole Bhature", "Main Market", "Rs.80-120",
                                        "Come hungry, the portions are huge"
                                    )
                                ]
                            else:
                                recommendations = [
                                    create_mock_recommendation(
                                        "Local Specialties", "{} market area".format(selected_area), "Rs.50-150",
                                        "Ask locals for the best spots in this area"
                                    )
                                ]
                            
                            if not recommendations:
                                st.warning("🤷‍♂️ Sorry, we don't have specific recommendations for {} right now. Try a different area or check back later!".format(selected_area))
                            else:
                                # Display recommendations
                                st.markdown("### 🍽️ Recommendations for {}".format(selected_area))
                                
                                for rec in recommendations:
                                    render_food_card(rec)
                                
                                # Local context
                                local_context = "Bhai, {} is great for street food! {} time is perfect, just watch out for the crowds. The food here is famous among locals.".format(
                                    selected_area, time_preference.lower()
                                )
                                
                                st.markdown("""
                                <div class="local-context">
                                    <strong>🗣️ Local Expert Says:</strong><br>
                                    {}
                                </div>
                                """.format(local_context), unsafe_allow_html=True)
                                
                                # Alternative areas
                                other_areas = [area for area in areas if area != selected_area][:3]
                                if other_areas:
                                    st.markdown("**🔄 You might also like:** {}".format(", ".join(other_areas)))
                        
                        except Exception as e:
                            st.error("😞 Oops! Our Delhi street food expert is having a chai break. Please try again in a moment!")
                            st.error("Technical details: {}".format(str(e)))

    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; color: white; margin-top: 2rem;">
            <p>🚧 <strong>Demo Version</strong> - Full AI integration coming soon!</p>
            <p>Made with ❤️ for Delhi food lovers</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()