# Credit Card Dispute Automation POC - Mock Websites

This project sets up two simple mock websites for testing an AI agent workflow for credit card dispute automation:

1. **Transaction Lookup System** - A website that allows searching and viewing transaction details
2. **Dispute Submission System** - A website with a form to submit disputes

Both websites are built with Flask and can be run in Docker containers for easy deployment.

## Project Structure

```
.
├── docker-compose.yml
├── main.py
├── pyproject.toml
├── README.md
├── uv.lock
├── tran_lookup/
│   ├── Dockerfile
│   ├── main.py
│   ├── pyproject.toml
│   ├── README.md
│   └── templates/
│       ├── login.html
│       ├── search.html
│       └── transaction_detail.html
└── tran_submission/
    ├── Dockerfile
    ├── main.py
    ├── pyproject.toml
    ├── README.md
    └── templates/
        ├── login.html
        ├── dispute_form.html
        ├── dispute_confirmation.html
        └── view_disputes.html
```

## Features

### Transaction Lookup System (System 2)
- Login page with simple authentication
- Transaction search functionality
- Detailed transaction view
- Sample transaction data automatically generated

### Dispute Submission System (System 3)
- Login page with simple authentication
- Dispute submission form
- Confirmation page with dispute details
- View all submitted disputes

## Getting Started

### Prerequisites
- Docker and Docker Compose

### Running the Applications

1. Clone this repository
```
git clone https://github.com/yourusername/credit-card-dispute-poc.git
cd credit-card-dispute-poc
```

2. Start the containers with Docker Compose
```
docker-compose up
```

3. Access the websites in your browser:
   - Transaction Lookup System: http://localhost:5001
   - Dispute Submission System: http://localhost:5002

### Default Login Credentials

For both systems:
- Username: `demo`
- Password: `password`

## How It Works for the Proof of Concept

This setup simulates the web interfaces that your agentic workflow will interact with:

1. Your agent will query System 1 (your in-house application with SQL Server DB) to get cases.
2. The agent will then log into the Transaction Lookup System (System 2) at `http://localhost:5001` to search for transaction details.
3. After retrieving the necessary information, the agent will log into the Dispute Submission System (System 3) at `http://localhost:5002` to submit the dispute.

## Integration with the Agentic Workflow

The Python agent using mcp-agent and Puppeteer MCP can:

1. Authenticate to both systems using the provided login forms
2. For System 2:
   - Navigate to the search page
   - Input search terms
   - Extract transaction details
   - Follow links to transaction detail pages

3. For System 3:
   - Navigate to the dispute form
   - Fill out all required fields
   - Submit the form
   - Capture the confirmation details

## Local Database Information

Both systems use SQLite for simplicity:
- `transaction_lookup.db` - Contains users and transactions tables
- `dispute_submission.db` - Contains users and disputes tables

## Notes for Development

- These are simplified mock systems for testing purposes
- In a production environment, you'd want to implement proper security measures
- For the POC, the sites are intentionally kept simple to focus on the agent's interaction capabilities