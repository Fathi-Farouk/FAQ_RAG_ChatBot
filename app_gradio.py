import gradio as gr
from rag_pipeline_02 import build_rag_chain

# =========================
# Chain Cache (IMPORTANT)
# =========================
chain_cache = {}

def get_chain(source, db_type):
    key = f"{source}_{db_type}"

    if key not in chain_cache:
        print(f"🚀 Loading chain for {key}")
        chain_cache[key] = build_rag_chain(source, db_type)

    return chain_cache[key]


# =========================
# Chat Function
# =========================
def chat_fn(message, history, source, db_type):

    if history is None:
        history = []

    # ✅ Use cached chain (fix repeated answer issue)
    chain = get_chain(source, db_type)

    response = chain.invoke(message)
    response = str(response)

    # ✅ Gradio message format
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": response})

    return history, history


# =========================
# Gradio UI
# =========================
with gr.Blocks(title="FAQ RAG Assistant") as demo:

    gr.Markdown("## 🤖 FAQ RAG Chatbot (STC + WE)")

    with gr.Row():

        source = gr.Dropdown(
            choices=["stc", "we"],
            value="stc",
            label="Select Source"
        )

        db_type = gr.Dropdown(
            choices=["faiss", "chroma"],
            value="faiss",
            label="Vector DB"
        )

    logo = gr.Image(
        value="assets/stc.png",
        height=100,
        show_label=False
    )

    def update_logo(source):
        return "assets/stc.png" if source == "stc" else "assets/we.png"

    chatbot = gr.Chatbot()
    msg = gr.Textbox(label="Ask your question")
    clear = gr.Button("Clear Chat")

    msg.submit(chat_fn, [msg, chatbot, source, db_type], [chatbot, chatbot])
    clear.click(lambda: [], None, chatbot)

    source.change(update_logo, source, logo)


# =========================
# Run App
# =========================
if __name__ == "__main__":
    demo.launch()