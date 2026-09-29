# 🧠 SupportMemory

### A customer support agent that learns from every interaction using persistent Hindsight memory.

SupportMemory is an AI-powered customer support agent designed to solve one common problem:

> Customers shouldn't have to explain the same problem every time they contact support.

Instead of treating every conversation as a fresh session, SupportMemory uses **Hindsight** to recall relevant customer history and personalize the next response.

---

## 🎯 The Problem

Traditional AI support agents are often stateless.

A customer may have:

- reported the same issue before
- received a previous replacement
- shared a product preference
- explained their business context
- contacted support multiple times

Yet a new conversation can still begin with:

> "Please provide your order number and explain the issue."

This creates repetition and frustration.

---

## 💡 Our Solution

SupportMemory gives the support agent persistent customer memory.

For every interaction, the system:

1. **Recalls** relevant customer history from Hindsight.
2. **Understands** the current issue using that context.
3. **Generates** a personalized response.
4. **Retains** a factual summary of the new interaction.
5. Uses that information in future conversations.

The goal is not simply to remember conversations.

The goal is to make future support interactions **more informed and personalized**.

---

## 🧠 Why Hindsight Matters

Hindsight is the central memory layer of SupportMemory.

Without memory:

> "Hi, I have an issue with my order."

The agent needs to ask for basic information again.

With Hindsight:

> "I see you previously received a replacement jar for your Bosch Series 6 mixer grinder..."

The agent can immediately connect the current issue with relevant history.

This creates a clear before/after demonstration:

**Without memory → generic support**

**With Hindsight → contextual support**

---

## 🔄 Memory Loop

```text
Customer Message
       ↓
Hindsight Recall
       ↓
Relevant Customer Context
       ↓
LLM Response
       ↓
Factual Interaction Summary
       ↓
Hindsight Retain
       ↓
Future Conversations
```

## Run the demo

1. Install dependencies from the project directory:

   ```powershell
   python -m pip install -r requirements.txt
   ```

2. Configure `HINDSIGHT_BASE_URL`, `HINDSIGHT_API_KEY`, `GROQ_API_KEY`, and optionally `GROQ_MODEL` in the root `.env` file. Do not commit `.env`.
3. Normally, seed the customer-specific v4 Hindsight banks once when starting with a fresh bank version. Do not rerun this against banks that already contain the demo data, because it adds the seed events again.

   ```powershell
   python seed_memory.py
   ```

4. Launch Streamlit:

   ```powershell
   python -m streamlit run app.py
   ```

Select a customer in the sidebar and enable **Compare with no-memory agent** to see the response comparison.