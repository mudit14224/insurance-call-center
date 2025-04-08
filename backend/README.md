# Insurance Call Center Agent

This is an AI-powered call center agent for insurance services. The agent can handle customer inquiries, look up policy information, and provide assistance with insurance-related questions.

## Features

- **Voice Interaction**: The agent can engage in natural voice conversations with customers
- **Policy Lookup**: Ability to retrieve and display customer policy information
- **Multimodal Capabilities**: Supports both audio and text interactions
- **Real-time Responses**: Powered by OpenAI's real-time model for quick and accurate responses

## Database Functionalities

The agent can perform the following database operations:

- **Policy Management**:
  - Look up insurance policies by policy number
  - Create new insurance policies with details like policy type, dates, and premium
  - Retrieve policy details including policy number, customer name, policy type, dates, and status

- **Customer Management**:
  - Register new customers with name, email, and phone information
  - Look up existing customers by email or phone number
  - Retrieve customer details including customer ID, name, email, and phone

- **Claims Processing**:
  - File new claims for existing policies with amount and description
  - Check the status of existing claims by claim ID
  - Retrieve claim details including claim ID, policy ID, status, amount, and description

## Prerequisites

- Python 3.8+
- PostgreSQL database
- OpenAI API key
- LiveKit account and credentials

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd insurance-call-center/backend
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up PostgreSQL

1. Install PostgreSQL if you haven't already:
   - **macOS**: `brew install postgresql`
   - **Ubuntu**: `sudo apt-get install postgresql postgresql-contrib`
   - **Windows**: Download from [PostgreSQL website](https://www.postgresql.org/download/windows/)

2. Start PostgreSQL service:
   - **macOS**: `brew services start postgresql`
   - **Ubuntu**: `sudo service postgresql start`
   - **Windows**: PostgreSQL service should start automatically

3. Create a database and user:
   ```bash
   # Connect to PostgreSQL
   psql postgres
   
   # Create a database
   CREATE DATABASE insurance_call_center;
   
   # Create a user with password
   CREATE USER insurance_user WITH PASSWORD 'your_password';
   
   # Grant privileges
   GRANT ALL PRIVILEGES ON DATABASE insurance_call_center TO insurance_user;
   
   # Exit psql
   \q
   ```

### 4. Configure Environment Variables

Create a `.env` file in the backend directory with the following variables:

```
LIVEKIT_URL="wss://your-livekit-instance.livekit.cloud"
LIVEKIT_API_KEY="your_livekit_api_key"
LIVEKIT_API_SECRET="your_livekit_api_secret"
OPENAI_API_KEY="your_openai_api_key"
POSTGRES_USER="insurance_user"
POSTGRES_PASSWORD="your_password"
POSTGRES_DB="insurance_call_center"
POSTGRES_HOST="localhost"
POSTGRES_PORT="5432"
```

Replace the placeholder values with your actual credentials.

### 5. Run the Agent

```bash
python agent.py dev
```

## Using the Agent

1. After starting the agent, visit the [LiveKit Playground](https://playground.livekit.io/) to interact with your agent.
2. Enter your LiveKit URL and credentials in the playground.
3. Start a new session to begin interacting with your insurance call center agent.

## Troubleshooting

- If you encounter database connection issues, ensure PostgreSQL is running and your credentials are correct.
- For LiveKit connection problems, verify your API keys and URL in the `.env` file.
- If the agent doesn't respond, check your OpenAI API key and ensure it has sufficient credits.

## License

[Specify your license here] 