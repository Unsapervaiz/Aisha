# IMPORTS
import re
import sqlite3
from dotenv import load_dotenv
import os

from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from fastapi import FastAPI, Request

import numpy as np
import faiss
from langchain_huggingface import HuggingFaceEmbeddings





# LOADING ENV VARIABLES
load_dotenv()

#Langsmith Tracking
os.environ['LANGCHAIN_API_KEY']=os.getenv('LANGCHAIN_API_KEY')
os.environ['LANGCHAIN_TRACKING_V2']="true"
os.environ['LANGCHAIN_PROJECT']=os.getenv('LANGCHAIN_PROJECT')
os.environ['GROQ_API_KEY']=os.getenv('GROQ_API_KEY')
os.environ['HF_TOKEN']=os.getenv('HF_TOKEN')
groq_api_key=os.getenv('GROQ_API_KEY')





# MODEL AND EMBEDDING INITIALIZATION
model=ChatGroq(model='gemma2-9b-it', groq_api_key=groq_api_key)

embedding=HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')





# VECTOR DB DEFINITIONS
# Stores session history corresponding to a session_id
session_store={}

# Uses IndexFlatL2, IndexFlatL2 is a type of FAISS index that performs brute-force similarity search using L2 distance (Euclidean distance) between vectors.
# On this we perform similarity search and all, then we provide relevant info from faiss_stores.
faiss_indices = {}

# For each session id, it stores a dict of the type {text : embeddings}. Used to store info from database like user info, order info etc.
faiss_stores = {}

# Prevents duplicate isue creation in the same session. Stores issue no for session id, if an issue number already exists, doesn't create another.
complaint_stores = {}

def get_session_history(session_id:str)->BaseChatMessageHistory:
    if session_id not in session_store:
        session_store[session_id]=ChatMessageHistory()
    return session_store[session_id]

def get_faiss_index(session_id: str):
    if session_id not in faiss_indices:
        dimension = 384  # Dimension of the embeddings
        faiss_indices[session_id] = faiss.IndexFlatL2(dimension)
        faiss_stores[session_id] = []
    return faiss_indices[session_id], faiss_stores[session_id]


def store_in_faiss(data_tuple, query_type, session_id):
    index, faiss_store = get_faiss_index(session_id)

    if query_type == 'customer':
        text = f"User ID: {data_tuple[0]}, Name: {data_tuple[1]} {data_tuple[2]}, Email: {data_tuple[3]}, Phone: {data_tuple[4]}, Address: {data_tuple[5]}, Registration Date: {data_tuple[6]}"
    elif query_type == 'order':
        text = f"Order ID: {data_tuple[0]}, User ID: {data_tuple[1]}, Order Date: {data_tuple[2]}, Total Amount: {data_tuple[3]}, Status: {data_tuple[4]}, Shipping Address: {data_tuple[5]}"
    else:
        text = data_tuple

    embedding_vector = embedding.embed_query(text)
    embedding_vector = np.array(embedding_vector).reshape(1, -1)
    index.add(embedding_vector)
    faiss_store.append(text)
    print(f"Added to FAISS for session {session_id}: {text}")


def search_faiss(query_text, session_id):
    index, faiss_store = get_faiss_index(session_id)

    query_vector = embedding.embed_query(query_text)
    query_vector = np.array(query_vector).reshape(1, -1)

    distances, indices = index.search(query_vector, k=5)

    if indices.size == 0 or indices[0][0] == -1:
        return []

    results = []
    for idx in indices[0]:
        if 0 <= idx < len(faiss_store):
            results.append(faiss_store[idx])

    return results





# QUERYING SQL

# Regex patterns
# 10 digit phone number
PHONE_PATTERN = re.compile(r'\b\d{10}\b')

# 5 digit number followed by 3 uppercase letters
ORDER_ID_PATTERN = re.compile(r'\b\d{5}[A-Z]{3}\b')

def extract_issue_from_response(response_text: str):
    # Example pattern to extract the issue; adjust as needed
    issue_pattern = re.compile(r'Issue:\s*([^.]*)')
    match = issue_pattern.search(response_text)
    return match.group(1) if match else "Issue details not found."

def add_complaint(ticket_no: str, phone: str, issue: str):
    conn = sqlite3.connect('walmart.db')
    cursor = conn.cursor()

    # Insert the complaint into the complaints table
    cursor.execute('''
    INSERT INTO complaints (ticketNo, phone, issue)
    VALUES (?, ?, ?)
    ''', (ticket_no, phone, issue))

    conn.commit()
    conn.close()
    print(f"Complaint added with ticket number {ticket_no}")

def find_phone_number(text: str):
    match = PHONE_PATTERN.search(text)
    return match.group(0) if match else None

def find_order_id(text: str):
    match = ORDER_ID_PATTERN.search(text)
    return match.group(0) if match else None

def query_customer(phone: str):
    conn = sqlite3.connect('walmart.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM customers WHERE phone = ?', (phone,))
    result = cursor.fetchone()
    conn.close()
    return result

def query_order(order_id: str):
    conn = sqlite3.connect('walmart.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM orders WHERE orderId = ?', (order_id,))
    result = cursor.fetchone()
    conn.close()
    return result





# MAKING LLM CHAIN

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", '''You are AISHA, a calm and helpful customer support agent. Answer the queries in {language}.
                    Greet users & introduce yourself only in the first message of the session and ask for phone number.
                    Respond to user queries directly, without greetings or unnecessary repetition or white spaces.
                    DON'T REPEAT THE THINGS YOU HAVE SAID BEFORE.
                    If the user expresses gratitude or says goodbye, acknowledge it politely.
                    If the user's name or phone number is missing, ask for it.
                    For technical issues, provide basic troubleshooting steps.
                    For complaints, try to resolve the complaint, if you are not able to resolve the issue, or customer is not satisfied,
                    create a ticket for the customer. REMEMBER: While creating a ticket, always give a ticket number to the customer.
                    When you are giving a ticket number add this kind of line to your response describing the issue. Issue: write the issue here.
                    The ticket number should be unique and comprise of 2 random uppercase letters followed by 4 random digits.
                    Avoid answering unrelated questions and guide users to stay on topic.
                    Do not offer discounts or promotions.
                    Keep it short, if the query is solved, ask if they have any more queries.
                    If user says thank you or goodbye or issue resolved, just end the conversation.
                    If no further queries, end with: "Thank you for contacting us. Have a great day!"
                      '''),
        # ('assistant', 'Hi! My name is AISHA. How can I help you today?'),
        ('system', 'This is the context of user from Database: {faiss_context}'),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ]
)

output_parser=StrOutputParser()

chain=prompt|model|output_parser


with_message_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)





# MAKING APIs

app=FastAPI(title="AISHA", version="1.0.0", description="AISHA API")

@app.post("/chat")
async def invoke_chat(request: Request):
    data = await request.json()

    input_data = data.get("input", {})
    if not input_data:
        return {"response": "Invalid input format. No content found."}

    content = input_data.get("content", "")
    language = input_data.get("language", "en")

    config = data.get("config", {})
    session_id = config.get("session_id", "")
    

    print(f"Received content: {content}")

    phone_number = find_phone_number(content)
    if phone_number:
        customer = query_customer(phone_number)
        print(customer)
        if customer:
            store_in_faiss(data_tuple=customer, query_type='customer', session_id=session_id)
        else:
            store_in_faiss(data_tuple=f"Customer with phone number {phone_number} not found", query_type='failed', session_id=session_id)

    
    order_id = find_order_id(content)
    if order_id:
        order = query_order(order_id)
        if order:
            store_in_faiss(data_tuple=order, query_type='order', session_id=session_id)
        else:
            store_in_faiss(data_tuple=f'Order with orderId {order_id} not found', query_type='failed', session_id=session_id)

    faiss_results = search_faiss(content, session_id)
    faiss_context = faiss_results if faiss_results else "No relevant context found."
    print(f"FAISS context: {faiss_context}")

    try:
        response = with_message_history.invoke(
            input={
                "input": [HumanMessage(content=content)],
                "faiss_context": faiss_context,
                "language": language
            },
            # This is default syntax used by with_message_history to search history for this session_id using function get_session_history.
            config={"configurable": {"session_id": session_id}}
        )
    except Exception as e:
        response = str(e)

    ticket_no_match = re.search(r'\b[A-Z]{2}\d{4}\b', response)
    if ticket_no_match and not complaint_stores.get(session_id):
        ticket_no = ticket_no_match.group(0)
        issue = extract_issue_from_response(response)
        phone=None
        for context in faiss_context:
            if 'Phone' in context:
                phone=context.split('Phone: ')[1].split(',')[0]
        add_complaint(ticket_no, phone, issue)
        complaint_stores[session_id] = ticket_no
        response=response.replace(f' Issue: {issue}.', '').strip()

    return {"response": response}


@app.get("/cron-job")
async def cron_job():
    return "CJ"

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='localhost', port=8001)