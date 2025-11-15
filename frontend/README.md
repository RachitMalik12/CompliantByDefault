# CompliantByDefault Frontend

Next.js web application for the SOC 2 Readiness Agent.

## Features

- 🎨 Modern, responsive UI built with Next.js and Tailwind CSS
- 📊 Interactive dashboards for compliance reports
- 🔄 Real-time scan progress monitoring
- 📁 Support for local and GitHub repository scanning
- 📈 Visual representation of SOC 2 control coverage
- 🔍 Filterable and sortable findings tables

## Prerequisites

- Node.js 18+ and npm/yarn
- Backend API running (see `/backend` folder)

## Installation

```bash
cd frontend

# Install dependencies
npm install
# or
yarn install
```

## Configuration

Create a `.env.local` file in the frontend directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Development

```bash
# Run development server
npm run dev
# or
yarn dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Build

```bash
# Build for production
npm run build

# Start production server
npm start
```

## Project Structure

```
frontend/
├── src/
│   ├── pages/
│   │   ├── index.tsx           # Landing page
│   │   ├── scan.tsx            # Scan initiation page
│   │   ├── report/[id].tsx     # Report detail page
│   │   └── _app.tsx            # Next.js app wrapper
│   ├── components/
│   │   ├── Navbar.tsx          # Navigation bar
│   │   ├── RepoSelector.tsx    # Repository input form
│   │   ├── ScanProgress.tsx    # Scan progress indicator
│   │   ├── ReportCard.tsx      # Score summary cards
│   │   └── FindingsTable.tsx   # Findings data table
│   ├── lib/
│   │   └── api.ts              # API client functions
│   ├── types/
│   │   └── index.ts            # TypeScript type definitions
│   └── styles/
│       └── globals.css         # Global styles
├── public/                     # Static assets
├── package.json
├── tsconfig.json
├── next.config.js
└── tailwind.config.js
```

## Pages

### Home (`/`)
- Landing page with product overview
- Feature highlights
- SOC 2 controls explained
- CTA to start scanning

### Scan (`/scan`)
- Repository selector (GitHub URL or local path)
- Scan initiation
- Real-time progress tracking
- Auto-redirect to report when complete

### Report (`/report/[id]`)
- Compliance score and grade
- Severity distribution
- AI-powered insights
- Top recommendations
- Control-by-control breakdown
- Detailed findings table with filters

## Components

### Navbar
Top navigation with branding and page links.

### RepoSelector
Form for selecting scan target:
- GitHub repository URL input
- Local directory path input  
- Optional GitHub token for private repos
- Validation and error handling

### ScanProgress
Real-time scan monitoring:
- Animated loading indicator
- Status messages
- Progress bar
- Error handling with retry option

### ReportCard
Score summary display:
- Overall readiness score (0-100)
- Letter grade (A-F)
- Total findings count
- Severity breakdown
- Control coverage percentage
- Risk level assessment

### FindingsTable
Interactive findings browser:
- Sortable by severity, file, control
- Filterable by severity and control
- Pagination for large result sets
- Expandable rows for details
- Color-coded severity badges

## API Integration

The frontend communicates with the backend API via `/src/lib/api.ts`:

- `scanLocal(path)` - Start local directory scan
- `scanGithub(url, token?)` - Start GitHub repository scan
- `getReport(jobId)` - Fetch scan report
- `listReports()` - List all reports
- `getControls()` - Get SOC 2 controls info
- `healthCheck()` - Check API status

All API calls are typed with TypeScript for type safety.

## Styling

- **Framework**: Tailwind CSS
- **Colors**: Custom primary blue theme
- **Layout**: Responsive grid system
- **Components**: Utility-first CSS classes

## Testing

```bash
# Run tests
npm test

# Run tests in watch mode
npm run test:watch
```

## Environment Variables

- `NEXT_PUBLIC_API_URL`: Backend API base URL (default: `http://localhost:8000`)

## Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Docker

```bash
# Build image
docker build -t compliantbydefault-frontend .

# Run container
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://api:8000 compliantbydefault-frontend
```

### Static Export

```bash
# Build static site
npm run build
npm run export

# Deploy `out/` directory to any static host
```

## Troubleshooting

**"Failed to connect to API"**
- Ensure backend is running on the configured URL
- Check CORS settings in backend
- Verify `NEXT_PUBLIC_API_URL` is correct

**"Report not found"**
- Scan may still be in progress
- Check backend logs for errors
- Ensure job ID is correct

**Slow page loads**
- Large reports may take time to render
- Consider pagination or virtualization for very large findings lists

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## License

MIT

## Contributing

See root README for contribution guidelines.
