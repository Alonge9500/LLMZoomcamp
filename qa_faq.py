import streamlit as st
import time  # For simulating a long-running process
from openai import OpenAI
from elasticsearch import Elasticsearch


client = OpenAI(
    base_url='http://localhost:11434/v1/',
    api_key='ollama',
)

es_client = Elasticsearch('http://localhost:9200')


def elastic_search_query(query):
    search_query = {
        "size": 3,
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": query,
                        "fields": ["question^4", "text"],
                        "type": "best_fields"
                    }
                },
                "filter": {
                    "term": {
                        "course": "machine-learning-zoomcamp"
                    }
                }
            }
        }
    }
    response = es_client.search(index="course-questions", body=search_query)
    
    results_doc = [hit['_source'] for hit in response['hits']['hits']]
    return results_doc
def build_prompt(query, search_results):
    prompt_template = """
    You're a course teaching assistant. Answer the QUESTION based on the CONTEXT from the FAQ database.
    Use only the facts from the CONTEXT when answering the QUESTION.

    QUESTION: {question}

    CONTEXT: 
    {context}
    """.strip()

    context = ""
    for doc in search_results:
        context += f"section: {doc['section']}\nquestion: {doc['question']}\nanswer: {doc['text']}\n\n"

    prompt = prompt_template.format(question=query, context=context).strip()
    return prompt

def llm(prompt):
    response = client.chat.completions.create(
        model='phi3',
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# Function that simulates a long-running process (replace with your actual 'rag' function)
def rag(q):
    #st.write('Im here')
    #search_results = elastic_search_query(answer)
    #st.write('Im here')
    #prompt = build_prompt(answer, search_results)
    #st.write(prompt)
    answer = llm(q)
    # Simulating a delay of 5 seconds
    time.sleep(5)
    return f"Processed input: {answer}"

# Streamlit app layout
def main():
    st.title("Streamlit App with Function Execution")

    # Input box for user input
    user_input = st.text_input("Enter your input:")

    # Button to trigger the 'rag' function
    if st.button("Ask"):
        # Display loading message
        with st.spinner('Processing...'):
            # Call the 'rag' function with user input
            result = rag(user_input)
            # Display the result after processing
            st.success(result)

if __name__ == "__main__":
    main()
