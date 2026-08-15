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
export default function LiveVerificationPage() {
  const navigate = useNavigate();
  const video = useRef();
  const recorder = useRef();
  const chunks = useRef([]);
  const timer = useRef();
  const sessionCountdownTimer = useRef();
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
  const [remaining, setRemaining] = useState(0);
  const [sessionPhase, setSessionPhase] = useState("camera_initializing");
  const [sessionCountdown, setSessionCountdown] = useState(3);
  const startCamera = async () => {
    try {
      const stream = await camera.start();
      if (video.current) video.current.srcObject = stream;
      const sessionId = await ensureSession();
      const first = await verificationApi.startVerification(sessionId);
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
      camera.stop();
      recorder.current?.state === "recording" && recorder.current.stop();
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
    )
      recordChallenge();
  }, [state, camera.status, challenge, sessionPhase]);
  const recordChallenge = () => {
    const stream = camera.streamRef.current;
    if (!stream) return;
    setState("CHALLENGE_RECORDING");
    setRemaining(challenge.durationSeconds);
    chunks.current = [];
    if (window.MediaRecorder) {
      const r = new MediaRecorder(stream, {
        mimeType: MediaRecorder.isTypeSupported("video/webm")
          ? "video/webm"
          : undefined,
      });
      r.ondataavailable = (event) =>
        event.data.size && chunks.current.push(event.data);
      r.onstop = submitClip;
      r.start();
      recorder.current = r;
    }
    timer.current = setInterval(
      () =>
        setRemaining((value) => {
          if (value <= 1) {
            clearInterval(timer.current);
            if (recorder.current?.state === "recording")
              recorder.current.stop();
            else submitClip();
            return 0;
          }
          return value - 1;
        }),
      1000,
    );
  };
  const submitClip = async () => {
    setState("CHALLENGE_UPLOADING");
    const clip = new Blob(chunks.current, { type: "video/webm" });
    const result = await verificationApi.submitChallengeVideo(
      "demo",
      challenge.id,
      clip,
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
  if (state === "ERROR")
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
