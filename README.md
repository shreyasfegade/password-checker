# 🔐 Password Strength Checker — Interactive Demo

### 🧾 Overview
An **educational Streamlit web app** that analyzes password strength through both:
1. **Mathematical entropy** (length × character diversity), and  
2. **Pattern-based evaluation** using the `zxcvbn` library (detects common words, substitutions, and sequences).

It also simulates password cracking attempts (purely visual) and generates an **HTML report** explaining the results in clear, layman-friendly language.

---

### 🚀 Live Demo
🔗 [**Open Web App on Streamlit Cloud**]  
*(Please **do not** enter your real passwords — this is for demonstration only.)*

---

### 📂 Project Structure

| File | Purpose |
|------|----------|
| `app.py` | Main Streamlit UI — takes password input, runs analysis, shows tables & animations |
| `strength.py` | Handles mathematical entropy calculations and character set estimation |
| `hashing_demo.py` | Demonstrates hashing algorithms (MD5, SHA256, bcrypt, Argon2) and attacker speed presets |
| `requirements.txt` | Python dependencies |
| `.gitignore` | Ignores virtual environment and build files |

---

### 💡 Features
✅ Real-time password strength feedback  
✅ Entropy & pattern-based scoring (theoretical + realistic)  
✅ Estimated crack time for different attack models (online/offline/hash types)  
✅ Interactive “cracking simulation” animation inspired by Aircrack-ng visuals  
✅ Downloadable HTML report explaining password safety to non-technical users  

---

### 🧮 Core Concepts
- **Entropy (bits)** → measures unpredictability of a password.  
  Formula: `Entropy = Length × log₂(Character set size)`  
- **Brute-force estimation** → converts entropy to total guesses & time.  
- **zxcvbn** → adjusts for real-world human behavior (dictionary words, patterns, dates).  
- **Hashing & attacker models** → illustrates how algorithms like bcrypt and Argon2 slow down brute-force attacks.

---

### 🧰 Installation (Run Locally)

1. Clone the repository:
   ```bash
   git clone https://github.com/<your-username>/password-checker.git
   cd password-checker
2. Create and activate a virtual environment:

python -m venv venv
.\venv\Scripts\Activate.ps1   # (Windows)


3. Install dependencies:

pip install -r requirements.txt


4. Launch the app:

streamlit run app.py


⚠️ Important Notice

This app is for educational and research purposes only.
Do not use it to test or store real credentials.
All calculations and animations are simulations — no passwords are stored or transmitted externally.

🧩 Acknowledgments

This project was built as part of an ACM Projects & Research interview assignment.
The development process included code assistance and explanations generated using ChatGPT (OpenAI) for UI structure, documentation, and concept summarization.
All code and educational content were reviewed and finalized manually.
I plan to make minor stylistic and content edits within 2 days of this repository going public.

📜 License

You are free to use, modify, and share this project for educational or personal purposes.

👤 Author
Shreyas Fegade

Your Name
📧 shreyasf@icloud.com

🌐 GitHub: @shreyasfegade
