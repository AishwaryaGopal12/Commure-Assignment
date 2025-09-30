# Commure-Assignment

# 🏥 Hospital Database Agent

This project demonstrates a natural language agent capable of interpreting questions and generating accurate SQL queries to interact with a hospital database.

---

## 📓 Main Notebook

- **`assessment.ipynb`**  
  This is the **main execution notebook** from which the agent can be run. It provides examples, evaluation logic, and test cases for various types of user queries.

---

## 🧱 Project Structure

The codebase is modularized into the following components:

- **`lang_graph.py`**  
  Defines the **LangGraph** including the nodes, edges, and control flow logic for the agent’s execution pipeline.

- **`tools.py`**  
  Contains various **agent tools** such as SQL parsing, schema extraction, error handling, and safety checks.

- **`utils.py`**  
  Includes **utility functions** and test helpers, such as test case execution and result comparison.

- **`agent.py`**  
  Defines the **main query generation agent** as well as the **critic agent**, which validates the correctness of SQL output against user intent.

- **`SQL_Files/`**  
  Directory containing all the SQL scripts used to **create and populate** the hospital database.

- **`Commure Assignment.pdf`**  
  A **detailed report** outlining the system architecture, database design, evaluation methodology, and observations.

---

## ⚙️ Setup Instructions

To run the notebook locally:

1. **Clone the repository:**

```bash
   git clone <your-repo-url>
   cd <your-repo-directory>
```
   
2. 🛠️ **Create and Activate a Virtual Environment**

  It's recommended to use a virtual environment to manage dependencies and avoid conflicts.
  
  ```bash
  # Create a virtual environment named 'venv'
  python -m venv venv
  
  # Activate the virtual environment
  # On macOS/Linux:
  source venv/bin/activate
  
  # On Windows:
  venv\Scripts\activate
  ```

3. 📚 **Installing Required Dependencies**

  After activating the virtual environment, you can install all required packages using the `requirements.txt` file provided in the project.
  
  Run the following command:
  
  ```bash
  pip install -r requirements.txt


