# Gradio Agent Checker

This app talks to the FastAPI agent endpoint to verify responses.

## Run

1) Start the API server:

```bash
cd /home/dev/agentic-tests/agentic-chat-test/api
uvicorn api.main:app --reload
```

2) Start the Gradio app:

```bash
cd /home/dev/agentic-tests/agentic-chat-test/gradio_app
python app.py
```

## Notes

- Default API URL: http://localhost:8000/chat
- Override with AGENT_API_URL if needed.
