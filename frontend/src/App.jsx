import { Toaster } from "@/components/ui/toaster"
import { QueryClientProvider } from '@tanstack/react-query'
import { queryClientInstance } from '@/lib/query-client'
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import PageNotFound from './lib/PageNotFound';
import ScrollToTop from './components/ScrollToTop';
import ProductSelectionPage from '@/pages/ProductSelectionPage';
import IssueDescriptionPage from '@/pages/IssueDescriptionPage';
import VerificationIntroPage from '@/pages/VerificationIntroPage';
import LiveVerificationPage from '@/pages/LiveVerificationPage';
import ProcessingPage from '@/pages/ProcessingPage';
import ResultPage from '@/pages/ResultPage';
import { RefundSessionProvider } from '@/state/RefundSessionContext';

const AuthenticatedApp = () => {
  return (
    <RefundSessionProvider>
      <Routes>
        <Route path="/" element={<ProductSelectionPage />} />
        <Route path="/describe" element={<IssueDescriptionPage />} />
        <Route path="/prepare" element={<VerificationIntroPage />} />
        <Route path="/verify" element={<LiveVerificationPage />} />
        <Route path="/processing" element={<ProcessingPage />} />
        <Route path="/result" element={<ResultPage />} />
        <Route path="*" element={<PageNotFound />} />
      </Routes>
    </RefundSessionProvider>
  );
};


function App() {

  return (
    <QueryClientProvider client={queryClientInstance}>
      <Router>
        <ScrollToTop />
        <AuthenticatedApp />
      </Router>
      <Toaster />
    </QueryClientProvider>
  )
}

export default App