# 🚀 PathForward  
### AI-Powered Financial Benefits Routing System (LA County)

---

## 🧠 Overview

PathForward is an AI-powered **decision-support and routing system** designed to help underbanked individuals and micro-business operators quickly find and act on relevant financial assistance programs.

Users complete a **90-second intake**, and PathForward returns:

- 📊 Ranked eligible programs  
- ✅ Explainable eligibility insights  
- 📄 Required documents  
- 🧭 Step-by-step action plan  

---

## ❗ Problem

Financial assistance programs are:

- Fragmented across multiple platforms  
- Difficult to understand  
- Not personalized to user needs  
- Time-consuming to navigate  

---

## 💡 Solution

PathForward simplifies access to financial assistance by:

> **Understanding user needs → Matching relevant programs → Guiding next steps**

---

## ⚙️ How It Works

### 1️⃣ Structured Intake  
Users provide basic information and describe their situation.

### 2️⃣ AI Understanding  
- Interprets user intent  
- Extracts relevant context from free text  

### 3️⃣ Eligibility Matching  
Programs are evaluated against structured eligibility rules to determine relevance.

### 4️⃣ Intelligent Ranking  
Programs are prioritized based on multiple factors such as:
- eligibility fit  
- urgency  
- accessibility  
- expected effort  

### 5️⃣ Actionable Guidance  
Users receive a clear step-by-step plan on what to do next.

---

## 🖥️ Key Features

- 🔍 Personalized program matching  
- 📊 Ranked recommendations  
- 📄 Document guidance  
- 🧠 AI-powered understanding  
- 🧭 Actionable next steps  
- 📈 Transparent reasoning  

---

## 🧱 Tech Stack

### Backend
- FastAPI  
- Python  

### AI Layer
- Gemini (structured outputs)  

### Frontend
- React  
- TypeScript  
- Tailwind CSS  

---

## 🏗️ System Design (High-Level)
User Input → AI Understanding → Matching Engine → Ranking → Action Plan


---

## 🎯 Target Audience

- Underbanked individuals  
- Micro-business operators  
- Freelancers / 1099 contractors  
- Gig workers  

---

## 🌍 Demo Scope

- Los Angeles County  
- Uses realistic demo data  
- Designed for real-world integration  

---

## 🔐 Data Privacy

- Sensitive structured data stays within backend  
- AI is used only for minimal context processing  
- No automated decision-making by AI  

---

## 🚀 Getting Started

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # or venv\\Scripts\\activate (Windows)
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```
🧪 Example Use Case

A user with urgent financial needs receives:

Relevant program recommendations
Eligibility insights
Required documentation
Clear next steps

💼 Business Model

PathForward follows a B2B2C model:

Institutions (government, NGOs, financial orgs) → platform customers
Individuals → end users
🔮 Future Work
Real-time data integration
Expanded geographic coverage
Improved personalization
Multilingual support
🏁 Summary

PathForward transforms complex financial systems into clear, actionable decisions.
