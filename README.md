# Emma AI Incident Response System

An intelligent incident response system that analyzes social care call transcripts, identifies policy violations, and generates comprehensive incident reports with automated email notifications.

## 🌟 Features

- **AI-Powered Analysis**: Uses OpenAI GPT-4 to analyze social care transcripts
- **Policy Violation Detection**: Automatically identifies policy breaches and required actions
- **Incident Report Generation**: Creates detailed, professional incident reports
- **Email Draft Creation**: Generates notification emails for supervisors, risk assessors, and family
- **Interactive Editing**: Manual editing capabilities for all generated content
- **Feedback System**: Refine and regenerate content based on your feedback
- **Secure API Management**: Browser-based encrypted storage of API keys
- **No Database Required**: Identifies service users directly from transcript content

## 🚀 Quick Start

### Prerequisites

- **OpenAI API Key**: Get yours from [OpenAI Platform](https://platform.openai.com/api-keys)
- **No other prerequisites**: The setup script installs everything automatically

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/yourusername/emma-incident-response.git
cd emma-incident-response
```

2. **Run the setup script**:
```bash
./setup.sh --api-key YOUR_OPENAI_API_KEY
```

This will automatically:
- Install Node.js and Python (if needed)
- Set up Python virtual environment
- Install all dependencies
- Configure your OpenAI API key
- Create the run script

3. **Start the system**:
```bash
./run_local.sh
```

4. **Access the application**:
- 🌐 **Frontend**: http://localhost:3000
- 🔗 **Backend API**: http://localhost:8000
- 📚 **API Documentation**: http://localhost:8000/docs

## 📖 How to Use

### Step 1: Submit a Transcript
1. Open http://localhost:3000 in your browser
2. Paste or type a social care call transcript in the input field
3. Click **"Analyze Transcript"**

**Example transcript format**:
```
Call Date: 2024-01-15
Call Time: 14:30
Caller: Sarah Johnson (Carer)

Hi, this is Sarah calling about Dorothy Patterson. 
I'm concerned because Dorothy fell in her bedroom this morning around 9 AM. 
She was trying to get to the bathroom and lost her balance. 
She's 78 years old and seemed a bit confused after the fall. 
She has a small bruise on her arm but says she feels okay otherwise.
This is the second time this week she's fallen.
```

### Step 2: Review the Analysis
The system will generate:

- **📋 Incident Report**: Complete incident details with extracted information
- **📧 Email Draft**: Professional notification email ready to send
- **⚠️ Policy Violations**: Identified breaches with severity levels
- **📝 Recommendations**: Suggested actions and follow-ups

### Step 3: Edit and Refine
- **Edit Reports**: Click "Edit Report" to modify any field manually
- **Provide Feedback**: Use the feedback system to regenerate improved content
- **Update Analysis**: Add additional information or corrections

### Step 4: Export and Use
- **Copy Email**: Use the generated email draft for notifications
- **Print Report**: Print or save the incident report
- **Share Results**: Export content for your records

## 🔧 Configuration

### API Key Management

**Option 1: Through Setup Script** (Recommended)
```bash
./setup.sh --api-key sk-your-openai-api-key
```

**Option 2: Through Web Interface**
1. Click the settings icon in the top-right corner
2. Enter your OpenAI API key
3. Click "Test Connection" to verify
4. Save the configuration

**Option 3: Manual Configuration**
1. Copy `.env.example` to `.env`
2. Add your API key: `OPENAI_API_KEY=sk-your-key-here`
3. Restart the application

### Advanced Options

**Setup Script Options**:
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

## 🏗️ System Architecture

```
emma-incident-response/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── services/          # AI analysis and generation services
│   │   │   ├── llm_analyzer.py    # OpenAI-powered transcript analysis
│   │   │   ├── report_generator.py # Incident report creation
│   │   │   └── email_generator.py  # Email draft generation
│   │   ├── data/
│   │   │   ├── policies.txt       # Social care policies (7 sections)
│   │   │   └── incident_template.json # Report template
│   │   ├── main.py            # FastAPI application
│   │   └── config.py          # Configuration management
│   └── requirements.txt       # Python dependencies
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── ChatInterface.js   # Main transcript input
│   │   │   ├── IncidentReport.js  # Report display/editing
│   │   │   ├── EmailDraft.js      # Email preview/editing
│   │   │   └── SettingsModal.js   # API key configuration
│   │   └── services/
│   │       └── api.js         # Backend communication
│   └── package.json           # Node.js dependencies
├── setup.sh                   # Automated setup script
└── run_local.sh               # Start script (created by setup)
```

## 🔍 Policy Analysis

The system analyzes transcripts against 7 comprehensive policy sections:

1. **Medication Management**: Proper medication handling and administration
2. **First Aid & Medical Emergencies**: Emergency response procedures  
3. **Mobility & Moving**: Fall prevention and mobility assistance
4. **Personal Care**: Privacy and dignity in personal care
5. **Mental Health**: Supporting cognitive and mental wellbeing
6. **Infection Control**: Hygiene and infection prevention
7. **Nutrition & Hydration**: Proper nutrition and fluid management

**How it works**:
- The LLM receives the full transcript and all policy documents
- It intelligently identifies violations and their severity (high/medium/low)
- Required actions are automatically determined based on policy requirements
- Notifications are generated for appropriate personnel (supervisors, risk assessors, family)

## 🛠️ Development

### Local Development Setup
```bash
# The setup script creates everything needed
./setup.sh --api-key YOUR_API_KEY

# Start development servers
./run_local.sh

# Or start services separately:
# Backend only:
cd backend && source venv/bin/activate && uvicorn app.main:app --reload

# Frontend only (in new terminal):
cd frontend && npm start
```

### Making Changes

**Backend Development**:
- Edit files in `backend/app/`
- Backend auto-reloads on file changes
- API docs available at http://localhost:8000/docs

**Frontend Development**:
- Edit files in `frontend/src/`
- Frontend auto-reloads on file changes
- Use browser dev tools for debugging

## 🔒 Security & Privacy

- **No Data Storage**: No user data is stored on servers
- **Encrypted API Keys**: Keys stored encrypted in browser localStorage only
- **Secure Communication**: All API calls use HTTPS in production
- **Privacy First**: Only transcript content is sent to OpenAI for analysis
- **Local Processing**: Most processing happens locally

## 🧪 Testing the System

### Sample Transcripts

**Fall Incident**:
```
Caller: Jane Smith (Support Worker)
Date: 2024-01-20
Time: 10:15

Hello, I'm calling about Mr. Robert Chen, age 72. 
He had a fall in the kitchen this morning around 8:30 AM. 
He was reaching for something in a high cupboard and lost his balance. 
He has a bruise on his shoulder but seems otherwise okay. 
This is his third fall this month, so I'm quite concerned.
```

**Medication Concern**:
```
Caller: Maria Rodriguez (Carer)
Date: 2024-01-20  
Time: 15:45

I need to report an issue with Mrs. Elizabeth Taylor's medication.
She's 65 and has dementia. This morning I found that she had 
taken extra blood pressure tablets because she forgot she already 
took them. She seemed confused and couldn't remember taking the 
morning dose. I'm worried about medication management.
```

### Expected Results

The system should generate:
- ✅ **Service User Identification**: Extract names from transcripts
- ✅ **Incident Classification**: Categorize as Fall, Medical, Mental Health, etc.
- ✅ **Policy Violations**: Identify specific policy breaches
- ✅ **Severity Assessment**: Assign appropriate severity levels
- ✅ **Required Actions**: Generate specific action items
- ✅ **Notification Lists**: Determine who needs to be informed

## ❓ Troubleshooting

### Common Issues

**Setup Problems**:
```bash
# Permission denied
chmod +x setup.sh

# Dependencies missing
./setup.sh --api-key YOUR_KEY  # Reinstalls everything
```

**Connection Issues**:
```bash
# Backend not responding
cd backend && source venv/bin/activate && uvicorn app.main:app --reload

# Frontend not loading  
cd frontend && npm start

# Test API directly
curl http://localhost:8000/health
```

**Analysis Problems**:
- Verify your OpenAI API key has sufficient credits
- Check transcript is clear and contains relevant information
- Try a shorter transcript (under 4000 characters works best)

For detailed troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Test thoroughly with sample transcripts
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: Create an issue in the GitHub repository
- **Documentation**: Check the API docs at http://localhost:8000/docs
- **Troubleshooting**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## 🎯 Emma AI Mission

This system is designed to support social care professionals in maintaining high standards of care through:
- **Rapid Incident Processing**: Faster response to care incidents
- **Consistent Reporting**: Standardized, comprehensive reports
- **Policy Compliance**: Automated policy violation detection
- **Quality Assurance**: Systematic documentation and follow-up

Built with ❤️ for the social care community.