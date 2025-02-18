
# AI Planning Service API

A FastAPI-based service that helps users create comprehensive, personalized plans through a series of AI-powered analyses and recommendations.

## Features

- **Policy Compliance Check**: Validates user input against content policies
- **Further Information Analysis**: Identifies additional details needed for plan creation
- **Final Plan Generation**: Creates detailed, personalized plans based on user input
- **Time Series Task Generation**: Converts plans into structured, time-based tasks

## Prerequisites

- Python 3.12+
- OpenAI API key

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd llm_playground/llm_service_api_ver1/app
```

2. Create a `.env` file in the project root and add your OpenAI API key:
```bash
OPENAI_API_KEY=your_api_key_here
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Service

### Using Python directly:
```bash
python main.py
```

### Using Docker:
```bash
docker build -t ai-planning-service .
docker run -p 8000:8000 ai-planning-service
```

The API will be available at `http://localhost:8000`

## API Endpoints

### 1. Check Policy
- **Endpoint**: `/check-policy/`
- **Method**: POST
- **Purpose**: Validates if the provided goal and plan comply with content policies
- **Request Body**:
```json
{
    "goal": "string",
    "plan": "string"
}
```

### 2. Get Further Information
- **Endpoint**: `/get-further-info/`
- **Method**: POST
- **Purpose**: Analyzes input to determine what additional information is needed
- **Request Body**:
```json
{
    "goal": "string",
    "plan": "string"
}
```

### 3. Get Final Plan
- **Endpoint**: `/get-final-plan/`
- **Method**: POST
- **Purpose**: Generates a comprehensive plan based on all provided information
- **Request Body**:
```json
{
    "goal": "string",
    "info_needed": [
        {
            "keyword": "string",
            "details": "string"
        }
    ]
}
```

### 4. Get Time Series
- **Endpoint**: `/get-time-series/`
- **Method**: POST
- **Purpose**: Converts the final plan into structured time-series tasks
- **Request Body**:
```json
{
    "user_goal": "string",
    "user_plan": "string",
    "further_info": "object",
    "final_plan": "string"
}
```

## Testing

You can test the service using the provided `terminal_test.py` script:
```bash
python terminal_test.py
```

## Dependencies

- FastAPI
- Pydantic
- Uvicorn
- Python-dotenv
- Langchain
- Langchain-openai
- JSONSchema

## Error Handling

The service includes comprehensive error handling for:
- Invalid input validation
- LLM API failures
- Content policy violations
- JSON parsing errors

## CORS

The API allows all origins by default. Modify the CORS middleware in `main.py` to restrict access if needed.
