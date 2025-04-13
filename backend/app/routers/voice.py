from fastapi import APIRouter, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from openai import OpenAI
from llama_index.core import VectorStoreIndex
from llama_index.core.schema import Document

client = OpenAI()  # assumes OPENAI_API_KEY is set in your environment

router = APIRouter(
    prefix="/voice",
    tags=["Voice"],
)

class ActivityJSON(BaseModel):
    name: str
    description: str
    expense: float
    location: str
    category: str
    repeat: bool
    interval: str  # "none", "daily", "weekly", "monthly", "yearly"

@router.post("/process", response_model=ActivityJSON)
async def process_voice_message(file: UploadFile):
    """
    Endpoint to process a voice message and convert it into a structured JSON object.
    """
    try:
        # Step 1: Save file temporarily
        contents = await file.read()
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(contents)

        # Step 2: Transcribe using new OpenAI API client
        with open(temp_path, "rb") as f:
            transcription_response = client.audio.transcriptions.create(
                model="whisper-1",
                file=f
            )
        transcribed_text = transcription_response.text
        print(f"Transcribed text: {transcribed_text}")
        if not transcribed_text:
            raise HTTPException(status_code=400, detail="Failed to transcribe the audio file.")

        # Step 3: Convert transcribed text to JSON via LlamaIndex
        documents = [Document(text=transcribed_text)]
        index = VectorStoreIndex.from_documents(documents)
        query_engine = index.as_query_engine()
        query = "Convert the following text into a JSON object with the format: { 'name': 'string', 'description': 'string', 'expense': number, 'location': 'string', 'category': 'string', 'repeat': bool, 'interval': 'none', 'daily', 'weekly', 'monthly', 'yearly' }"
        response = query_engine.query(query)
        json_data = response.response.strip()

        return JSONResponse(content=json_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
