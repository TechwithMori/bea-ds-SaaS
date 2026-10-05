import { useState, type FormEvent } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { errorMessage } from "../api/client";
import { useAuth } from "../auth/AuthContext";

export default function RegisterPage() {
  const { register, user, preview, ready } = useAuth();
  const navigate = useNavigate();
  const [company, setCompany] = useState("");
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
      await register(email, password, company);
      navigate("/finance");
    } catch (caught) {
      setError(errorMessage(caught));
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center px-6 py-16">
      <form onSubmit={submit} className="mx-auto w-full max-w-md">
        <p className="font-display text-4xl italic">Bea</p>
        <h1 className="mt-4 font-display text-4xl">Open a merchant account</h1>
        <p className="mt-3 text-sm leading-6 text-ink-soft">Password needs at least 10 characters. You will name the store on the next step.</p>
        <label className="mt-8 block text-sm">
          Company
          <input className="mt-2 w-full rounded-2xl border border-line bg-cream px-4 py-3" value={company} onChange={(event) => setCompany(event.target.value)} />
        </label>
        <label className="mt-4 block text-sm">
          Email
          <input className="mt-2 w-full rounded-2xl border border-line bg-cream px-4 py-3" type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
        </label>
        <label className="mt-4 block text-sm">
          Password
          <input className="mt-2 w-full rounded-2xl border border-line bg-cream px-4 py-3" type="password" minLength={10} value={password} onChange={(event) => setPassword(event.target.value)} required />
        </label>
        {error ? <p className="mt-3 text-sm text-[#8d3d32]">{error}</p> : null}
        <button className="mt-6 w-full rounded-full bg-ink py-3 text-sm text-cream" disabled={pending} type="submit">
          {pending ? "Creating…" : "Create account"}
        </button>
        <p className="mt-6 text-sm text-ink-soft">
          Already operating? <Link className="text-ink underline" to="/login">Sign in</Link>
        </p>
      </form>
    </div>
  );
}
