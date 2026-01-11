# 🤖 AI Support Agent

An intelligent customer support agent built with Streamlit, Groq AI, and vector search capabilities. This agent helps customers with order inquiries, FAQs, and general support questions.

## ✨ Features

- **💬 Interactive Chat Interface**: Modern, user-friendly Streamlit-based chat interface
- **📦 Order Status Tracking**: Query order status and delivery information
- **❓ FAQ Search**: Intelligent FAQ retrieval using vector search and semantic similarity
- **🧠 Conversation Memory**: Maintains context across the conversation session
- **💾 Chat Export**: Download conversation history as text files
- **🎨 Modern UI**: Beautiful gradient design with responsive layout

## 🏗️ Project Structure

```
ai-support-agent/
├── app/
│   ├── agent.py          # Core agent orchestration logic
│   ├── memory.py          # Session-based conversation memory
│   ├── tools.py           # Order status and FAQ tools
│   ├── retrieval.py       # Vector search for FAQs
│   ├── schemas.py         # Data models
│   └── main.py            # FastAPI backend (optional)
├── data/
│   └── faqs.txt           # FAQ knowledge base
├── streamlit_app.py       # Main Streamlit frontend
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Groq API key ([Get one here](https://console.groq.com/))

### Installation

1. **Clone the repository** (or navigate to the project directory):
   ```bash
   cd "C:\Users\HP\Desktop\projects\ai-support agent"
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - **Windows (PowerShell)**:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - **Windows (Command Prompt)**:
     ```cmd
     venv\Scripts\activate.bat
     ```
   - **macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**:
   
   Create a `.env` file in the root directory:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```
   
   **⚠️ Important**: Update `app/agent.py` to use environment variables:
   ```python
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   client = Groq(api_key=os.getenv("GROQ_API_KEY"))
   ```

6. **Run the application**:
   ```bash
   streamlit run streamlit_app.py
   ```

7. **Open your browser**:
   The app will automatically open at `http://localhost:8501`

## 📖 Usage

### For Users

1. **Start a conversation**: Type your question in the chat input at the bottom
2. **Ask about orders**: "What's the status of order ORD-1001?"
3. **Search FAQs**: "How do I return an item?" or "What's your refund policy?"
4. **Export chat**: Use the sidebar to download your conversation history

### Example Queries

- "What's the status of order ORD-1001?"
- "How do I return an item?"
- "What's your refund policy?"
- "How can I track my order?"
- "What are your payment options?"

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### Model Configuration

The agent uses `llama-3.1-8b-instant` by default. You can modify this in `app/agent.py`:

```python
response = client.chat.completions.create(
    model="llama-3.1-8b-instant",  # Change this to use a different model
    messages=messages,
    temperature=0.2,
    max_tokens=150,
)
```

## 🌐 Deployment

### Deploy to Streamlit Cloud

1. **Push your code to GitHub** (see [GitHub Deployment](#-github-deployment) below)

2. **Go to [Streamlit Cloud](https://streamlit.io/cloud)**

3. **Sign in** with your GitHub account

4. **Click "New app"**

5. **Select your repository** and branch

6. **Set the main file path**: `streamlit_app.py`

7. **Add secrets** (for API keys):
   - Go to "Advanced settings"
   - Add secret: `GROQ_API_KEY` = `your_api_key_here`

8. **Click "Deploy"**
   ```

## 📦 GitHub Deployment

### Initial Setup

1. **Initialize Git repository** (if not already done):
   ```bash
   git init
   ```

2. **Create a `.gitignore` file** (already included in this repo):

3. **Add all files**:
   ```bash
   git add .
   ```

4. **Commit your changes**:
   ```bash
   git commit -m "Initial commit: AI Support Agent"
   ```

### Push to GitHub

1. **Create a new repository on GitHub**:
   - Go to [GitHub](https://github.com)
   - Click "New repository"
   - Name it (e.g., `ai-support-agent`)
   - **Don't** initialize with README, .gitignore, or license (we already have these)
   - Click "Create repository"

2. **Connect your local repository to GitHub**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   ```

3. **Push your code**:
   ```bash
   git branch -M main
   git push -u origin main
   ```

### Updating Your Repository

Whenever you make changes:

```bash
git add .
git commit -m "Description of your changes"
git push
```

## 🔒 Security Notes

- **⚠️ Never commit API keys to GitHub**
- Use environment variables or Streamlit secrets for sensitive data
- The `.gitignore` file already excludes `.env` files
- For Streamlit Cloud, use the "Secrets" section in app settings

## 🛠️ Development

### Running in Development Mode

```bash
streamlit run streamlit_app.py --server.runOnSave true
```

### Testing

Test individual components:

```python
# Test agent
from app.agent import run_agent
response = run_agent("test-session", "What's the status of ORD-1001?")
print(response)
```

## 📝 Dependencies

- **streamlit**: Web framework for the frontend
- **groq**: AI model API client
- **sentence-transformers**: For semantic search
- **faiss-cpu**: Vector database for FAQ retrieval
- **fastapi**: Optional backend API
- **python-dotenv**: Environment variable management

See `requirements.txt` for complete list.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [Groq AI](https://groq.com/)
- Uses [FAISS](https://github.com/facebookresearch/faiss) for vector search

## 📧 Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Made with ❤️ using Streamlit and Groq AI**
