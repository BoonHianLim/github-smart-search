# Detect platform-specific venv path
if [[ -f "venv/bin/activate" ]]; then
    # Linux/macOS
    source venv/bin/activate
elif [[ -f "venv/Scripts/activate" ]]; then
    # Windows Git Bash / WSL
    source venv/Scripts/activate
else
    echo "No virtual environment found. Using system Python."
fi

streamlit run main.py