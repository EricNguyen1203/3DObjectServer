from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import grpc
import audio_pb2
import audio_pb2_grpc

router = APIRouter(prefix="/audio", tags=["audio"])


def normalize_text(text: str):
    return text


def stream_audio(text: str, language: str):
    try:
        with grpc.insecure_channel("localhost:50093") as channel:
            stub = audio_pb2_grpc.GenAudioServiceStub(channel)
            request = audio_pb2.AudioGenRequest(text=text, language=language)
            responses = stub.GenAudio(request)
            for response in responses:
                yield response.data
    except Exception as e:
        print(f"[grpc_image_stream] Exception: {str(e)}")
        raise


@router.get("/tts-en")
async def text_to_speech_en(text: str):
    clean_text = normalize_text(text)
    return StreamingResponse(stream_audio(clean_text, "en"), media_type="audio/wav")


@router.get("/tts-vi")
async def text_to_speech_vi(text: str):
    clean_text = normalize_text(text)
    return StreamingResponse(stream_audio(clean_text, "vi"), media_type="audio/wav")
