# Gray Swan Manual Testing Interface

This application provides a web-based interface for manually testing prompts against AI models as part of the Gray Swan framework. It allows researchers to select prompts, test them against various AI models, and record the results for analysis.

## Features

- **Prompt Management**: Browse, filter, create, edit, and delete prompts
- **Manual Testing Interface**: Copy prompts to test against AI models and record responses
- **Results Tracking**: View and filter test results
- **Dashboard**: Overview of testing activity and statistics

## Setup and Installation

### Backend (FastAPI)

1. Navigate to the web directory:
   ```
   cd ai_learning_platform/web
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the FastAPI server:
   ```
   python run_server.py
   ```

   The API will be available at http://localhost:8000

### Frontend (React)

1. Navigate to the frontend directory:
   ```
   cd ai_learning_platform/web/frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm start
   ```

   The web interface will be available at http://localhost:3000

## Usage

1. **Login**: Use the default credentials (username: `admin`, password: `password`)

2. **Browse Prompts**: Navigate to the Prompts page to view existing prompts

3. **Test a Prompt**:
   - Select a prompt from the list
   - Click "Test Prompt" or navigate to the Test Interface
   - Select the AI model to test against
   - Copy the prompt and paste it to the AI model
   - Get the AI's response
   - Paste the response back into the interface
   - Indicate whether the test was successful
   - Add any notes
   - Submit the result

4. **View Results**: Navigate to the Results page to view all test results

## API Endpoints

### Authentication
- `POST /token`: Get authentication token

### Prompts
- `GET /api/prompts`: List prompts with filtering and pagination
- `GET /api/prompts/{id}`: Get a specific prompt
- `POST /api/prompts`: Create a new prompt
- `PUT /api/prompts/{id}`: Update a prompt
- `DELETE /api/prompts/{id}`: Delete a prompt

### Test Results
- `GET /api/results`: List test results with filtering and pagination
- `POST /api/results`: Submit a new test result

### Utility Endpoints
- `GET /api/models`: List available AI models
- `GET /api/challenges`: List available challenges
- `GET /api/categories`: List available categories
- `GET /api/techniques`: List available techniques

## Development

### Project Structure

```
web/
├── main.py                # FastAPI application
├── run_server.py          # Server startup script
├── requirements.txt       # Python dependencies
└── frontend/             # React frontend
    ├── public/           # Static files
    └── src/              # Source code
        ├── components/   # React components
        ├── contexts/     # React contexts
        ├── services/     # API services
        └── App.js        # Main application component
```

### Adding New Features

- **New API Endpoints**: Add new endpoints to `main.py`
- **New React Components**: Add new components to the appropriate directory in `frontend/src/components/`
- **New API Services**: Add new API service functions to `frontend/src/services/api.js`