import { useCallback, useEffect, useRef, useState } from "react";

export default function useCamera() {
  const [status, setStatus] = useState("idle");
  const [facingMode, setFacingMode] = useState("environment");
  const streamRef = useRef(null);
  const stop = useCallback(() => { streamRef.current?.getTracks().forEach((track) => track.stop()); streamRef.current = null; }, []);
  const start = useCallback(async (mode = facingMode) => {
    stop(); setStatus("loading");
    try { const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: { ideal: mode } }, audio: false }); streamRef.current = stream; setStatus("ready"); return stream; }
    catch (error) { setStatus(error.name === "NotAllowedError" ? "denied" : "error"); throw error; }
  }, [facingMode, stop]);
  const flip = useCallback(async () => { const next = facingMode === "environment" ? "user" : "environment"; setFacingMode(next); return start(next); }, [facingMode, start]);
  useEffect(() => stop, [stop]);
  return { status, streamRef, start, stop, flip, facingMode };
}