"""
Simple Hindi Translation App using Google Translate
User-friendly interface for translating names to Hindi
"""

import streamlit as st
import asyncio
from googletrans import Translator
import time
import requests
import json
from urllib.parse import quote
from bs4 import BeautifulSoup
import pandas as pd
import os
from google.transliteration import transliterate_word

# Page configuration
st.set_page_config(
    page_title="Hindi Translation App",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .result-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .hindi-text {
        font-size: 1.5rem;
        color: #2e8b57;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .english-text {
        font-size: 1.2rem;
        color: #333;
        margin: 0.5rem 0;
    }
    .error-box {
        background-color: #ffe6e6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff4444;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'translation_history' not in st.session_state:
    st.session_state.translation_history = []

# Load hospital CSV data
@st.cache_data
def load_hospital_data():
    """Load hospital data from CSV file"""
    try:
        csv_path = os.path.join(os.path.dirname(__file__), 'hospitals_hindi_names_degenericized.csv')
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            return df
        else:
            st.error(f"CSV file not found at: {csv_path}")
            return None
    except Exception as e:
        st.error(f"Error loading CSV file: {e}")
        return None

def search_hospital_in_csv(hospital_name, hospital_df):
    """Search for hospital name in CSV data"""
    if hospital_df is None:
        return None
    
    # Convert to lowercase for case-insensitive search
    hospital_name_lower = hospital_name.lower()
    
    # Try exact match first
    exact_match = hospital_df[hospital_df['lab_name'].str.lower() == hospital_name_lower]
    if not exact_match.empty:
        return exact_match.iloc[0]['hindi_name']
    
    # Try partial match (hospital name contains the search term)
    partial_matches = hospital_df[hospital_df['lab_name'].str.lower().str.contains(hospital_name_lower, na=False)]
    if not partial_matches.empty:
        # Return the first match
        return partial_matches.iloc[0]['hindi_name']
    
    # Try reverse search (search term contains hospital name)
    reverse_matches = hospital_df[hospital_df['lab_name'].str.lower().apply(lambda x: hospital_name_lower in x if pd.notna(x) else False)]
    if not reverse_matches.empty:
        return reverse_matches.iloc[0]['hindi_name']
    
    return None

def translate_person_name(name):
    """Translate a person name from English to Hindi using Google Translate with transliteration fallback"""
    try:
        # First try: Google Translate
        translator = Translator()
        result = translator.translate(name, src='en', dest='hi')
        if result and result.text:
            return result.text
        else:
            st.warning(f"Translation service returned empty result for '{name}'. Trying transliteration...")
            raise Exception("Empty translation result")
    except Exception as e:
        try:
            # Fallback: Google Transliteration API
            st.warning(f"Translation service unavailable for '{name}': {str(e)[:50]}... Trying transliteration...")
            transliteration_result = transliterate_word(name, lang_code='hi')
            if transliteration_result and len(transliteration_result) > 0:
                return f"Transliterated: {transliteration_result[0]}"
            else:
                st.warning(f"Transliteration also failed for '{name}'. Using original name.")
                return name
        except Exception as translit_error:
            st.warning(f"Both translation and transliteration failed for '{name}': {str(translit_error)[:50]}... Using original name.")
            return name

def extract_hindi_hospital_name(text, original_hospital_name):
    """Extract Hindi hospital name from text containing Devanagari script"""
    import re
    
    # Find all Devanagari script text (Hindi)
    hindi_pattern = r'[\u0900-\u097F]+(?:\s+[\u0900-\u097F]+)*'
    hindi_matches = re.findall(hindi_pattern, text)
    
    if hindi_matches:
        # Hospital-related Hindi keywords
        hospital_keywords = ['अस्पताल', 'हॉस्पिटल', 'चिकित्सालय', 'आरोग्यशाला', 'संस्थान', 'महाविद्यालय', 'चिकित्सा', 'आयुर्विज्ञान']
        
        # Common Hindi descriptive/grammatical words to avoid
        descriptive_words = ['का', 'के', 'में', 'है', 'हैं', 'की', 'को', 'से', 'पर', 'तक', 'भी', 'सभी', 'कुछ', 'बहुत', 'यह', 'वह', 'इस', 'उस', 'होता', 'होती', 'होते', 'होतीं']
        
        # Score each Hindi match based on relevance
        scored_matches = []
        
        for hindi_text in hindi_matches:
            score = 0
            text_length = len(hindi_text)
            
            # Length scoring (prefer names that are not too short or too long)
            if 8 <= text_length <= 40:
                score += 3
            elif 5 <= text_length <= 50:
                score += 2
            elif text_length > 50:
                score -= 2  # Penalize very long text (likely descriptions)
            
            # Hospital keyword bonus
            if any(keyword in hindi_text for keyword in hospital_keywords):
                score += 5
            
            # Penalty for descriptive words
            descriptive_count = sum(1 for word in descriptive_words if word in hindi_text)
            score -= descriptive_count * 2
            
            # Bonus for proper nouns (words that start with capital letters in context)
            # This is harder to detect in Hindi, so we use other heuristics
            
            # Penalty for common words that appear in descriptions
            common_words = ['भारत', 'दिल्ली', 'मुंबई', 'बंगलुरु', 'चेन्नई', 'कोलकाता', 'हैदराबाद', 'पुणे', 'अहमदाबाद', 'जयपुर']
            if any(word in hindi_text for word in common_words) and text_length > 20:
                score -= 1  # Slight penalty for location names in long text
            
            # Only consider matches with positive or neutral scores
            if score >= 0:
                scored_matches.append((hindi_text.strip(), score))
        
        # Sort by score (highest first) and return the best match
        if scored_matches:
            scored_matches.sort(key=lambda x: x[1], reverse=True)
            return scored_matches[0][0]
    
    return None

def duckduckgo_html_search(query: str):
    """Search using DuckDuckGo HTML interface (like your script)"""
    try:
        url = "https://duckduckgo.com/html/"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        params = {"q": query}
        response = requests.get(url, headers=headers, params=params, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")
        results = soup.select(".result__a, .result__snippet")  # titles + snippets
        return [r.get_text(strip=True) for r in results]
    except Exception as e:
        st.error(f"Error in HTML search: {e}")
        return []

def search_hospital_name(hospital_name):
    """Search for hospital name using CSV first, then web search as fallback"""
    try:
        # First, try to find the hospital in the CSV file
        hospital_df = load_hospital_data()
        if hospital_df is not None:
            csv_result = search_hospital_in_csv(hospital_name, hospital_df)
            if csv_result:
                return f"From Database: {csv_result}"
        
        # If not found in CSV, fall back to web search
        st.info(f"'{hospital_name}' not found in database. Searching online...")
        
        # Using DuckDuckGo HTML search (like your script) for better results
        search_query = f"official hindi name of {hospital_name}"
        search_results = duckduckgo_html_search(search_query)
        
        # Combine all search results text
        all_text = " ".join(search_results[:10])  # Use first 10 results
        
        # Try to extract Hindi hospital name
        if all_text:
            hindi_hospital_name = extract_hindi_hospital_name(all_text, hospital_name)
            if hindi_hospital_name:
                return f"From Web Search: {hindi_hospital_name}"
        
        # Final fallback: try Google Translate for hospital name
        translator = Translator()
        result = translator.translate(hospital_name, src='en', dest='hi')
        return f"Translated: {result.text}"
        
    except Exception as e:
        st.error(f"Error searching for hospital {hospital_name}: {e}")
        # Fallback to Google Translate
        try:
            translator = Translator()
            result = translator.translate(hospital_name, src='en', dest='hi')
            return f"Translated: {result.text}"
        except:
            return hospital_name

def translate_names_batch(names, category):
    """Translate multiple names from English to Hindi based on category"""
    results = []
    for name in names:
        if name.strip():  # Skip empty names
            if category == "Person Name":
                hindi_name = translate_person_name(name.strip())
            else:  # Hospital
                hindi_name = search_hospital_name(name.strip())
            results.append({
                'english': name.strip(),
                'hindi': hindi_name,
                'category': category
            })
    return results

def display_translation_result(english_name, hindi_name, category=None):
    """Display a single translation result"""
    st.markdown('<div class="result-box">', unsafe_allow_html=True)
    if category:
        st.markdown(f'<div class="english-text">**Category:** {category}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="english-text">**English:** {english_name}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="hindi-text">**Hindi:** {hindi_name}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">Hindi Translation App</h1>', unsafe_allow_html=True)
    st.markdown("**Translate English names to Hindi - Choose your category**")
    
    # Category selection
    category = st.radio(
        "Select Category:",
        ["Person Name", "Hospital"],
        horizontal=True,
        help="Choose whether you want to translate person names or search for hospital information"
    )
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Settings")
        if category == "Person Name":
            st.info("This mode uses Google Translate to convert English person names to Hindi. If unavailable, it falls back to transliteration, then to the original English name.")
        else:
            st.info("This mode first searches the hospital database, then uses web search as fallback to find Hindi names.")
        
        # Clear history button
        if st.button("🗑️ Clear History"):
            st.session_state.translation_history = []
            st.rerun()
        
        # Test fallback button for person names
        if category == "Person Name":
            if st.button("🧪 Test Fallback (Simulate API Error)"):
                st.info("If Google Translate API fails, the app will show a warning and return the original English name.")
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["🔤 Single Translation", "📝 Batch Translation", "📚 History"])
    
    with tab1:
        if category == "Person Name":
            st.markdown("### Single Person Name Translation")
            placeholder_text = "e.g., John Smith, Mary Johnson, Robert Brown"
            help_text = "Enter a single person name to translate to Hindi"
        else:
            st.markdown("### Single Hospital Search")
            placeholder_text = "e.g., Apollo Hospital, Fortis Healthcare, AIIMS"
            help_text = "Enter a hospital name to search for Hindi information"
        
        # Single name input
        with st.form("single_translation_form"):
            english_name = st.text_input(
                f"Enter English {category.lower()}:",
                placeholder=placeholder_text,
                help=help_text
            )
            
            translate_single = st.form_submit_button("🔍 Search/Translate", type="primary")
        
        # Process single translation
        if translate_single and english_name:
            with st.spinner("Processing..."):
                if category == "Person Name":
                    hindi_name = translate_person_name(english_name)
                else:
                    hindi_name = search_hospital_name(english_name)
                
                # Display result
                display_translation_result(english_name, hindi_name, category)
                
                # Add to history
                st.session_state.translation_history.append({
                    'english': english_name,
                    'hindi': hindi_name,
                    'category': category,
                    'timestamp': time.time()
                })
    
    with tab2:
        if category == "Person Name":
            st.markdown("### Batch Person Name Translation")
        else:
            st.markdown("### Batch Hospital Search")
        
        # Batch input options
        batch_option = st.radio(
            "Choose input method:",
            ["Manual Entry", "Paste Text"]
        )
        
        if batch_option == "Manual Entry":
            if category == "Person Name":
                st.markdown("**Enter multiple person names (one per line):**")
                placeholder_text = "John Smith\nMary Johnson\nRobert Brown\nPriya Sharma"
                help_text = "Enter multiple person names, one per line"
            else:
                st.markdown("**Enter multiple hospital names (one per line):**")
                placeholder_text = "Apollo Hospital\nFortis Healthcare\nAIIMS\nMax Hospital"
                help_text = "Enter multiple hospital names, one per line"
            
            batch_text = st.text_area(
                f"{category}s:",
                placeholder=placeholder_text,
                height=150,
                help=help_text
            )
            
            if st.button("🔍 Search/Translate Batch"):
                if batch_text:
                    names = [line.strip() for line in batch_text.split('\n') if line.strip()]
                    if names:
                        with st.spinner(f"Processing {len(names)} {category.lower()}s..."):
                            results = translate_names_batch(names, category)
                            
                            # Display results
                            for result in results:
                                display_translation_result(result['english'], result['hindi'], result['category'])
                                
                                # Add to history
                                st.session_state.translation_history.append({
                                    'english': result['english'],
                                    'hindi': result['hindi'],
                                    'category': result['category'],
                                    'timestamp': time.time()
                                })
                    else:
                        st.warning(f"Please enter at least one {category.lower()}.")
                else:
                    st.warning(f"Please enter some {category.lower()}s to process.")
        
        elif batch_option == "Paste Text":
            if category == "Person Name":
                st.markdown("**Paste text containing person names:**")
                help_text = "Paste text and the app will try to extract person names"
            else:
                st.markdown("**Paste text containing hospital names:**")
                help_text = "Paste text and the app will try to extract hospital names"
            
            pasted_text = st.text_area(
                "Text:",
                placeholder="Paste any text containing names here...",
                height=150,
                help=help_text
            )
            
            if st.button("🔍 Extract and Process Names"):
                if pasted_text:
                    # Simple name extraction (you can improve this)
                    import re
                    # Extract potential names (words that start with capital letters)
                    potential_names = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', pasted_text)
                    
                    if potential_names:
                        # Remove duplicates while preserving order
                        unique_names = list(dict.fromkeys(potential_names))
                        
                        with st.spinner(f"Processing {len(unique_names)} {category.lower()}s..."):
                            results = translate_names_batch(unique_names, category)
                            
                            # Display results
                            for result in results:
                                display_translation_result(result['english'], result['hindi'], result['category'])
                                
                                # Add to history
                                st.session_state.translation_history.append({
                                    'english': result['english'],
                                    'hindi': result['hindi'],
                                    'category': result['category'],
                                    'timestamp': time.time()
                                })
                    else:
                        st.warning(f"No {category.lower()}s found in the text. Make sure names start with capital letters.")
                else:
                    st.warning(f"Please paste some text containing {category.lower()}s.")
    
    with tab3:
        st.markdown("### Translation History")
        
        if st.session_state.translation_history:
            st.markdown(f"**Total translations: {len(st.session_state.translation_history)}**")
            
            # Display history (most recent first)
            for i, entry in enumerate(reversed(st.session_state.translation_history)):
                st.markdown(f"### Translation {len(st.session_state.translation_history) - i}")
                category = entry.get('category', 'Unknown')
                display_translation_result(entry['english'], entry['hindi'], category)
                st.markdown("---")
        else:
            st.info("No translation history yet. Start translating names to see your history here.")
    
    # Footer
    st.markdown("---")
    st.markdown("**About:** This app provides two modes: **Person Name** mode uses Google Translate API with transliteration fallback to convert English person names to Hindi, while **Hospital** mode first searches the hospital database (1,157+ hospitals) and falls back to web search for Hindi names.")

if __name__ == "__main__":
    main()