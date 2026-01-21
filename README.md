<img width="983" height="519" alt="image" src="https://github.com/user-attachments/assets/cd2f8f28-939e-4c12-a158-af8ae0f94af1" />



# TradingView Headline Scrape-N-Read (Lite)

**TradingView Headline Scrape-N-Read Lite** is a lightweight, Python tool that continuously scrapes live headlines from TradingView’s News Flow and reads new headlines aloud using text-to-speech (TTS).

Designed for traders, analysts, and anyone who wants **real-time market news while keeping their eyes on the charts**.

---

## ✨ Features

- **Live headline scraping** from TradingView News Flow  
- **Text-to-Speech (TTS)** reads new headlines automatically  
- Displays **local time** for each headline  
- **Duplicate filtering** (headline + provider + timestamp)  
- **Cross-platform support** (Windows, macOS, Linux)  
- **Customizable URL** via external config file  
- Lightweight & headless (no visible browser)

---

## 📸 What It Does

- Loads TradingView’s News Flow page on a headless browser
- Scrapes headlines, providers, and timestamps  
- Prints them in chronological order  
- Continuously refreshes the feed  
- Alerts you with a sound + reads **only new headlines** aloud  

---

## 🧰 Requirements

- **Python 3.9+**
- Supported OS:
  - Windows

### Python Dependencies

```
pip install playwright pyttsx3 playsound3
```
### Playwright Browser Setup
```
playwright install
```
### Run the script:
```
python scrape_n_read_lite.py
```

Once Running:
- Headlines print to the console
- New headlines trigger:
- - A system sound
- - Spoken headline via TTS
- Press Ctrl+C to exit

### Configuration:
### Custom News URL (Optional)
Create a file named:
```
Scrape-n-Read_LITE_URL.txt
```
Place it in the same directory as the script and add a valid URL, for example:
```
https://www.tradingview.com/news-flow/?market=crypto
```
If the file is missing or invalid, the script falls back to the default TradingView News Flow.

## Platform Notes
Sounds:
- Windows: Uses system chime

### DISCLAIMER
THIS PROJECT IS FOR EDUCATIONAL AND PERSONAL USE ONLY. IT IS NOT AFFILIATED WITH TRADINGVIEW. USE RESPONSIBLY AND RESPECT WEBSITE TERMS OF SERVICE.
