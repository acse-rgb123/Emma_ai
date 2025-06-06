# Service User Identification in Emma System

## How It Works

The Emma Incident Response System does **NOT** use a database for service user identification. Instead, it extracts information directly from the transcript text using pattern matching.

### Extraction Process

1. **Name Extraction** (`analyzer_fix.py`):
   - Looks for patterns like:
     - "I am Mary Smith"
     - "I'm John Doe"
     - "Mary Smith: Hello..."
     - "My name is Sarah Wilson"
   
2. **Location Extraction**:
   - Searches for location keywords:
     - "in my bedroom"
     - "at the kitchen"
     - "fallen in the bathroom"

3. **No Persistent Storage**:
   - Names are extracted fresh each time
   - No user database or profiles
   - Each session is independent
   - Context only maintained during active session

### Why No Database?

- **Privacy**: No personal data stored
- **Simplicity**: No database management needed
- **Compliance**: Easier GDPR/privacy compliance
- **Flexibility**: Works with any transcript format

### Adding a Database (Future Enhancement)

If you want to add persistent user storage:

1. Add a database service to docker-compose.yml (PostgreSQL/MySQL)
2. Create user models with SQLAlchemy
3. Store user profiles with IDs
4. Link incidents to user IDs
5. Add user search/management endpoints

But for now, the system is designed to be stateless and extract all needed information from the transcript itself.
