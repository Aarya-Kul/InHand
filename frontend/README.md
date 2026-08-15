# Frontend

React + Vite placeholder. Works in a phone browser (use `npm run dev -- --host` and the machine's LAN URL).

UI teammate: replace `src/App.tsx` (and add views) with Figma/Base44 screens. Keep using `src/api.ts`:

- `startSession(products)` after the customer picks items and reasons
- Show `response.current.challenge.instruction`
- `submitRecording(sessionId, videoBlob)` after each take
- Switch on `response.action`: `retry_challenge` | `next_challenge` | `next_product` | `done`
- On `retry_challenge`, show the **same** instruction (`current.challenge.attempt` is 2)
- Banner `response.last.challenge` (`pass`/`fail`) after every take
- On `next_product` or `done`, also banner `response.last.product` for the item you just finished
- On `done`, show `terminal.payment.status`: `full` | `partial` | `none`

The smoke page's Demo pass / Demo fail buttons call `submitRecording` with `demo_result` so the backend can be walked without a camera or OpenAI.
