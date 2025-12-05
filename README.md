# AISHA - AI-Powered Customer Support and Help Assistant

AISHA is an intelligent customer support system designed to streamline query handling and issue resolution through an AI-powered chatbot. It utilizes **FAISS** for context-based search and **SQLite** for structured data storage. AISHA is capable of processing user queries, retrieving relevant data, and providing contextual AI-driven responses to ensure an efficient customer support experience.

---

## Features

- **AI-Based Chat System**: Uses advanced AI models to interact with users and provide relevant solutions.
- **FAISS Integration**: Enables efficient and quick retrieval of context-based information for improved responses.
- **SQLite Database**: Stores customer details, orders, and complaints for structured query handling.
- **Automated Complaint Management**: Logs customer complaints, generates unique ticket numbers, and stores them for tracking.
- **Multi-Language Support**: Responds to user queries in multiple languages, including Hindi.
- **Session-Based Context Memory**: Retains conversation history within sessions for a seamless customer experience.
- **Order and Customer Information Lookup**: Fetches user details and order statuses dynamically from the database.
- **Smart Query Handling**: Identifies phone numbers and order IDs in messages to provide personalized assistance.
- **Voice-Based Interaction (Temporarily Unavailable)**: Previously supported voice interactions using speech-to-text and text-to-speech via GCP, but currently disabled due to high costs.

---

## Technologies Used

- **Python**: Core programming language for backend development.
- **FastAPI**: Lightweight web framework to handle API requests.
- **FAISS**: High-speed similarity search for storing and retrieving contextual embeddings.
- **SQLite**: Database for structured storage of customer and order information.
- **LangChain**: Framework for building conversational AI models.
- **Groq API (Gemma2-9b-it)**: AI model for generating intelligent responses.
- **Hugging Face Embeddings**: For text vectorization and context matching.

---

## Installation & Setup

### Prerequisites

Ensure you have Python 3.8+ installed.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-repo/AISHA.git
   cd AISHA
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Set up environment variables:**
   Create a `.env` file and add your API keys:
   ```env
   LANGCHAIN_API_KEY=your_langchain_key
   LANGCHAIN_PROJECT=your_project_name
   GROQ_API_KEY=your_groq_api_key
   HF_TOKEN=your_huggingface_token
   ```
4. **Run the FastAPI server:**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

---

## API Endpoints

### 1. Chat API

- **Endpoint:** `/chat`
- **Method:** `POST`
- **Request Body:**
  ```json
  {
    "input": {"content": "Where is my order?", "language": "en"},
    "config": {"session_id": "user123"}
  }
  ```
- **Response:**
  ```json
  {
    "response": "Your order #1234 was shipped on March 25th. Expected delivery: March 30th."
  }
  ```

---

## How AISHA Works

1. **User Query Processing**:
   - Extracts phone number or order ID from the input.
   - Retrieves corresponding details from the SQLite database.
2. **Contextual Search with FAISS**:
   - Stores and searches historical customer data to provide relevant responses.
3. **AI-Based Response Generation**:
   - Uses Groq API’s Gemma2-9b-it model to generate intelligent responses.
   - Responds in the user's preferred language.
4. **Complaint Management**:
   - If an issue is unresolved, AISHA generates a ticket number and logs the complaint.
   - Ensures a structured workflow for issue resolution.

---

## Example Interaction

**User:** *"I have an issue with my order 5678."*

**AISHA:** *"I found your order. It was delivered on March 20th. Could you specify the issue?"*

**User:** *"The product is damaged."*

**AISHA:** *"I apologize for the inconvenience. I have created a complaint ticket: TH1234. Our support team will contact you soon."*

---

## Future Enhancements

- **Voice-Based Support (Reintegration Planned)**: Optimize cost-effective speech-to-text and text-to-speech services.
- **Advanced Sentiment Analysis**: Improve response personalization based on user sentiment.
- **Dashboard for Admins**: Provide real-time monitoring of complaints and query statistics.
- **Integration with External APIs**: Fetch live order tracking updates from e-commerce platforms.

---

## Contributing

We welcome contributions! To contribute:

1. Fork the repository.
2. Create a new branch.
3. Make your changes and submit a pull request.

---

## License

AISHA is licensed under the **MIT License**. Feel free to modify and use it as needed.

---

## Contact

For any issues or queries, reach out to us at **[unsapervaiz264@gmail.com](mailto:unsapervaiz264@gmail.com)**.


