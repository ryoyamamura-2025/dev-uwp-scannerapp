# main.py
from fastapi import FastAPI, APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import uvicorn

# --- アプリケーション設定 ---
app = FastAPI(title="Sample Application")

# ====== エンドポイント ======
# 静的ファイル提供
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", include_in_schema=False)
async def root():
    return FileResponse('static/index.html')

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)