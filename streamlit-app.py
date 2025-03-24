import streamlit as st
import requests

# Backend FastAPI URL (Ensure this is accessible from Streamlit Cloud)
BACKEND_URL = "http://localhost:8000"  # Adjust as needed

model_mapper = {
    "openai/gpt-4o": "gpt-4o-2024-08-06",
    "openai/gpt-3.5-turbo": "gpt-3.5-turbo-0125",
    "openai/gpt-4": "gpt-4-0613",
    "openai/gpt-4o-mini": "gpt-4o-mini-2024-07-18",
    "gemini/gemini-1.5-pro": "gemini/gemini-1.5-pro",
    "gemini/gemini-2.0-flash-lite": "gemini/gemini-2.0-flash-lite"
}

available_models = list(model_mapper.keys())

# Function to call the query API
def rag(year, qtr, model, prompt):
    url = f"{BACKEND_URL}/qa"
    data = {
        "year": year,
        "qtr": qtr.replace("Q", ""),  # Strip "Q" from quarter
        "model": model_mapper[model],
        "prompt": prompt
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.ConnectionError:
        st.error("Error: Unable to connect to the backend. Please ensure the server is running and accessible.")
    except requests.Timeout:
        st.error("Error: The request timed out. Please try again later.")
    except requests.RequestException as e:
        st.error(f"Error: An unexpected issue occurred. {str(e)}")
    
    return None  # Return None if an error occurs

# Streamlit UI
st.title("NVIDIA Agentic RAG Explorer")

mode = 'nvidia'
st.header("Financial Report Query")

# Create side-by-side columns for Year, Quarter, and Model selection
col1, col2, col3 = st.columns([1, 1, 1.5])

with col1:
    year = st.selectbox("Select Year:", [str(yr) for yr in range(2021, 2026)], index=4)

with col2:
    qtr = st.selectbox("Select Quarter:", ['Q1', 'Q2', 'Q3', 'Q4'], index=0)

with col3:
    model_choice = st.selectbox("Select the data source:", available_models, index=available_models.index("gemini/gemini-1.5-pro"))

# User input for query
query = st.text_area("Enter your query:", "", height=150)

# Button to submit the query
if st.button("Submit Query"):
    if query.strip():
        with st.spinner("Querying the backend..."):
            result = rag(year, qtr, model_choice, query)

        if result and "markdown" in result:
            st.subheader("Generated Response:")
            st.write(result["markdown"])
        elif result is None:
            st.error("Failed to retrieve data. Please check the backend connection.")
        else:
            st.error("Something went wrong.")
    else:
        st.error("Please enter a valid query.")
