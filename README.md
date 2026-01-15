# Idea Vault

A Streamlit-based tool to track startup problems and ideas. Data is stored locally in your browser using localStorage - no external database required.

## Features

- **Problems**: Track pain points you've observed with severity, frequency, and status
- **Ideas**: Develop solution concepts with validation stages and scoring
- **Notes**: Capture research, interviews, competitor analysis, and more
- **Linking**: Connect ideas to the problems they solve
- **Export/Import**: Backup and restore your data as JSON

## Local-Only Storage

**Important**: Your data is stored in your browser's localStorage. This means:

- Data persists on your device/browser only
- No cross-device sync
- No server-side storage
- Data is lost if you clear browser data
- Private/incognito sessions won't have access to your data

Use the Export feature regularly to backup your data!

## Deployment

### Option 1: Streamlit Community Cloud (Recommended - Free)

1. Push this repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app"
4. Select your repository, branch, and set `Idea_Vault.py` as the main file
5. Click "Deploy"

That's it! No environment variables or database setup required.

### Option 2: Run Locally

```bash
# Clone the repository
git clone <your-repo-url>
cd IdeaTracker

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run Idea_Vault.py
```

The app will open in your browser at `http://localhost:8501`.

### Option 3: Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "Idea_Vault.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:
```bash
docker build -t idea-vault .
docker run -p 8501:8501 idea-vault
```

### Note on Vercel

Vercel's serverless architecture is not well-suited for Streamlit apps (which require a persistent server process). For free hosting, **Streamlit Community Cloud** is the recommended option for Streamlit applications.

## Project Structure

```
IdeaTracker/
├── Idea_Vault.py          # Main app entry point
├── database.py            # Database API (wrapper for storage)
├── storage.py             # Browser localStorage implementation
├── pages/
│   ├── 1_Dashboard.py     # Overview dashboard
│   ├── 2_Problems.py      # Problems management
│   ├── 3_Ideas.py         # Ideas management
│   └── 4_Notes.py         # Notes management
├── requirements.txt       # Python dependencies
├── vercel.json           # Vercel config (limited support)
└── README.md             # This file
```

## Data Model

### Problems
- Title, description, observed context
- Severity (1-5), frequency (rare/weekly/daily)
- Status (open/solved/ignored)
- Tags (comma-separated)

### Ideas
- Title, pitch, target user
- Value proposition, differentiation
- Assumptions, risks
- Status (new/researching/validating/building/parked)
- Score (0-100, optional)
- Tags (comma-separated)

### Notes
- Type (interview/competitor/pricing/tech/general)
- Content, links
- Can be attached to problems or ideas

### Links
- Many-to-many relationship between problems and ideas

## Testing

After deployment, test the following:

1. **Create**: Add a new problem, idea, and note
2. **Read**: View all items on Dashboard and list pages
3. **Update**: Edit an existing item and verify changes persist
4. **Delete**: Delete an item and verify it's removed
5. **Linking**: Link an idea to a problem and verify the relationship
6. **Export**: Export your data to JSON
7. **Import**: Import the JSON backup and verify data
8. **Refresh**: Refresh the page and verify data persists
9. **Browser close/reopen**: Close and reopen browser, verify data persists

## License

MIT License - feel free to use and modify as needed.
