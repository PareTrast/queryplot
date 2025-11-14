import pandas as pd
import io
import traceback
import os
import google.generativeai as genai
from dotenv import load_dotenv

# --- Helper Functions ---


def analyze_dataframe(df: pd.DataFrame) -> tuple[str, str]:
    """
    Analyzes a DataFrame to extract its schema and a sample of its data.
    """
    schema_buffer = io.StringIO()
    df.info(buf=schema_buffer)
    df_schema = schema_buffer.getvalue()
    df_head = df.head().to_string()
    return df_schema, df_head


def validate_api_key(api_key: str) -> bool:
    """Pings the AI model to validate the API key."""
    try:
        genai.configure(api_key=api_key)
        # Perform a lightweight, inexpensive API call to check validity
        list(genai.list_models())
        return True
    except Exception:
        return False


def generate_analysis_code(
    user_prompt: str, df_schema: str, df_head: str, api_key: str
) -> str:
    """
    Constructs a detailed prompt and sends it to an AI model to generate Python code.
    """
    try:
        if not api_key:
            raise ValueError("API key is missing.")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-pro")  # Using a stable, recent model
    except Exception as e:
        return f"print('Error configuring AI model: {e}')"

    system_instruction = """
    You are an expert Python data analyst. Your task is to generate Python code
    to analyze and visualize a pandas DataFrame.

    - The DataFrame is already loaded and available in a variable named `df`.
    - You must generate code that uses pandas, matplotlib, or seaborn.
    - Your code should produce a single plot or a DataFrame as output.
    - IMPORTANT: To display the output, you must save any generated plot to a file
      named 'output.png'. If the result is a DataFrame, it should be the final
      expression in the script.
    - Do not include any sample data creation (e.g., `pd.DataFrame(...)`).
    - The code should be a single, executable snippet.
    """

    full_prompt = f"""
    System Instruction:
    {system_instruction}

    Here is the schema of the DataFrame `df`:
    {df_schema}

    Here are the first 5 rows of the data:
    {df_head}

    User Request:
    "{user_prompt}"

    Generate the Python code to fulfill this request.
    """

    print("--- Sending Prompt to AI Model ---")

    try:
        response = model.generate_content(full_prompt)
        generated_code = response.text
    except Exception as e:
        return f"print('Error calling AI model: {e}')"

    # Clean up the code received from the model (e.g., remove markdown backticks)
    if generated_code.strip().startswith("```python"):
        generated_code = generated_code.strip()[9:].strip("`").strip()

    print("\n--- AI Generated Code ---")
    print(generated_code)
    return generated_code


def safe_execute_code(code: str, df: pd.DataFrame) -> dict:
    """
    Safely executes the generated code in a restricted environment.
    """
    # The `execution_globals` dictionary defines the environment for the executed code.
    # We only expose the DataFrame `df` and necessary libraries to it.
    execution_globals = {"df": df, "pd": pd}
    output = {}

    print("\n--- Executing Code ---")
    try:
        # WARNING: In a production system, `exec()` is a major security risk.
        # This code should be run in a properly isolated sandbox.
        exec(code, execution_globals)

        # Check if the AI followed our instruction to create 'output.png'.
        # A more advanced method would be to write to an in-memory buffer.
        try:
            with open("output.png", "rb") as f:
                output["image"] = f.read()
                print("Successfully captured 'output.png'.")
        except FileNotFoundError:
            # This is expected if the code generated a DataFrame or text.
            print("No 'output.png' found. The script may have produced other output.")

    except Exception as e:
        print(f"An error occurred during code execution: {e}")
        output["error"] = traceback.format_exc()

    return output


def main():
    """
    A simple main function to test the logic from the command line.
    """
    # 1. Load Data
    csv_data = """
Category,Sales,Date
Electronics,1500,2023-01-15
Clothing,800,2023-01-16
Groceries,450,2023-01-16
Electronics,2200,2023-01-17
Books,300,2023-01-18
"""
    df = pd.read_csv(io.StringIO(csv_data))
    print("--- Original DataFrame ---")
    print(df)
    print("-" * 26)

    # 2. Analyze Schema for the AI
    df_schema, df_head = analyze_dataframe(df)

    # 3. Get User's Request
    user_prompt = "Create a pie chart showing the distribution of sales by category."

    # For local testing, load the key from .env
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")

    # 4. & 5. Generate and Execute Code
    generated_code = generate_analysis_code(user_prompt, df_schema, df_head, api_key)
    result = safe_execute_code(generated_code, df)

    # 6. Process the Result
    print("\n--- Final Result ---")
    if "image" in result:
        print("An image was generated. In a real app, you would display this.")
    elif "error" in result:
        print("An error occurred during execution:")
        print(result["error"])
    else:
        print("Code executed, but no visual output was captured.")


if __name__ == "__main__":
    main()
