import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { lazy, Suspense, type ReactNode } from "react";
import { BrowserRouter, Link, Navigate, Route, Routes } from "react-router-dom";
import { shouldRetry } from "./api/hooks";
import { AuthProvider, useAuth } from "./auth/AuthProvider";
import { RequireAdmin, RequireAuth } from "./auth/guards";
import { AdminLayout } from "./components/AdminLayout";
import { Loading } from "./components/DataState";
import { ErrorBoundary } from "./components/ErrorBoundary";
import { ToastProvider } from "./components/Toast";
import { SubmitComplaintPage } from "./pages/customer/SubmitComplaintPage";
import { LoginPage } from "./pages/LoginPage";

// Admin pages (and the charts library) load on demand, keeping the
// customer portal's first load small.
const OverviewPage = lazy(() => import("./pages/admin/OverviewPage").then((m) => ({ default: m.OverviewPage })));
const CasesPage = lazy(() => import("./pages/admin/CasesPage").then((m) => ({ default: m.CasesPage })));
const CaseDetailPage = lazy(() => import("./pages/admin/CaseDetailPage").then((m) => ({ default: m.CaseDetailPage })));
const IncidentsPage = lazy(() => import("./pages/admin/IncidentsPage").then((m) => ({ default: m.IncidentsPage })));
const SentimentPage = lazy(() => import("./pages/admin/SentimentPage").then((m) => ({ default: m.SentimentPage })));
const TopicsPage = lazy(() => import("./pages/admin/TopicsPage").then((m) => ({ default: m.TopicsPage })));
const ReviewQueuePage = lazy(() => import("./pages/admin/ReviewQueuePage").then((m) => ({ default: m.ReviewQueuePage })));
const AssistantPage = lazy(() => import("./pages/admin/AssistantPage").then((m) => ({ default: m.AssistantPage })));

const page = (el: ReactNode) => <Suspense fallback={<Loading label="Loading page…" />}>{el}</Suspense>;

export function makeQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: shouldRetry,
        retryDelay: (attempt) => Math.min(1000 * 2 ** attempt, 8000),
        refetchOnWindowFocus: false,
      },
      mutations: { retry: false },
    },
  });
}

function HomeRedirect() {
  const { user, loading, canUseAdmin } = useAuth();
  if (loading) return <Loading label="Checking your session…" fullPage />;
  if (!user) return <Navigate to="/login" replace />;
  return <Navigate to={canUseAdmin ? "/admin" : "/submit"} replace />;
}

function NotFound() {
  return (
    <div className="center-page">
      <div className="card auth-card stack">
        <h2>Page not found</h2>
        <Link className="btn" to="/">
          Go home
        </Link>
      </div>
    </div>
  );
}

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<HomeRedirect />} />
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/submit"
        element={
          <RequireAuth>
            <SubmitComplaintPage />
          </RequireAuth>
        }
      />
      <Route
        path="/admin"
        element={
          <RequireAdmin>
            <AdminLayout />
          </RequireAdmin>
        }
      >
        <Route index element={page(<OverviewPage />)} />
        <Route path="cases" element={page(<CasesPage />)} />
        <Route path="cases/:caseId" element={page(<CaseDetailPage />)} />
        <Route path="incidents" element={page(<IncidentsPage />)} />
        <Route path="sentiment" element={page(<SentimentPage />)} />
        <Route path="topics" element={page(<TopicsPage />)} />
        <Route path="review" element={page(<ReviewQueuePage />)} />
        <Route path="assistant" element={page(<AssistantPage />)} />
      </Route>
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}

const queryClient = makeQueryClient();

export default function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <ToastProvider>
            <BrowserRouter>
              <AppRoutes />
            </BrowserRouter>
          </ToastProvider>
        </AuthProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}
