# Emma AI - Local Development Troubleshooting

## Common Issues and Solutions

### 🔧 Setup Issues

#### "Permission denied" when running setup script
```bash
chmod +x setup.sh
./setup.sh --api-key YOUR_API_KEY
```

#### Node.js/Python not found
The setup script automatically installs these. If you need to install manually:

**Node.js:**
- macOS: `brew install node`
- Ubuntu: `sudo apt-get install nodejs npm`
- Or download from: https://nodejs.org/

**Python:**
- macOS: `brew install python@3.11`
- Ubuntu: `sudo apt-get install python3 python3-pip python3-venv`
- Or download from: https://python.org/

### 🌐 Connection Issues

#### "Connection failed" when testing OpenAI API
1. **Check API key format**: Must start with `sk-`
2. **Verify API key**: Test at https://platform.openai.com/playground
3. **Check billing**: Ensure you have credits/active billing
4. **Network issues**: Try again in a few minutes

#### Frontend won't load (localhost:3000)
```bash
# Check if process is running
ps aux | grep "npm start"

# Restart frontend
cd frontend && npm start
```

#### Backend API not responding (localhost:8000)
```bash
# Check if backend is running
ps aux | grep uvicorn

# Restart backend
cd backend && source venv/bin/activate && uvicorn app.main:app --reload
```

#### "Proxy error" messages
This usually means the backend isn't fully started yet. Wait 1-2 minutes and refresh.

### 🔄 Runtime Issues

#### Analysis fails with "OpenAI analysis failed"
1. **Check API key**: Verify in settings modal or .env file
2. **Check credits**: Ensure OpenAI account has sufficient credits
3. **Try again**: Temporary OpenAI API issues are common
4. **Check transcript**: Ensure it's not empty or too long

#### "Service user name not found" in results
This is normal - the AI extracts names from transcripts. If no name is clearly stated, it will show "Unknown".

#### Reports look incomplete
1. **Check transcript quality**: Ensure transcript is clear and detailed
2. **Try regenerating**: Use the feedback system to request improvements
3. **Edit manually**: Use the "Edit Report" feature to add missing information

### 💻 Local Development Issues

#### Python virtual environment issues
```bash
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### Node.js dependency issues
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

#### "Module not found" errors
1. **Backend**: Ensure virtual environment is activated: `source backend/venv/bin/activate`
2. **Frontend**: Ensure you're in frontend directory and ran `npm install`

#### Port already in use
```bash
# Find what's using the ports
lsof -i :3000  # Frontend
lsof -i :8000  # Backend

# Kill the processes
kill -9 PID_NUMBER

# Or use different ports
cd backend && uvicorn app.main:app --reload --port 8001
cd frontend && PORT=3001 npm start
```

### 🔍 Debugging Commands

#### Check if services are running
```bash
# Check backend
curl http://localhost:8000/health

# Check frontend
curl http://localhost:3000
```

#### Test OpenAI connection directly
```bash
curl -X POST http://localhost:8000/api/test_openai \
  -H "Content-Type: application/json" \
  -d '{"api_key":"YOUR_API_KEY"}'
```

#### View backend logs
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --log-level debug
```

#### Reset everything
```bash
# Complete reset
rm -rf backend/venv frontend/node_modules
rm -f .env
./setup.sh --api-key YOUR_API_KEY
```

### 🎯 Performance Tips

#### Speed up analysis
- Use shorter, focused transcripts
- Ensure stable internet connection
- Keep transcript under 4000 characters for best results

#### Reduce resource usage
- Close other applications
- Use latest version of Node.js and Python
- Consider using a faster internet connection

### 🔐 Security Notes

- API keys are stored in browser localStorage only
- No sensitive data is sent to external services except OpenAI
- The .env file is for development only - don't commit it to version control
- Regularly rotate API keys for security

### 📞 Getting Help

If you're still experiencing issues:

1. **Check the console**: Open browser developer tools (F12) and check for errors
2. **Check terminal output**: Look for error messages in the terminal where you ran the scripts
3. **Try a simple test**: Use a basic transcript to verify the system works
4. **Check versions**: Ensure you have recent versions of Node.js (16+) and Python (3.8+)

### 🚀 Quick Fixes

```bash
# Most common fix - restart everything
./run_local.sh

# If that doesn't work, reset dependencies
cd backend && rm -rf venv && cd ..
cd frontend && rm -rf node_modules && cd ..
./setup.sh --api-key YOUR_API_KEY

# If still having issues, check your API key
echo $OPENAI_API_KEY  # Should show your key
# Or check the .env file
cat .env
```