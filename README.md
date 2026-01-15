# Idea Vault

A Next.js app to track startup problems and ideas. Built for **free Vercel hosting** with data stored locally in your browser using localStorage - no external database required.

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

## Deployment to Vercel (Recommended)

### One-Click Deploy

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/YOUR_USERNAME/IdeaTracker)

### Manual Deploy

1. Push this repository to GitHub
2. Go to [vercel.com](https://vercel.com) and sign in with GitHub
3. Click "Add New Project"
4. Import your repository
5. Click "Deploy"

That's it! Vercel automatically detects Next.js and configures everything.

## Run Locally

```bash
# Clone the repository
git clone <your-repo-url>
cd IdeaTracker

# Install dependencies
npm install

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build for Production

```bash
npm run build
npm start
```

## Project Structure

```
IdeaTracker/
├── src/
│   ├── app/
│   │   ├── layout.tsx        # Root layout with sidebar navigation
│   │   ├── page.tsx          # Home page with stats & data management
│   │   ├── globals.css       # Tailwind CSS styles
│   │   ├── dashboard/
│   │   │   └── page.tsx      # Dashboard overview
│   │   ├── problems/
│   │   │   └── page.tsx      # Problems CRUD
│   │   ├── ideas/
│   │   │   └── page.tsx      # Ideas CRUD
│   │   └── notes/
│   │       └── page.tsx      # Notes CRUD
│   └── lib/
│       ├── storage.ts        # localStorage CRUD operations
│       └── types.ts          # TypeScript interfaces
├── package.json              # Node.js dependencies
├── tsconfig.json             # TypeScript config
├── tailwind.config.js        # Tailwind CSS config
├── next.config.js            # Next.js config
├── vercel.json               # Vercel deployment config
└── README.md                 # This file
```

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Storage**: Browser localStorage
- **Hosting**: Vercel (free tier)

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
6. **Export**: Export your data to JSON (Home page)
7. **Import**: Import the JSON backup and verify data
8. **Refresh**: Refresh the page and verify data persists
9. **Browser close/reopen**: Close and reopen browser, verify data persists

## License

MIT License - feel free to use and modify as needed.
