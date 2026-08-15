from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from models.schemas import SessionResponse, StartSessionRequest
from services.engine import apply_challenge_result, to_response
from services.judge import judge
from services.workflow import create_session
import store

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.post("", response_model=SessionResponse)
def start_session(body: StartSessionRequest) -> SessionResponse:
    session = create_session(body.products)
    store.save(session)
    return to_response(session, action="show_challenge")


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(session_id: str) -> SessionResponse:
    session = store.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="session not found")
    action = "done" if session.status == "done" else "show_challenge"
    return to_response(session, action=action)


@router.post("/{session_id}/recordings", response_model=SessionResponse)
async def submit_recording(
    session_id: str,
    video: UploadFile | None = File(default=None),
    demo_result: str | None = Form(default=None),
) -> SessionResponse:
    session = store.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="session not found")
    if session.status == "done":
        return to_response(session, action="done")

    video_bytes = await video.read() if video is not None else b""
    content_type = video.content_type if video is not None else "application/octet-stream"

    product = session.products[session.product_index]
    challenge = product.challenges[product.challenge_index]
    passed, _reason = judge(
        product,
        challenge,
        video_bytes,
        content_type,
        demo_result=demo_result,
    )
    action = apply_challenge_result(session, passed)
    store.save(session)
    return to_response(session, action=action)
