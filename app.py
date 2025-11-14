import streamlit as st
import pandas as pd
import io
import os

# Import the functions from our logic file
from data_analyzer import (
    analyze_dataframe,
    generate_analysis_code,
    safe_execute_code,
    validate_api_key,
)

# --- Streamlit App Configuration ---
st.set_page_config(page_title="AI Data Analyzer", page_icon="🤖", layout="wide")

st.title("🤖 AI-Powered Data Analyzer")
st.write(
    "Upload a CSV file and use natural language to generate data visualizations and analyses."
)

# --- API Key Management in Sidebar ---
st.sidebar.header("Configuration")
api_key_input = st.sidebar.text_input(
    "Enter your Gemini API Key",
    type="password",
    help="Get your key from Google AI Studio.",
)

if api_key_input:
    if st.sidebar.button("Validate and Save Key"):
        with st.spinner("Validating API key..."):
            is_valid = validate_api_key(api_key_input)
            if is_valid:
                st.session_state["api_key"] = api_key_input
                st.session_state["is_key_valid"] = True
                st.sidebar.success("API Key is valid and saved!")
            else:
                st.session_state["is_key_valid"] = False
                st.sidebar.error("Invalid API Key. Please check and try again.")

# --- Main App Logic (only runs if key is valid) ---
if st.session_state.get("is_key_valid", False):
    st.success("API Key validated. You can now upload your data.")

    # 1. File Uploader
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        try:
            # Best Practice: Reset file pointer to the beginning before reading
            uploaded_file.seek(0)
            # To ensure consistent parsing, decode the uploaded file and read it with pandas
            string_data = uploaded_file.getvalue().decode("utf-8")
            # Be explicit with the separator and tell pandas to ignore comment lines starting with '#'
            df = pd.read_csv(io.StringIO(string_data), sep=",", comment="#")

            st.success("CSV file loaded successfully!")

            # Display a preview of the dataframe
            st.write("Data Preview:")
            st.dataframe(df.head())

            # 2. User Prompt
            user_prompt = st.text_input(
                "What would you like to do with this data?",
                placeholder="e.g., 'Show me a bar chart of sales by category'",
            )

            # 3. Generate Button
            if st.button("Generate Analysis"):
                if not user_prompt:
                    st.warning("Please enter a prompt.")
                else:
                    with st.spinner("The AI is thinking..."):
                        # 4. Analyze schema and generate code using the saved API key
                        df_schema, df_head = analyze_dataframe(df)
                        api_key = st.session_state.get("api_key")
                        generated_code = generate_analysis_code(
                            user_prompt, df_schema, df_head, api_key
                        )

                        # 5. Execute the code and display results
                        with st.expander("View Generated Code"):
                            st.code(generated_code, language="python")

                        result = safe_execute_code(generated_code, df)

                        st.subheader("Result")
                        if "image" in result:
                            st.image(result["image"], caption="Generated Plot")
                            # Add a download button for the image
                            st.download_button(
                                label="Download Image",
                                data=result["image"],
                                file_name="generated_plot.png",
                                mime="image/png",
                            )
                            # Clean up the generated image file
                            if os.path.exists("output.png"):
                                os.remove("output.png")
                        elif "error" in result:
                            st.error("An error occurred during code execution:")
                            st.code(result["error"])
                        else:
                            st.info(
                                "The code executed but did not produce a visual output (like 'output.png')."
                            )

        except Exception as e:
            st.error(f"An error occurred: {e}")
else:
    st.warning("Please enter and validate your API key in the sidebar to begin.")
