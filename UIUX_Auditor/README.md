# 🌟 AI Website UI/UX Auditor

An advanced AI-powered auditor that analyzes websites for UI/UX, SEO, and Performance, providing real-time AI-generated redesigns, gamified achievement badges, and a professional executive summary.

## 🏆 Hackathon Highlights
- **Interactive Before/After Slider**: Visualize the transformation from the original site to the AI's redesign vision.
- **AI Executive Pitch**: Get a business-focused impact summary for every audit.
- **Gamified Rewards**: Earn medals like **Conversion King**, **UX Visionary**, and **Speed Demon**.
- **Professional PDF Export**: Generate a branded, one-click PDF report for stakeholders.
- **Multi-Device Compatible**: Fully responsive design optimized for mobile, tablet, and desktop.

## 🛠️ Tech Stack
- **Backend**: Python (Flask)
- **AI Intelligence**: OpenAI (GPT-4o)
- **Frontend**: HTML5, Vanilla JS, CSS3 (Glassmorphism & Dark Mode)
- **Analysis Tools**: BeautifulSoup4, Google PageSpeed API patterns.
- **Export Engine**: html2pdf.mJS

## 🚀 Setup & Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/uiux-auditor.git
   cd uiux-auditor
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Browser for Scraper**:
   ```bash
   playwright install chromium
   ```

4. **Set up environment variables**:
   Create a `.env` file in the root directory and add your OpenAI API Key:
   ```env
   OPENAI_API_KEY=your_key_here
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```
   Visit `http://127.0.0.1:5000` in your browser.

## 📖 How to Use
1. Enter any website URL in the input field.
2. Click **Audit Now** and wait for the AI to analyze.
3. Explore the **Comparison Slider** to see the redesign.
4. Check your **Earned Badges** and **Executive Pitch**.
5. Click **Save as PDF** to export your results.

---
*Built for Hackathon Excellence.* 🚀
