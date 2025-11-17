# QueryPlot

This project is a Streamlit web application that allows users to upload a CSV file and use natural language prompts to automatically generate data analyses and visualizations. It leverages a Large Language Model (LLM) like Google's Gemini to understand user requests and generate the corresponding Python code for analysis.

## Features

-   **Natural Language Interface**: Instead of writing Python code, simply ask the AI what you want to see (e.g., "Plot a bar chart of Tornadoes by Date").
-   **CSV Upload**: Easily upload your own datasets for analysis.
-   **Code Generation**: The application generates and displays the Python (pandas, matplotlib, seaborn) code used for the analysis.
-   **Visualization**: View generated plots and charts directly in the web app.
-   **Modular Design**: The core analysis logic (`data_analyzer.py`) is separate from the user interface (`app.py`), making it easy to customize or integrate into other projects.

## Requirements

-   Python 3.7+
-   An API key from an LLM provider (the current implementation uses Google's Gemini).

## Setup and Installation

Follow these steps to get the application running on your local machine.

### 1. Clone the Repository

First, clone this repository to your local machine (or simply download the files).

```bash
git clone <your-repository-url>
cd <repository-folder>
```

### 2. Install Dependencies

Install the required Python libraries using pip.

```bash
pip install streamlit pandas google-generativeai python-dotenv
```

### 3. Set Up Your API Key

This application requires an API key to communicate with a generative AI model. The current code is configured for Google's Gemini API.

1.  **Get an API Key**: Visit Google AI Studio to create and obtain your free Gemini API key.

2.  **Create a `.env` file**: In the root directory of the project, create a new file named `.env`.

3.  **Add the Key**: Open the `.env` file and add your API key in the following format. Be sure to replace `"YOUR_API_KEY_HERE"` with your actual key.

    ```
    GEMINI_API_KEY="YOUR_API_KEY_HERE"
    ```

    The application uses the `python-dotenv` library to automatically load this key, keeping it secure and out of your source code.

## How to Use

### Running the Web App

To start the user-friendly web interface, run the following command in your terminal from the project's root directory:

```bash
streamlit run app.py
```

Your web browser will open with the application. From there, you can upload your CSV file, type your analysis request into the text box, and click "Generate Analysis".

### Using the Core Logic Script (for advanced users)

If you are a developer and wish to use or test the core logic directly, you can run the `data_analyzer.py` script. This script contains a `main()` function for testing purposes.

```bash
python data_analyzer.py
```
