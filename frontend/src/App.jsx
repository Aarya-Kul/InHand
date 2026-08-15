import { Toaster } from "@/components/ui/toaster";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClientInstance } from "@/lib/query-client";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import PageNotFound from "./lib/PageNotFound";
import { AuthProvider, useAuth } from "@/lib/AuthContext";
import UserNotRegisteredError from "@/components/UserNotRegisteredError";
import ScrollToTop from "./components/ScrollToTop";
import ProductSelectionPage from "@/pages/ProductSelectionPage";
import IssueDescriptionPage from "@/pages/IssueDescriptionPage";
import VerificationIntroPage from "@/pages/VerificationIntroPage";
import LiveVerificationPage from "@/pages/LiveVerificationPage";
import ProcessingPage from "@/pages/ProcessingPage";
import StripeConnectionPage from "@/pages/StripeConnectionPage";
import ResultPage from "@/pages/ResultPage";
import { RefundSessionProvider } from "@/state/RefundSessionContext";

const AuthenticatedApp = () => {
  const { isLoadingAuth, isLoadingPublicSettings, authError, navigateToLogin } =
    useAuth();

  // Show loading spinner while checking app public settings or auth
  if (isLoadingPublicSettings || isLoadingAuth) {
    return (
      <div className="fixed inset-0 flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-slate-200 border-t-slate-800 rounded-full animate-spin"></div>
      </div>
    );
  }

  // Handle authentication errors
  if (authError) {
    if (authError.type === "user_not_registered") {
      return <UserNotRegisteredError />;
    } else if (authError.type === "auth_required") {
      // Redirect to login automatically
      navigateToLogin();
      return null;
    }
  }

  // Render the main app
  return (
    <RefundSessionProvider>
      <Routes>
        <Route path="/" element={<ProductSelectionPage />} />
        <Route path="/describe" element={<IssueDescriptionPage />} />
        <Route path="/prepare" element={<VerificationIntroPage />} />
        <Route path="/verify" element={<LiveVerificationPage />} />
        <Route path="/processing" element={<ProcessingPage />} />
        <Route path="/stripe-connection" element={<StripeConnectionPage />} />
        <Route path="/result" element={<ResultPage />} />
        <Route path="*" element={<PageNotFound />} />
      </Routes>
    </RefundSessionProvider>
  );
};

function App() {
  return (
    <AuthProvider>
      <QueryClientProvider client={queryClientInstance}>
        <Router>
          <ScrollToTop />
          <AuthenticatedApp />
        </Router>
        <Toaster />
      </QueryClientProvider>
    </AuthProvider>
  );
}

export default App;
