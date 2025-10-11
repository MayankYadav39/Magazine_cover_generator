import streamlit as st
import asyncio
import os
import base64
from pathlib import Path
from mcp_use import MCPAgent, MCPClient
from langchain_groq import ChatGroq
from PIL import Image
import requests
from io import BytesIO

# Set page config
st.set_page_config(
    page_title="Magazine Cover Generator",
    page_icon="📰",
    layout="wide"
)

# Set API key
os.environ['GROQ_API_KEY'] = 'Paste_Your_GROQ_API_KEY_Here'

# MCP Configuration
MCP_CONFIG = {
    "mcpServers": {
        "filesystem": {
            "command": "npx",
            "args": [
                "-y",
                "@modelcontextprotocol/server-filesystem",
                "C:\\Users\\aryam\\Downloads",
                "C:\\Users\\aryam\\Documents"
            ]
        },
        "image-transform": {
            "command": "uv",
            "args": [
                "run",
                "--with",
                "mcp[cli]",
                "mcp",
                "run",
                "D:\\mcp\\pythonProject1\\mcp_server.py"
            ],
            "timeout": 600000
        }
    }
}


async def generate_magazine_cover(image_path: str, user_preferences: dict):
    """Generate magazine cover using MCP agent"""

    # Build dynamic prompt based on user preferences
    prompt = f'''
    Your goal is to convert the provided image into a magazine cover using the image_to_image_tool of the image-transform mcp server.

    Generate a prompt for the flux model (KEEP BELOW 70 WORDS):

    a) Magazine title: "{user_preferences.get('title', 'STYLE')}" - Position prominently at the top, partially behind the subject's head for depth.
    b) Main headline: "{user_preferences.get('headline', 'The Modern Icon')}" - Add bold headline near the top, below the title.
    c) Subheadings: {user_preferences.get('subheadings', 'Fashion Forward, Living Bold')} - Place strategically on left and right.
    *** MAGAZINE STYLE : {user_preferences.get('style', 'Vogue')}
    *** COLOUR SCHEME : {user_preferences.get('color_scheme', 'Minimalist')}
    d) Add aesthetically pleasing design elements and colors to make it look like a magazine cover.
    e) Change background only if it's plain and boring, otherwise keep original.
    f) Use colorful design elements that match the magazine aesthetic.

    The path to the image is {image_path}.

    After receiving output from Flux at "D:\\mcp\\pythonProject1\\output.png", pass the image path and context to start_ocr_correction tool.

    CONTEXT for OCR correction:
    """
    Professional magazine cover featuring the main subject in focus.
    - Main magazine title: "{user_preferences.get('title', 'STYLE')}"
    - Primary headline: "{user_preferences.get('headline', 'The Modern Icon')}"
    - Subheadings include: {user_preferences.get('subheadings', 'Fashion Forward, Living Bold')}
    - Design is clean and professional, typical of high-end magazines
    """
    '''

    client = MCPClient.from_dict(MCP_CONFIG)
    llm = ChatGroq(model_name='meta-llama/llama-4-maverick-17b-128e-instruct', temperature=0.8)
    agent = MCPAgent(llm=llm, client=client, max_steps=30)

    result = await agent.run(prompt)
    return result


def download_image_from_colab(result):
    """Extract and download image from result"""
    try:
        # Parse the result - it might be a string representation
        if isinstance(result, str):
            # Try to parse as dict if it's a string
            import ast
            try:
                result = ast.literal_eval(result)
            except:
                pass

        # Check if result has nested structure from OCR correction
        if isinstance(result, dict):
            # Check for OCR correction response structure
            if 'result' in result and isinstance(result['result'], dict):
                inner_result = result['result']
                if 'final_image_base64' in inner_result:
                    img_data = base64.b64decode(inner_result['final_image_base64'])
                    return Image.open(BytesIO(img_data))

            # Check direct base64 image
            if 'final_image_base64' in result:
                img_data = base64.b64decode(result['final_image_base64'])
                return Image.open(BytesIO(img_data))

            # Check if result contains URL
            if 'final_image_url' in result:
                response = requests.get(result['final_image_url'], timeout=60)
                return Image.open(BytesIO(response.content))

        # Check for local output file as fallback
        if os.path.exists("D:\\mcp\\pythonProject1\\output.png"):
            return Image.open("D:\\mcp\\pythonProject1\\output.png")

        return None
    except Exception as e:
        st.error(f"Error downloading image: {str(e)}")
        st.write(f"Debug - Result structure: {type(result)}")
        if isinstance(result, dict):
            st.write(f"Debug - Result keys: {result.keys()}")
        return None


# UI Layout
st.title("📰 Magazine Cover Generator")
st.markdown("Transform your photos into professional magazine covers using AI")

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Settings")

    st.subheader("Magazine Content")
    title = st.text_input("Magazine Title (1-2 words)", value="STYLE", max_chars=20)
    headline = st.text_input("Main Headline (6-7 words)", value="The Modern Icon", max_chars=50)
    subheadings = st.text_area("Subheadings (comma separated)", value="Fashion Forward, Living Bold", height=100)

    st.subheader("Style Options")
    style = st.selectbox(
        "Magazine Style",
        ["Fashion", "Business", "Lifestyle", "Tech", "Sports", "Entertainment"]
    )

    color_scheme = st.selectbox(
        "Color Scheme",
        ["Vibrant", "Elegant", "Bold", "Minimalist", "Retro"]
    )

# Main content area
col1, col2 = st.columns(2)

with col1:
    st.subheader("📤 Upload Image")
    uploaded_file = st.file_uploader(
        "Choose an image",
        type=['png', 'jpg', 'jpeg'],
        help="Upload a portrait photo for best results"
    )

    if uploaded_file:
        # Display uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption="Original Image", use_container_width=True)

        # Save to temp location
        temp_path = "C:\\Users\\aryam\\Downloads\\temp_upload.png"
        image.save(temp_path)

with col2:
    st.subheader("✨ Generated Cover")

    if uploaded_file:
        if st.button("🎨 Generate Magazine Cover", type="primary", use_container_width=True):
            with st.spinner("🔄 Generating magazine cover... This may take 2-5 minutes"):

                # Progress indicators
                progress_bar = st.progress(0)
                status_text = st.empty()

                try:
                    status_text.text("📤 Uploading image to FAL...")
                    progress_bar.progress(20)

                    # Prepare user preferences
                    user_prefs = {
                        'title': title,
                        'headline': headline,
                        'subheadings': subheadings,
                        'style': style,
                        'color_scheme': color_scheme
                    }

                    status_text.text("🎨 Generating cover design with Flux AI...")
                    progress_bar.progress(40)

                    # Run async generation
                    result = asyncio.run(generate_magazine_cover(temp_path, user_prefs))

                    status_text.text("🔧 Applying OCR corrections...")
                    progress_bar.progress(70)

                    # Download result image
                    output_image = download_image_from_colab(result)

                    progress_bar.progress(100)
                    status_text.text("✅ Complete!")

                    if output_image:
                        st.image(output_image, caption="Generated Magazine Cover", use_container_width=True)

                        # Download button
                        buf = BytesIO()
                        output_image.save(buf, format="PNG")
                        btn = st.download_button(
                            label="⬇️ Download Cover",
                            data=buf.getvalue(),
                            file_name="magazine_cover.png",
                            mime="image/png",
                            use_container_width=True
                        )
                    else:
                        st.warning("⚠️ Could not retrieve final image. Check if OCR correction service is running.")
                        st.info(f"Result: {result}")

                        # Try to show intermediate output
                        if os.path.exists("D:\\mcp\\pythonProject1\\output.png"):
                            st.subheader("Intermediate Result (Before OCR)")
                            intermediate = Image.open("D:\\mcp\\pythonProject1\\output.png")
                            st.image(intermediate, use_container_width=True)

                except asyncio.TimeoutError:
                    st.error("❌ Generation timed out. Please try again.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.exception(e)
                finally:
                    progress_bar.empty()
                    status_text.empty()
    else:
        st.info("👆 Upload an image to get started")

# Footer
st.markdown("---")
st.markdown("""
### 💡 Tips for Best Results
- Use high-quality portrait photos with good lighting
- Ensure the subject is clearly visible and centered
- Avoid cluttered backgrounds
- The AI works best with images of people or products

### 🔧 Troubleshooting
- If generation fails, check that your Colab server is running
- Make sure the MCP server path is correct
- Verify your FAL API key is valid
""")

# Show system status in sidebar
with st.sidebar:
    st.markdown("---")
    st.subheader("System Status")

    # Check if output directory exists
    if os.path.exists("D:\\mcp\\pythonProject1"):
        st.success("✅ MCP Server Path OK")
    else:
        st.error("❌ MCP Server Path Not Found")

    # Check if temp directory is writable
    if os.access("C:\\Users\\aryam\\Downloads", os.W_OK):
        st.success("✅ Upload Directory Writable")
    else:
        st.error("❌ Upload Directory Not Writable")