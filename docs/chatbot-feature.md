# AI Chatbot Feature

## Goal

Create an AI-powered chatbot that can answer questions about Blinkit customer reviews using the analyzed data.

## What the chatbot does

The chatbot can:
- **Answer questions** about customer feedback patterns
- **Provide insights** on specific themes or topics
- **Summarize** customer opinions on products/services
- **Compare** sentiment across different time periods or sources
- **Recommend** actions based on customer feedback

## How it works

1. User asks a question in natural language
2. Chatbot analyzes the question and retrieves relevant data
3. Gemini AI processes the data and generates an answer
4. Response is displayed in the chat interface

## Features

- **Natural language interface** — Ask questions like you would to a human analyst
- **Context-aware** — Understands the Blinkit domain and customer feedback
- **Data-driven answers** — Responses based on actual review data
- **Interactive conversation** — Follow-up questions and clarifications

## How to use

```powershell
streamlit run app/chatbot.py
```

The chatbot will open in your browser at http://localhost:8501

## Example questions

- "What are customers saying about delivery times?"
- "How do customers feel about the app performance?"
- "What are the main complaints from negative reviews?"
- "Show me positive feedback about product quality"
- "What themes are most common in recent reviews?"

## Technical details

- Uses Gemini AI for natural language understanding
- Integrates with analyzed review data from previous phases
- Streamlit chat interface for easy interaction
- Context-aware responses using RAG (Retrieval-Augmented Generation)
