# Hindi Translation Agent for Healthcare Facilities

A comprehensive Python application for translating English healthcare facility names to Hindi, with a focus on Community Health Centers (CHCs), Primary Health Centers (PHCs), and District Hospitals across Uttar Pradesh, India.

## 🏥 Overview

This project provides an intelligent translation system that converts English healthcare facility names to their proper Hindi equivalents, ensuring accurate localization for healthcare data management and reporting systems.

## ✨ Features

- **Comprehensive Translation**: Converts 1000+ healthcare facility names from English to Hindi
- **Smart Pattern Recognition**: Handles various naming patterns including:
  - Community Health Centers (CHC)
  - Primary Health Centers (PHC) 
  - District Hospitals
  - Women's Hospitals
  - Mental Health Facilities
- **Area Name Translation**: Converts English area/district names to Hindi
- **Data Cleaning**: Removes formatting issues like triple quotes and malformed entries
- **Streamlit Web Interface**: User-friendly web application for interactive translation
- **CSV Processing**: Batch processing of healthcare facility data

## 📁 Project Structure

```
hindi_translation_agent/
├── ui/
│   ├── streamlit_app.py                    # Main Streamlit web application
│   ├── hospitals_hindi_names_degenericized.csv  # Processed healthcare facility data
│   ├── sanitize_hindi_names.py            # Data cleaning utilities
│   └── set_hindi_from_labname_overrides.py # Translation override handling
├── .gitignore                              # Git ignore file
└── README.md                               # Project documentation
```

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- pip or conda package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd hindi_translation_agent
   ```

2. **Install dependencies**
   ```bash
   pip install streamlit pandas
   ```

3. **Run the Streamlit application**
   ```bash
   streamlit run ui/streamlit_app.py
   ```

4. **Access the web interface**
   - Open your browser and go to `http://localhost:8501`

## 📊 Data Processing

### Input Data Format
The application processes CSV files with the following structure:
```csv
lab_name,hindi_name
CHC RATH,सामुदायिक स्वास्थ्य केंद्र राठ
DISTRICT HOSPITAL AGRA,जिला चिकित्सालय, आगरा
```

### Translation Examples

| English | Hindi |
|---------|-------|
| CHC BABHANI (SONBHADRA) | सामुदायिक स्वास्थ्य केंद्र बभानी (सोनभद्र) |
| DISTRICT WOMEN HOSPITAL GHAZIABAD | जिला महिला चिकित्सालय, गाज़ियाबाद |
| COMBINED HOSPITAL BACHHRAUN AMROHA | संयुक्त चिकित्सालय, अमरोहा |

## 🛠️ Key Components

### 1. Translation Engine
- **Comprehensive Dictionary**: 500+ English to Hindi translations
- **Pattern Matching**: Regex-based identification of English words
- **Context-Aware**: Handles healthcare-specific terminology

### 2. Data Cleaning
- **Quote Removal**: Eliminates malformed triple quotes (`"""`)
- **Format Standardization**: Ensures consistent Hindi formatting
- **Validation**: Checks for remaining English characters

### 3. Web Interface
- **Interactive Translation**: Real-time English to Hindi conversion
- **Batch Processing**: Upload and process CSV files
- **Preview & Download**: Review results before downloading

## 📈 Usage Examples

### Command Line Processing
```python
import pandas as pd

# Load the processed data
df = pd.read_csv('ui/hospitals_hindi_names_degenericized.csv')

# View translated entries
print(df[df['lab_name'].str.contains('CHC', na=False)].head())
```

### Streamlit Web App
```python
# Run the interactive web application
streamlit run ui/streamlit_app.py
```

## 🔧 Configuration

### Translation Dictionary
The translation system uses a comprehensive dictionary mapping English terms to Hindi equivalents:

```python
translations = {
    'CHC': 'सामुदायिक स्वास्थ्य केंद्र',
    'DISTRICT': 'जिला',
    'HOSPITAL': 'चिकित्सालय',
    'WOMEN': 'महिला',
    'COMBINED': 'संयुक्त',
    # ... 500+ more translations
}
```

## 📋 Data Statistics

- **Total Records**: 1,155 healthcare facilities
- **Translation Coverage**: 100% English to Hindi conversion
- **Data Quality**: Clean, validated Hindi translations
- **Geographic Coverage**: Uttar Pradesh, India

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Healthcare facility data from Uttar Pradesh government sources
- Hindi language translation resources
- Streamlit community for the web framework

## 📞 Support

For questions, issues, or contributions, please:
- Open an issue on GitHub
- Contact the development team
- Check the documentation for common solutions

## 🔄 Version History

- **v1.0.0**: Initial release with comprehensive translation system
- **v1.1.0**: Added Streamlit web interface
- **v1.2.0**: Enhanced data cleaning and validation
- **v1.3.0**: Improved translation accuracy and coverage

---

**Made with ❤️ for Healthcare Localization in India**
