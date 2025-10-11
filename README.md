
-----

# 📰 Magazine Cover Generator

This project is an AI-powered tool designed for the Inter-IIT Tech Preperation to automatically transform any user-uploaded image into a professional-looking magazine cover. The system uses a multi-stage pipeline involving advanced generative models for image creation and a sophisticated OCR correction module to ensure high-quality, legible text.

-----

## 👥 Team Members

  * Aryaman Tiwari
  * Keshav
  * Anushka Jain
  * Hrishabh Mittal

-----

## ⚙️ Our Approach: A Two-Stage Pipeline

Our solution uses a sophisticated two-stage pipeline to ensure both high visual quality and accurate text rendering on the final magazine cover.

### 1\. Cover Generation with Fine-Tuned FLUX

The core of our image generation is the **FLUX model**. We've fine-tuned this powerful text-to-image diffusion model specifically for the task of creating magazine covers.

  * **Input**: The process starts with a user-provided image and text preferences (like title, headlines, and style).
  * **Process**: An LLM agent (powered by Groq's Llama 4) dynamically crafts a detailed prompt based on the user's input. This prompt guides the fine-tuned FLUX model in an **image-to-image** transformation, adding text, design elements, and stylistic flair to convert the original photo into a draft magazine cover.
  * **Challenge**: While excellent at visual composition, diffusion models often struggle with rendering perfectly accurate and legible text, a phenomenon known as "garbled text."

### 2\. Text Correction with an OCR Pipeline

To solve the garbled text problem, we implemented a dedicated OCR correction module that acts as a post-processing step.

  * **Text Detection with Florence-2**: We first use **Florence-2**, a state-of-the-art vision model, to accurately detect the bounding boxes of all the garbled text on the generated cover.
  * **Text Inpainting with Calligrapher**: Once the incorrect text is located, we use the **Calligrapher** model. It performs a targeted inpainting process:
    1.  It "erases" the garbled text within the detected bounding boxes.
    2.  It then "rewrites" the correct text (from the user's original input) back onto the cover in a font and style that is contextually appropriate.

This two-stage approach allows us to leverage the creative power of FLUX for the visuals while ensuring the final output has crisp, accurate, and professional-looking text.

-----

## 🛠️ System Architecture

The project is built on a client-server architecture to modularize the different components.

  * **Streamlit Client (`streamlit_app.py`)**: This is the user-facing web interface. It allows users to upload an image, specify their preferences for the magazine cover, and view the final result.
  * **MCP Server (`mcp_server.py`)**: The Model Context Protocol (MCP) server acts as the backend orchestrator. It exposes our core functionalities as "tools" that the LLM agent can call.
      * `image_to_image_tool`: This tool interfaces with the FLUX model (hosted on a separate server, exposed via ngrok) to generate the initial cover.
      * `start_ocr_correction`: This tool communicates with our OCR correction service (hosted on Google Colab, also exposed via ngrok) to fix the text.
  * **External Services**:
      * **FLUX Model Server**: A dedicated server hosting the fine-tuned FLUX model.
      * **OCR Correction Server**: A Google Colab notebook running the Florence-2 and Calligrapher models.

-----

## 🚀 How to Run

### Prerequisites

  * Python 3.8+
  * Node.js and `npx`
  * A Groq API Key
  * Ngrok for exposing local servers to the internet.

### Setup Instructions

1.  **Clone the Repository**

    ```bash
    git clone <your-repo-url>
    cd <your-repo-directory>
    ```

2.  **Set Up Backend Services**

      * **FLUX Server**: Launch your FLUX model on a server and expose it using ngrok. Update the `FLUX_NGROK_URL` in `mcp_server.py`.
      * **OCR Server**: Run the Florence/Calligrapher notebook in Google Colab and expose its API via ngrok. Update the `COLAB_API_URL` in `mcp_server.py`.

3.  **Run the MCP Server**

      * Install the required Python packages:
        ```bash
        pip install -r requirements.txt
        ```
      * Start the MCP server. This server will host the tools that the LLM agent will use.
        ```bash
        python mcp_server.py
        ```

4.  **Run the Streamlit Client**

      * Open a new terminal.
      * Set your Groq API key as an environment variable:
        ```bash
        export GROQ_API_KEY='your_groq_api_key_here'
        ```
      * Launch the Streamlit application:
        ```bash
        streamlit run streamlit_app.py
        ```

5.  **Use the Application**

      * Open your web browser and navigate to the local URL provided by Streamlit.
      * Upload an image, fill in your desired magazine text, and click "Generate"\!
