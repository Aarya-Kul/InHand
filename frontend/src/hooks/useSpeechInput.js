import { useRef, useState } from "react";
const demo = "The right side was cracked when I opened the package.";

export default function useSpeechInput(onTranscript) {
  const [listening, setListening] = useState(false);
  const timerRef = useRef(null);
  const recognitionRef = useRef(null);
  const start = () => {
    setListening(true);
    const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (Recognition) {
      const recognition = new Recognition(); recognition.continuous = true; recognition.interimResults = true;
      recognition.onresult = (event) => onTranscript(Array.from(event.results).map((result) => result[0].transcript).join(""));
      recognition.onend = () => setListening(false); recognition.start(); recognitionRef.current = recognition;
    } else {
      let count = 0; timerRef.current = setInterval(() => { count += 1; onTranscript(demo.slice(0, Math.min(demo.length, count * 7))); if (count * 7 >= demo.length) clearInterval(timerRef.current); }, 90);
    }
  };
  const stop = () => { recognitionRef.current?.stop(); clearInterval(timerRef.current); setListening(false); };
  return { listening, start, stop };
}