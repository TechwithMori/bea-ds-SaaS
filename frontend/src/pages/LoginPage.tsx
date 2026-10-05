import { useState, type FormEvent } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { errorMessage } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import { LanguageSwitch, useI18n } from "../i18n/LanguageContext";

export default function LoginPage() {
  const { login, enterPreview, user, preview, ready } = useAuth();
  const { t } = useI18n();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [pending, setPending] = useState(false);

  if (ready && (user || preview)) return <Navigate to="/finance" replace />;

  async function submit(event: FormEvent) {
    event.preventDefault();
    setPending(true);
    setError("");
    try {
      await login(email, password);
      navigate("/finance");
    } catch (caught) {
      setError(errorMessage(caught));
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="grid min-h-screen lg:grid-cols-[1.1fr_0.9fr]">
      <section className="hidden bg-espresso px-12 py-16 text-cream lg:flex lg:flex-col lg:justify-between">
        <p className="font-display text-4xl italic">Bea</p>
        <div>
          <h1 className="max-w-md font-display text-5xl leading-tight">{t("loginHeadline")}</h1>
          <p className="mt-6 max-w-md text-base leading-7 text-cream/75">{t("loginLede")}</p>
        </div>
        <p className="text-sm text-blush">{t("loginFoot")}</p>
      </section>
      <section className="flex items-center px-6 py-16">
        <form onSubmit={submit} className="mx-auto w-full max-w-md">
          <div className="flex items-center justify-between">
            <p className="font-display text-4xl italic lg:hidden">Bea</p>
            <LanguageSwitch />
          </div>
          <h2 className="mt-4 font-display text-4xl">{t("signIn")}</h2>
          <label className="mt-8 block text-sm">
            {t("email")}
            <input className="mt-2 w-full rounded-2xl border border-line bg-cream px-4 py-3" type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
          </label>
          <label className="mt-4 block text-sm">
            {t("password")}
            <input className="mt-2 w-full rounded-2xl border border-line bg-cream px-4 py-3" type="password" value={password} onChange={(event) => setPassword(event.target.value)} required />
          </label>
          {error ? <p className="mt-3 text-sm text-[#8d3d32]">{error}</p> : null}
          <button className="mt-6 w-full rounded-full bg-ink py-3 text-sm text-cream" disabled={pending} type="submit">
            {pending ? t("signingIn") : t("enterDesks")}
          </button>
          <button
            className="mt-3 w-full rounded-full border border-line py-3 text-sm"
            type="button"
            onClick={() => {
              enterPreview();
              navigate("/finance");
            }}
          >
            {t("tour")}
          </button>
          <p className="mt-6 text-sm text-ink-soft">
            {t("newMerchant")} <Link className="text-ink underline" to="/register">{t("openAccount")}</Link>
          </p>
        </form>
      </section>
    </div>
  );
}
