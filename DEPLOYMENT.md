# Delhi Street Food Recommender - Deployment Guide

## 🚀 Quick Start

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

### Streamlit Cloud Deployment

1. **Push to GitHub**
   - Create a new repository on GitHub
   - Push all files to the repository

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub account
   - Select your repository
   - Set main file path: `app.py`
   - Deploy!

3. **Configure Secrets (Optional)**
   - In Streamlit Cloud dashboard, go to "Secrets"
   - Add Kiro API credentials if using real AI backend:
   ```toml
   [kiro]
   api_key = "your_kiro_api_key_here"
   base_url = "https://api.kiro.ai"
   ```

## 📁 Project Structure

```
delhi-street-food-app/
├── app.py                    # Main Streamlit application
├── simple_backend.py         # Recommendation engine
├── requirements.txt          # Dependencies
├── integration_test.py       # Complete test suite
├── .streamlit/
│   ├── config.toml          # App configuration
│   └── secrets.toml         # Secrets template
├── .kiro/specs/delhi-street-food-app/
│   └── product.md           # Delhi street food knowledge base
└── Product.md.md            # Original context file
```

## ✅ Features Implemented

- **Complete UI**: Animated food cards, Delhi-themed design, mobile responsive
- **Smart Backend**: Context loading, prompt building, recommendation engine
- **Performance**: Caching, progress indicators, error handling with retries
- **Deployment Ready**: Optimized for Streamlit Cloud with proper configuration

## 🧪 Testing

Run the integration test to verify everything works:
```bash
python integration_test.py
```

## 🎯 Usage

1. Select a Delhi area from the dropdown
2. Choose your preferred time (Morning/Afternoon/Evening/Late Night)
3. Enter food preferences (e.g., "momos", "budget-friendly", "spicy")
4. Select budget range
5. Click "Find Street Food" for personalized recommendations!

## 🔧 Configuration

- **Theme**: Customized Delhi street food colors in `.streamlit/config.toml`
- **Performance**: Caching enabled for faster responses
- **Error Handling**: Graceful fallbacks and retry mechanisms
- **Mobile**: Fully responsive design

## 📱 Demo Mode

The app works in demo mode without external dependencies, showing sample recommendations for popular Delhi areas like Connaught Place, Lajpat Nagar, and Chandni Chowk.

---

**Ready for deployment!** 🎉