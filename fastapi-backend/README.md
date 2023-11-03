# Assignment3-QAChatApplication-VectorEmbeddings
End-user facing question-answering chatbot application built using microservices architecture. Stack: Streamline, FastAPI, Airflow, Pinecone, Docker


## Abstract
This project entails the development of a comprehensive system in two distinct parts. Part 1 centers around the automation of embedding creation and the population of a Vector database using Apache Airflow. This includes the creation of two pipelines, one for data acquisition and embedding generation, and another for inserting records into the Pinecone vector database. Part 1 incorporates data validation checks, metadata extraction, and the efficient handling of PDF files. Part 2 introduces a client-facing application built with FastAPI and Streamlit, offering user registration and secure login mechanisms with JWT authentication. The application leverages a SQL database to store user credentials and logs. Users gain access to a Question Answering interface that can query the Pinecone vector database for information. Furthermore, they can select from a variety of preprocessed forms and documents for querying. The entire system is containerized and deployed to a public cloud platform to ensure widespread accessibility.

## Team Members 👥
- Aditya Kawale
  - NUID 002766716
  - Email kawale.a@northeastern.edu
- Nidhi Singh
  - NUID 002925684
  - Email singh.nidhi1@northeastern.edu
- Uddhav Zambare
  - NUID 002199488
  - Email zambare.u@northeastern.edu


## Project Structure
```text
backend
├── Pipfile
├── Pipfile.lock
├── README.md
├── example.env
├── fastapiservice
│   ├── __init__.py
│   ├── filecache
│   │   └── README.md
│   ├── postman
│   │   └── damg7245-assgn2-chatbot-private-files.postman_collection.json
│   ├── src
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── chatanswer.py
│   │   ├── processpdf.py
│   │   └── utilities
│   │       ├── __init__.py
│   │       └── customexception.py
│   └── test
│       ├── __init__.py
│       └── test_app.py
└── fine-tune model
    └── create-model.ipynb
```

```text
frontend
├── README.md
├── diagram
│   ├── architecture-assgn1-generator.py
│   └── architecture-assgn2-generator.py
├── images
│   ├── pdf_processing_flow.png
│   ├── qa_chatbot_for_pdfs_architecture.png
│   ├── streamlit.png
│   └── user.png
├── main.py
├── pages
│   ├── architecture-assign1.py
│   └── architecture-assign2.py
└── requirements.txt
```

## Links 📎
1. Codelab Doc - [link](https://codelabs-preview.appspot.com/?file_id=1GZnCnwqlNUug0sMdtQ-UlrRjIQoFD-XferMC06DVpyc#0)
2. Nougat Library - [link](https://facebookresearch.github.io/nougat/)
3. SEC Forms - [link](https://www.sec.gov/forms)
4. PyPDF Documentation - [link](https://pypdf.readthedocs.io/en/stable/)
5. Open AI Cookbook - [link](https://github.com/openai/openai-cookbook/tree/main/examples/fine-tuned_qa)
6. Streamlit - [link](https://streamlit.io/)

## Architecture 👷🏻‍♂️

![alt text](frontend/images/qa_chatbot_for_pdfs_architecture.png)

## Project Workflow

### Step 1: Input PDF URLs
- Users initiate the process by providing web links to PDF documents.
- The system validates and downloads the PDFs, saving them in cache memory for further processing.

### Step 2: Choose PDF Processor
- Users choose between PyPDF and Nougat for text extraction from the PDFs.

### Step 3: Create Sections of Processed PDF
- Text is segmented into coherent sections of approximately 1000 tokens.
- Sections are grouped and embedded for convenient access.

### Step 4: Generate a Model
- Select the "gpt-3.5-turbo-instruct" model for AI-based Q&A.
- Create question-answer pairs for model training.
- Format the data for fine-tuning and use the Open AI Finetuning Job API.

### Step 5: Chat with Your Personal Chatbot
- Users can interact with the fine-tuned model:
  - Provide a question.
  - The chatbot searches for relevant context.
  - Embeddings are generated and contexts ranked.
  - The top contexts are sent to the model for an answer, which is returned to the user.


## Steps to Execute

App can be directly accessed from Streamlit Cloud via [link](https://team7-a2-frontend.streamlit.app/)

*OR*

1. **Clone the Repository**

    Clone the [repository](https://github.com/BigDataIA-Fall2023-Team7/Assignment3-QAChatApplication-VectorEmbeddings.git) to your local machine:
   ```
   git clone <repository_url>
   ```

**Backend**

1. **Open the Backend folder**
    Navigate to the module directory:
   ```
   cd backend
   ```

2. **Create a .env file**
    Create a `.env` file with the necessary environment variables and API Keys. Reference: [example.env](example.env)

3. **Install Dependencies:**

   Open the terminal in VSCode and run the following commands:

   ```shell
   pipenv install --dev
   ```

4. **Activate Virtual Environment:**

   To activate the virtual environment, run:

   ```shell
   pipenv shell
   ```

5. **Run the Backend Server:**

   Start the backend server using Uvicorn. Run the following command:

   ```shell
   uvicorn fastapiservice.src.app:app --reload
   ```

   Your backend API will be accessible at [http://127.0.0.1:8000](http://127.0.0.1:8000).

**Frontend**

1. **Open the Frontend folder**
    Navigate to the module directory:
   ```
   cd frontend
   ```

2. **Create a Virtual Environment:**
    Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. **Install Frontend Dependencies:**

   In the activated virtual environment, install the required Python packages:

   ```shell
   pip install -r requirements.txt
   ```

4. **Upgrade Pip (Optional):**

   You can upgrade Pip to the latest version if needed:

   ```shell
   pip install --upgrade pip
   ```

5. **Run the Frontend Application:**

   To start the frontend application, run the following command:

   ```shell
   streamlit run main.py
   ```

## Creating Your Own Fine-Tuned Language Model

1. Save a CSV file with 'context' and 'tokens' columns in the 'backend/fine-tune model' directory.
2. Open 'create-model.ipynb' in your Jupyter Notebook environment.
3. Modify the filepath in the first code snippet to point to your CSV file.
4. Follow the instructions in the notebook to fine-tune your model.


## Scope
The project scope involves two main parts. Part 1 focuses on automating the creation of embeddings and populating the Vector database using Apache Airflow. This entails developing two separate Airflow pipelines, one for data acquisition and embedding generation and another for inserting records into the Pinecone vector database. The pipelines should handle PDF files and include data validation checks, embedding generation, and metadata extraction. In Part 2, a client-facing application will be created using FastAPI and Streamlit. This application will feature user registration, login functionality with JWT authentication, and SQL database storage for login credentials and application logs. Users will have access to a Question Answering interface, which can query a Pinecone vector database using a similarity search technique. Additionally, users will be able to select from various preprocessed forms for querying, and the deployment will involve containerization and deployment to a public cloud platform for public access.

## Contribution 🤝
*   Aditya : 34`%` 
*   Nidhi : 33`%`
*   Uddhav : 33`%`

## Individual Distribution ⚖️

| **Developer** |          **Deliverables**          	            |
|:-------------:|:-------------------------------------------------:|
|      Aditya   | Airflow Pipeline 1                                |
|      Aditya   | Integration of embeddings to Airflow pipeline2    |
|      Uddhav   | Streamlit Frontend Code                           |
|      Uddhav   | Python code for embeddings and Pinecone setup     |
|      Nidhi    | FastAPI & JWT implementation and testing          |
|      Nidhi    | Docker code & Documentation                       |

---
---
> WE ATTEST THAT WE HAVEN’T USED ANY OTHER STUDENTS’ WORK IN OUR ASSIGNMENT AND ABIDE BY THE POLICIES LISTED IN THE STUDENT HANDBOOK.