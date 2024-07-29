import os
from fastapi import File, UploadFile, APIRouter
from session import Track, AudioSource
from pedalboard.io import AudioFile


router = APIRouter()


@router.post("/{session_id}/upload")
def upload(session_id: str, file: UploadFile = File(...)):
    s = Track.load(session_id)
    try:
        contents = file.file.read()
        track_path = os.path.join(s.save_path, "original.wav")
        with open(track_path, "wb") as f:
            f.write(contents)

        t = AudioSource("original", 0.0, "", contents, track_path)
        s.original = t
        s.last_modified = None
        s.save()

    except Exception as e:
        print(e)
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()

    return {"message": f"Successfully uploaded {file.filename}"}
