import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { VideoOff } from "lucide-react";
import PageShell from "@/components/refund/PageShell";
import { PrimaryButton } from "@/components/refund/Buttons";
import CurrentActionCard from "@/components/refund/CurrentActionCard";
import {
  CameraControls,
  CheckHistory,
} from "@/components/refund/CameraOverlay";
import useCamera from "@/hooks/useCamera";
import { verificationApi } from "@/services/mockVerificationApi";
import { useRefundSession } from "@/state/RefundSessionContext";

const STILL_COUNT = 8;

function grabJpeg(videoEl) {
  if (!videoEl || !videoEl.videoWidth) return Promise.resolve(null);
  const canvas = document.createElement("canvas");
  const max = 960;
  const scale = Math.min(1, max / Math.max(videoEl.videoWidth, videoEl.videoHeight));
  canvas.width = Math.round(videoEl.videoWidth * scale);
  canvas.height = Math.round(videoEl.videoHeight * scale);
  canvas.getContext("2d").drawImage(videoEl, 0, 0, canvas.width, canvas.height);
  return new Promise((resolve) =>
    canvas.toBlob((blob) => resolve(blob), "image/jpeg", 0.85),
  );
}

export default function LiveVerificationPage() {
  const navigate = useNavigate();
  const video = useRef();
  const recorder = useRef();
  const chunks = useRef([]);
  const stills = useRef([]);
  const stillGrabs = useRef([]);
  const stillTimers = useRef([]);
  const timer = useRef();
  const sessionCountdownTimer = useRef();
  const backendSession = useRef(null);
  const {
    selectedProduct,
    issueDescription,
    ensureSession,
    setChallenge,
    completeChallenge,
    completedChallenges,
  } = useRefundSession();
  const camera = useCamera();
  const [state, setState] = useState("CAMERA_INITIALIZING");
  const [challenge, setLocalChallenge] = useState(null);
  const [sessionPhase, setSessionPhase] = useState("camera_initializing");
  const [sessionCountdown, setSessionCountdown] = useState(3);

  const startCamera = async () => {
    try {
      const stream = await camera.start();
      if (video.current) video.current.srcObject = stream;
      const sid = await ensureSession();
      backendSession.current = sid;
      const first = await verificationApi.startVerification(sid);
      setLocalChallenge(first);
      setChallenge(first);
      setState("CHALLENGE_READY");
    } catch {
      setState("ERROR");
    }
  };

  useEffect(() => {
    if (!selectedProduct || !issueDescription) {
      navigate("/");
      return;
    }
    startCamera();
    return () => {
      clearInterval(timer.current);
      clearTimeout(sessionCountdownTimer.current);
      stillTimers.current.forEach(clearTimeout);
      camera.stop();
      if (recorder.current?.state === "recording") recorder.current.stop();
    };
  }, []);

  useEffect(() => {
    if (
      camera.status === "ready" &&
      challenge &&
      sessionPhase === "camera_initializing"
    ) {
      setSessionCountdown(3);
      setSessionPhase("countdown");
    }
  }, [camera.status, challenge, sessionPhase]);

  useEffect(() => {
    if (sessionPhase !== "countdown") return;
    sessionCountdownTimer.current = window.setTimeout(() => {
      if (sessionCountdown <= 1) setSessionPhase("active");
      else setSessionCountdown((value) => value - 1);
    }, 1000);
    return () => clearTimeout(sessionCountdownTimer.current);
  }, [sessionPhase, sessionCountdown]);

  useEffect(() => {
    if (
      state === "CHALLENGE_READY" &&
      camera.status === "ready" &&
      challenge &&
      sessionPhase === "active"
    ) {
      recordChallenge();
    }
  }, [state, camera.status, challenge, sessionPhase]);

  const captureStill = () => {
    const job = grabJpeg(video.current).then((blob) => {
      if (blob && stills.current.length < STILL_COUNT) stills.current.push(blob);
    });
    stillGrabs.current.push(job);
    return job;
  };

  const recordChallenge = () => {
    const stream = camera.streamRef.current;
    if (!stream) return;
    setState("CHALLENGE_RECORDING");
    chunks.current = [];
    stills.current = [];
    stillGrabs.current = [];
    stillTimers.current.forEach(clearTimeout);
    stillTimers.current = [];
    const durationMs = (challenge.durationSeconds || 8) * 1000;
    captureStill();
    for (let i = 1; i < STILL_COUNT; i++) {
      const delay = Math.round((durationMs * i) / (STILL_COUNT - 1));
      stillTimers.current.push(window.setTimeout(captureStill, delay));
    }
    if (window.MediaRecorder) {
      const mime = MediaRecorder.isTypeSupported("video/webm")
        ? "video/webm"
        : undefined;
      const r = new MediaRecorder(stream, mime ? { mimeType: mime } : undefined);
      r.ondataavailable = (event) =>
        event.data.size && chunks.current.push(event.data);
      r.onstop = submitClip;
      r.start(400);
      recorder.current = r;
    }
    let ticks = challenge.durationSeconds || 8;
    timer.current = setInterval(() => {
      ticks -= 1;
      if (ticks <= 0) {
        clearInterval(timer.current);
        captureStill();
        if (recorder.current?.state === "recording") recorder.current.stop();
        else submitClip();
      }
    }, 1000);
  };

  const submitClip = async () => {
    setState("CHALLENGE_UPLOADING");
    await Promise.all(stillGrabs.current);
    const clip = new Blob(chunks.current, { type: "video/webm" });
    const result = await verificationApi.submitChallengeVideo(
      backendSession.current,
      challenge.id,
      clip,
      stills.current,
    );
    setState(
      result.verdict === "passed" ? "CHALLENGE_PASSED" : "CHALLENGE_FAILED",
    );
    completeChallenge({
      id: challenge.id,
      instruction: challenge.instruction,
      verdict: result.verdict,
    });
    setTimeout(() => {
      if (result.complete) {
        camera.stop();
        navigate("/processing");
      } else {
        setLocalChallenge(result.next);
        setChallenge(result.next);
        setState("CHALLENGE_READY");
      }
    }, 950);
  };

  if (state === "ERROR") {
    return (
      <PageShell className="justify-center">
        <div className="refund-surface p-6 text-center">
          <VideoOff
            className="mx-auto text-muted-foreground"
            size={30}
            strokeWidth={1.6}
          />
          <h1 className="mt-4 text-xl font-semibold tracking-[-0.01em] text-foreground">
            Camera unavailable
          </h1>
          <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
            Please allow camera access to continue your visual check.
          </p>
          <PrimaryButton className="mt-6" onClick={startCamera}>
            Try again
          </PrimaryButton>
          <button
            onClick={() => navigate("/prepare")}
            className="mt-4 text-sm font-medium text-primary"
          >
            Upload a video instead
          </button>
        </div>
      </PageShell>
    );
  }

  return (
    <main className="relative mx-auto min-h-dvh max-w-[540px] overflow-hidden bg-foreground">
      <video
        ref={video}
        autoPlay
        playsInline
        muted
        className="absolute inset-0 h-full w-full object-cover"
      />
      <div className="absolute inset-0 bg-black/35" />
      <div className="relative z-10 flex min-h-dvh flex-col px-5 pb-[max(24px,env(safe-area-inset-bottom))] pt-[max(20px,env(safe-area-inset-top))]">
        <CurrentActionCard challenge={challenge} state={state} />
        {state === "CHALLENGE_RECORDING" && (
          <div className="mt-3 flex items-center justify-center gap-2 text-[11px] font-semibold tracking-[0.12em] text-white">
            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-primary" />
            RECORDING
          </div>
        )}
        <div className="mt-auto">
          <CheckHistory items={completedChallenges} />
          <div className="mt-5">
            <CameraControls
              onFlip={async () => {
                const stream = await camera.flip();
                video.current.srcObject = stream;
              }}
            />
          </div>
        </div>
      </div>
      {sessionPhase === "countdown" && (
        <div className="absolute inset-0 z-20 grid place-items-center bg-foreground/40 backdrop-grayscale backdrop-blur-sm">
          <span
            key={sessionCountdown}
            className="animate-in fade-in zoom-in-95 duration-200 text-8xl font-semibold tracking-[-0.02em] text-white"
          >
            {sessionCountdown}
          </span>
        </div>
      )}
    </main>
  );
}
