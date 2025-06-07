# Emma Incident Response System

An AI-Enhanced Incident Response System for Social Care that analyzes call transcripts, identifies policy violations, generates incident reports, and drafts notification emails.

## Features

- **OpenAI Integration**: Powered by OpenAI's GPT-4 for accurate incident analysis
- **Transcript Analysis**: Analyzes social care call transcripts against organizational policies
- **Policy Violation Detection**: Identifies policy violations and required actions
- **Incident Report Generation**: Automatically generates detailed incident reports
- **Email Draft Creation**: Creates professional notification emails to relevant parties
- **Feedback System**: Allows users to provide feedback and regenerate content
- **Edit Functionality**: Manual editing of generated reports
- **Secure API Key Management**: Browser-based encrypted storage of API keys
- **No Database Required**: Service users identified through transcript analysis

## Quick Start

### Prerequisites

- **No prerequisites needed** - the setup script installs everything
- **Required**: OpenAI API key from https://platform.openai.com/api-keys

### Installation

Simple one-command setup for local development:

```bash
git clone https://github.com/yourusername/emma-incident-response.git
cd emma-incident-response
./setup.sh --api-key YOUR_OPENAI_API_KEY
```

This will:
- Install Node.js and Python if needed (macOS/Linux)
- Set up Python virtual environment
- Install all dependencies
- Configure your OpenAI API key
- Create the run script

Then start the system:
```bash
./run_local.sh
```

### Access Points

After setup, access your application at:
- 🌐 **Frontend**: http://localhost:3000
- 🔗 **Backend API**: http://localhost:8000  
- 📚 **API Documentation**: http://localhost:8000/docs

### Setup Script Options

```bash
./setup.sh [OPTIONS]

Options:
  -k, --api-key KEY     OpenAI API key (required)
  --skip-deps           Skip dependency installation
  -h, --help            Show help message

Examples:
  ./setup.sh -k sk-your-openai-api-key
  ./setup.sh --api-key sk-your-api-key --skip-deps
```

## Configuration

### API Keys

API keys can be configured in two ways:

1. **Through the UI** (Recommended):
   - Click the provider selector in the top-right
   - Select "Configure API Keys"
   - Enter your keys securely (stored encrypted in browser)

2. **Through environment variables**:
   - Copy `.env.example` to `.env`
   - Add your API keys

### Switching AI Providers

Click on the provider logo in the top-right corner to:
- Switch between configured providers
- View available providers
- Access API key configuration

### Management

- **`./run_local.sh`**: Start the system in local development mode (created by setup.sh)

## Usage

1. **Submit Transcript**: Paste or type a call transcript in the chat interface
2. **Analysis**: The system analyzes the transcript against policies
3. **Review Results**: View the generated incident report and email draft
4. **Edit Reports**: Click "Edit Report" to manually modify any fields
5. **Provide Feedback**: Use the feedback feature to refine results
6. **Export**: Download reports or copy email drafts

## Architecture

```
emma-incident-response/
├── backend/
│   ├── app/
│   │   ├── services/       # AI providers, analyzers, generators
│   │   ├── data/          # Policies and templates
│   │   └── main.py        # FastAPI application
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   └── services/      # API services
│   └── package.json
├── setup.sh               # Setup script
└── run_local.sh           # Start script (created by setup)
```

## Development

The setup script creates a complete local development environment. After running setup:

```bash
# Start both frontend and backend
./run_local.sh

# Or start them separately:
# Backend only:
cd backend && source venv/bin/activate && uvicorn app.main:app --reload

# Frontend only (in separate terminal):
cd frontend && npm start
```

## Security

- API keys are stored encrypted in browser localStorage
- No server-side storage of sensitive information
- All communication over HTTPS in production
- No user data persistence - each session is independent

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues or questions:
- Create an issue in the repository
- Check the documentation in `/docs`
- Review the API documentation at http://localhost:8000/docs
