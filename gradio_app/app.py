import os
import requests
import gradio as gr

API_URL = os.getenv("AGENT_API_URL", "http://localhost:8000/chat")


def _default_profile():
    return {"full_name": "", "email": "", "bio": "", "is_complete": False}


def send_message(message, history, profile_state, session_id):
    if not message:
        return history, profile_state, "", session_id

    history = list(history or [])
    profile_state = profile_state or _default_profile()

    payload_history = history[:]
    history.append({"role": "user", "content": message})

    payload = {
        "message": message,
        "history": payload_history,
        "profile": profile_state,
    }
    if session_id:
        payload["session_id"] = session_id

    try:
        response = requests.post(API_URL, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        history.append({"role": "assistant", "content": f"Error contacting API: {exc}"})
        return history, profile_state, "", session_id

    assistant_message = data.get("message", "No response")
    updated_profile = data.get("profile", profile_state)
    action = data.get("action", "")

    if action == "submit_request":
        assistant_message += "\n\n✅ **[SUBMITTED]** Your request has been successfully submitted!"
    elif action == "request_confirmation":
        assistant_message += "\n\n⏳ **[AWAITING CONFIRMATION]** Please confirm to proceed."

    session_id = data.get("session_id", session_id)
    history.append({"role": "assistant", "content": assistant_message})
    return history, updated_profile, "", session_id


def build_ui():
    with gr.Blocks(title="Agent Response Checker") as demo:
        gr.Markdown("# Agent Response Checker\nRun the FastAPI server first.")

        profile_state = gr.State(_default_profile())
        session_state = gr.State("")

        with gr.Row():
            chatbot = gr.Chatbot(label="Agent", height=420)

        with gr.Row():
            message = gr.Textbox(label="Message", placeholder="Type a message...")

        with gr.Row():
            send_btn = gr.Button("Send")
            clear_btn = gr.Button("Clear")

        send_btn.click(
            send_message,
            inputs=[message, chatbot, profile_state, session_state],
            outputs=[chatbot, profile_state, message, session_state],
        )
        message.submit(
            send_message,
            inputs=[message, chatbot, profile_state, session_state],
            outputs=[chatbot, profile_state, message, session_state],
        )
        clear_btn.click(
            lambda: ([], _default_profile(), "", ""),
            outputs=[chatbot, profile_state, message, session_state],
        )

    return demo


if __name__ == "__main__":
    app = build_ui()
    app.launch()
