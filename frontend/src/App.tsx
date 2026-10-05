import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./auth/AuthContext";
import AppShell from "./components/AppShell";
import CatalogPage from "./pages/CatalogPage";
import CustomersPage from "./pages/CustomersPage";
import FinancePage from "./pages/FinancePage";
import FulfillmentPage from "./pages/FulfillmentPage";
import LoginPage from "./pages/LoginPage";
import MarketingPage from "./pages/MarketingPage";
import RegisterPage from "./pages/RegisterPage";
import StorefrontPage from "./pages/StorefrontPage";

function Gate() {
  const { ready, user, preview } = useAuth();
  if (!ready) return <p className="p-8 text-sm text-ink-soft">Opening the desks…</p>;
  if (!user && !preview) return <Navigate to="/login" replace />;
  return <AppShell />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route element={<Gate />}>
        <Route index element={<Navigate to="/finance" replace />} />
        <Route path="/finance" element={<FinancePage />} />
        <Route path="/catalog" element={<CatalogPage />} />
        <Route path="/marketing" element={<MarketingPage />} />
        <Route path="/storefront" element={<StorefrontPage />} />
        <Route path="/fulfillment" element={<FulfillmentPage />} />
        <Route path="/customers" element={<CustomersPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/finance" replace />} />
    </Routes>
  );
}
