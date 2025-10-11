import os
import base64
import uuid
from io import BytesIO
import sys
import fal_client
import requests
from mcp.server.fastmcp import FastMCP
import os
import base64
import uuid
import sys
import fal_client
import requests
from mcp.server.fastmcp import FastMCP
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

# Initialize MCP server
mcp = FastMCP("image-transform")

os.environ["FAL_KEY"] = "Paste_Your_FAL_KEY_Here"
COLAB_API_URL = "https://grey-unproscribed-sedately.ngrok-free.dev"

# Ensure your FAL_KEY is set
FAL_KEY = os.environ.get("FAL_KEY")
if not FAL_KEY:
    raise RuntimeError("FAL_KEY environment variable must be set")


@mcp.tool()
def start_ocr_correction(image_path: str, context: str) -> dict:
    jobs = {}
    """Start OCR correction and return immediately with job ID, this tool fixes broken text in the generated image from Flux"""
    try:
        if not os.path.exists(image_path):
            return {"error": f"Image not found: {image_path}"}

        job_id = str(uuid.uuid4())
        jobs[job_id] = {"status": "processing", "progress": 0}

        # Start processing in background
        with open(image_path, "rb") as img_file:
            files = {"image": (os.path.basename(image_path), img_file, "image/jpeg")}
            data = {"context": context}

            response = requests.post(
                f"{COLAB_API_URL}/api/correct",
                files=files,
                data=data,
                timeout=3600
            )
            response.raise_for_status()
            result = response.json()

            if result.get("final_image_url"):
                image_url = f"{COLAB_API_URL}{result['final_image_url']}"
                img_data = requests.get(image_url, timeout=600).content
                result["final_image_base64"] = base64.b64encode(img_data).decode("utf-8")

            jobs[job_id] = {"status": "completed", "result": result}

        return {
            "job_id": job_id,
            "status": "completed",
            "message": "OCR completed immediately",
            "result": jobs[job_id].get("result")
        }

    except Exception as e:
        return {"error": f"Failed to process image: {str(e)}"}


import os
import base64
import uuid
from io import BytesIO
import sys
import fal_client
import requests
from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("image-transform")

os.environ["FAL_KEY"] = "Paste_Your_FAL_KEY_Here"
COLAB_API_URL = "https://grey-unproscribed-sedately.ngrok-free.dev"

# Ensure your FAL_KEY is set
FAL_KEY = os.environ.get("FAL_KEY")
if not FAL_KEY:
    raise RuntimeError("FAL_KEY environment variable must be set")


@mcp.tool()
def start_ocr_correction(image_path: str, context: str) -> dict:
    jobs = {}
    """Start OCR correction and return immediately with job ID, this tool fixes broken text in the generated image from Flux"""
    try:
        if not os.path.exists(image_path):
            return {"error": f"Image not found: {image_path}"}

        job_id = str(uuid.uuid4())
        jobs[job_id] = {"status": "processing", "progress": 0}

        # Start processing in background
        with open(image_path, "rb") as img_file:
            files = {"image": (os.path.basename(image_path), img_file, "image/jpeg")}
            data = {"context": context}

            response = requests.post(
                f"{COLAB_API_URL}/api/correct",
                files=files,
                data=data,
                timeout=3600
            )
            response.raise_for_status()
            result = response.json()

            if result.get("final_image_url"):
                image_url = f"{COLAB_API_URL}{result['final_image_url']}"
                img_data = requests.get(image_url, timeout=600).content
                result["final_image_base64"] = base64.b64encode(img_data).decode("utf-8")

            jobs[job_id] = {"status": "completed", "result": result}

        return {
            "job_id": job_id,
            "status": "completed",
            "message": "OCR completed immediately",
            "result": jobs[job_id].get("result")
        }

    except Exception as e:
        return {"error": f"Failed to process image: {str(e)}"}


@mcp.tool()
def image_to_image_tool(image_path: str, prompt: str) -> str:
    """
    Transform an input image using a text prompt with FLUX MODEL to make it into a magazine cover.

    Args:
        image_path: Path to the input image file
        prompt: Text description of desired transformation

    Returns:
        Base64-encoded PNG image
    """
    print(f"DEBUG: Received image_path={image_path}, prompt={prompt}", file=sys.stderr)

    if not os.path.exists(image_path):
        return f"Error: File {image_path} not found."

    # Upload local image to Fal server
    try:
        image_url = fal_client.upload_file(image_path)
        print(f"DEBUG: Uploaded image, got URL: {image_url}", file=sys.stderr)
    except Exception as e:
        return f"Error uploading image: {str(e)}"

    try:
        # Call Fal Kontext LoRA model
        result = fal_client.subscribe(
            "fal-ai/flux-kontext-lora",
            arguments={
                "image_url": image_url,
                "prompt": prompt,
                "loras": [
                    {
                        "path": "https://v3.fal.media/files/elephant/eyeQ1ZtOpNxv-bmOE7iV6_adapter_model.safetensors",
                        "scale": 1.0
                    }
                ],
                "num_inference_steps": 30,
                "guidance_scale": 2.5,
                "output_format": "png",
                "resolution_mode": "2:3"
            },
            with_logs=True
        )
        print(f"DEBUG: Received result: {result}", file=sys.stderr)
    except Exception as e:
        return f"Error generating image: {str(e)}"

    # Convert returned image URL to Base64
    try:
        # Fetch image bytes from URL
        import requests
        img_resp = requests.get(result["images"][0]["url"])
        img_resp.raise_for_status()
        img_bytes = img_resp.content

        with open('output.png', 'wb') as f:
            f.write(img_bytes)

        return 'output.png'
    except Exception as e:
        return f"Error processing output image: {str(e)}"

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
