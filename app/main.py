# main.py
import base64
import io
import os
from dotenv import load_dotenv

from fastapi import FastAPI, APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from PIL import Image
from google import genai

load_dotenv() # GOOGLE_APPLICATION_CREDENTIALS を読み込む
GCP_PROJECT_ID = os.environ["GCP_PROJECT_ID"]
LOCATION = os.environ["LOCATION"]

# Geminiクライアント初期化
_client = genai.Client(
    vertexai=True,
    project=GCP_PROJECT_ID,
    location=LOCATION,
)

# --- アプリケーション設定 ---
app = FastAPI(title="Sample Application")
# Allow all origins for CORS (useful for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====== エンドポイント ======
# 静的ファイル提供
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", include_in_schema=False)
async def root():
    return FileResponse('static/index.html')

class ImageData(BaseModel):
    """Request model for receiving the base64 image string."""
    image_data: str

@app.post("/color-change")
async def color_change(data: ImageData):
    """
    Receives a base64 encoded image, converts it to a red monochrome,
    and returns the new image as a base64 string.
    base64 で受け取った画像の色を赤に変え、base64データを返す関数
    """
    try:
        # --- 1. Base64データをデコード ---
        # "data:image/png;base64," のようなヘッダー部分を分離
        header, encoded = data.image_data.split(",", 1)
        image_bytes = base64.b64decode(encoded)

        # --- 2. 画像データを開く ---
        # バイトデータを画像として読み込む
        image = Image.open(io.BytesIO(image_bytes))
        # 処理のためにRGB形式に変換
        image = image.convert("RGB")

        # --- 3. 画像をピクセルごとに処理 ---
        width, height = image.size
        # 元の画像のピクセルデータを取得
        pixels = image.load() 
        
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                # 輝度（明るさ）を計算して、赤の色合いに変換
                # Y = 0.299*R + 0.587*G + 0.114*B
                luminance = int(0.299 * r + 0.587 * g + 0.114 * b)
                # ピクセルを新しい色（赤の濃淡）で上書き
                pixels[x, y] = (luminance, 0, 0)

        # --- 4. 処理後の画像をBase64にエンコード ---
        # メモリ上のバッファに画像を保存
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        # バッファからバイトデータを取得し、base64文字列にエンコード
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

        # --- 5. 新しいBase64データを返す ---
        # 元のヘッダーを付けて返す
        new_image_data = f"data:image/png;base64,{img_str}"
        return {"image_data": new_image_data, "message": "Image processed successfully"}

    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}, 500

@app.post("/generate-image")
async def generate_image(data: ImageData):
    """
    base64で受け取った画像とプロンプトを元にGeminiで新しい画像を生成し、base64データを返す
    """
    prompt = (
        "Using the provided image of a document, please meticulously retouch the scene "
        "to eliminate all unwanted elements such as shadows, glare, and any visible parts of a hand or fingers. "
        "Ensure the document is perfectly straightened and flattened, simulating a direct overhead shot under soft, "
        "natural light, resulting in a pristine and highly readable digital document. "
        "Do not alter any text or graphics within the document."
    )

    try:
        # Base64データをデコードして画像として開く
        header, encoded = data.image_data.split(",", 1)
        image_bytes = base64.b64decode(encoded)
        image = Image.open(io.BytesIO(image_bytes))

        # image = Image.open('./static/assets/unnamed.png')

        response = _client.models.generate_content(
            model="gemini-2.5-flash-image-preview",
            contents=[prompt, image],
        )

        generated_image_bytes = None
        for part in response.candidates[0].content.parts:
            if part.text is not None:
                print(part.text)
            elif part.inline_data is not None:
                generated_image_bytes = part.inline_data.data

        if generated_image_bytes is None:
            error_message = "Image generation failed. No image data in response."
            raise HTTPException(status_code=500, detail=error_message)

        # 生成された画像をBase64にエンコード
        img_str = base64.b64encode(generated_image_bytes).decode("utf-8")
        # 元のヘッダーを付けて返す
        new_image_data = f"data:image/png;base64,{img_str}"
        return {"image_data": new_image_data, "message": "Image generated successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)