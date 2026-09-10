import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import {
  Sparkles, FlaskConical, Coins, TrendingUp,
  User as UserIcon, Mail, Building2, Beaker, Lock,
  GraduationCap, Rocket, Briefcase, ShieldCheck,
} from "lucide-react";
import { GoogleLogin } from "@react-oauth/google";
import { registerUser, loginUser, googleLogin } from "../services/authService";

const ROLES = [
  { value: "researcher", label: "Researcher", desc: "Academic or independent research", icon: GraduationCap },
  { value: "startup_founder", label: "Startup Founder", desc: "Building a research-based venture", icon: Rocket },
  { value: "innovation_manager", label: "Innovation Manager", desc: "Managing a research portfolio", icon: Briefcase },
];

function Register() {
  const [form, setForm] = useState({
    full_name: "",
    email: "",
    password: "",
    confirmPassword: "",
    role: "researcher",
    organization: "",
    research_domain: "",
  });
  const [agreed, setAgreed] = useState(false);
  const [error, setError] = useState("");
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (form.password !== form.confirmPassword) {
      setError("Passwords do not match");
      return;
    }
    if (!agreed) {
      setError("Please agree to the Terms of Service and Privacy Policy");
      return;
    }

    try {
      const { confirmPassword, ...payload } = form;
      await registerUser(payload);
      const data = await loginUser({ email: form.email, password: form.password });
      login(data.access_token);
      navigate("/dashboard");
    } catch (err) {
      setError("Registration failed — email may already be in use");
    }
  };

  const inputClass =
    "w-full pl-9 pr-3 py-2.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:border-purple-400 focus:ring-1 focus:ring-purple-400";

  return (
    <div className="min-h-screen grid grid-cols-2 bg-white">
      {/* Left panel */}
      <div className="hidden md:flex relative flex-col justify-between bg-gradient-to-br from-purple-700 via-purple-600 to-indigo-700 p-12 overflow-hidden text-white">
        <div className="absolute -top-24 -right-24 w-80 h-80 rounded-full bg-white/10 blur-3xl" />
        <div className="absolute -bottom-24 -left-24 w-80 h-80 rounded-full bg-fuchsia-400/20 blur-3xl" />

        <div className="relative z-10 flex items-center gap-2">
          <div className="w-9 h-9 bg-white/15 rounded-xl flex items-center justify-center backdrop-blur">
            <FlaskConical size={18} className="text-white" />
          </div>
          <span className="font-semibold text-lg">InnovaFund AI</span>
        </div>

        <div className="relative z-10">
          <h2 className="text-3xl font-bold leading-tight mb-4">
            Powering the Next<br />Generation of Discovery
          </h2>
          <p className="text-purple-100 text-sm mb-10 max-w-xs">
            Transform your funding landscape with AI-driven research and patent intelligence.
          </p>

          <div className="flex gap-3">
            <MiniStat icon={<Coins size={16} />} value="1,204" label="Funding sources" />
            <MiniStat icon={<TrendingUp size={16} />} value="24.5K" label="Publications" />
          </div>
        </div>

        <div className="relative z-10 flex items-center gap-2 text-purple-200 text-xs">
          <ShieldCheck size={14} /> Secured with enterprise-grade encryption
        </div>
      </div>

      {/* Right form panel */}
      <div className="flex items-center justify-center px-8 py-10 overflow-y-auto">
        <div className="w-full max-w-md">
          <div className="flex items-center gap-2 mb-6">
            <div className="w-9 h-9 bg-gradient-to-br from-purple-600 to-indigo-600 rounded-xl flex items-center justify-center shadow-sm shadow-purple-200">
              <Sparkles size={18} className="text-white" />
            </div>
            <span className="font-semibold text-lg text-gray-900">InnovaFund AI</span>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-1">Create account</h2>
          <p className="text-sm text-gray-500 mb-5">Set up your research profile.</p>

          <div className="mb-4 flex justify-center">
            <GoogleLogin
              onSuccess={async (credentialResponse) => {
                try {
                  const data = await googleLogin(credentialResponse.credential);
                  login(data.access_token);
                  navigate("/dashboard");
                } catch (err) {
                  setError("Google sign-in failed");
                }
              }}
              onError={() => setError("Google sign-in failed")}
              width="400"
            />
          </div>

          <div className="flex items-center gap-3 mb-4">
            <div className="flex-1 h-px bg-gray-200" />
            <span className="text-xs text-gray-400">or</span>
            <div className="flex-1 h-px bg-gray-200" />
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-sm font-medium text-gray-700">Full Name</label>
                <div className="relative mt-1">
                  <UserIcon size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                  <input name="full_name" placeholder="John Doe" onChange={handleChange} className={inputClass} required />
                </div>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700">Email Address</label>
                <div className="relative mt-1">
                  <Mail size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                  <input name="email" type="email" placeholder="john@example.com" onChange={handleChange} className={inputClass} required />
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-sm font-medium text-gray-700">Organization / University</label>
                <div className="relative mt-1">
                  <Building2 size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                  <input name="organization" placeholder="Institution Name" onChange={handleChange} className={inputClass} />
                </div>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700">Research Domain</label>
                <div className="relative mt-1">
                  <Beaker size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                  <input name="research_domain" placeholder="e.g. AI Ethics" onChange={handleChange} className={inputClass} />
                </div>
              </div>
            </div>

            <div>
              <label className="text-sm font-medium text-gray-700 mb-2 block">Account Role</label>
              <div className="grid grid-cols-3 gap-2">
                {ROLES.map((r) => {
                  const Icon = r.icon;
                  const selected = form.role === r.value;
                  return (
                    <button
                      type="button"
                      key={r.value}
                      onClick={() => setForm({ ...form, role: r.value })}
                      className={`text-left p-3 rounded-lg border transition ${
                        selected
                          ? "border-purple-500 bg-purple-50 ring-1 ring-purple-400"
                          : "border-gray-200 hover:border-gray-300"
                      }`}
                    >
                      <Icon size={18} className={selected ? "text-purple-600" : "text-gray-400"} />
                      <p className="text-xs font-medium mt-1.5 text-gray-800">{r.label}</p>
                      <p className="text-[10px] text-gray-400 mt-0.5 leading-tight">{r.desc}</p>
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-sm font-medium text-gray-700">Password</label>
                <div className="relative mt-1">
                  <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                  <input name="password" type="password" placeholder="••••••••" onChange={handleChange} className={inputClass} required />
                </div>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700">Confirm Password</label>
                <div className="relative mt-1">
                  <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                  <input name="confirmPassword" type="password" placeholder="••••••••" onChange={handleChange} className={inputClass} required />
                </div>
              </div>
            </div>

            <label className="flex items-start gap-2 text-sm text-gray-600">
              <input
                type="checkbox"
                checked={agreed}
                onChange={(e) => setAgreed(e.target.checked)}
                className="mt-0.5 accent-purple-600"
              />
              <span>
                I agree to the <span className="text-purple-600 font-medium">Terms of Service</span> and{" "}
                <span className="text-purple-600 font-medium">Privacy Policy</span>.
              </span>
            </label>

            {error && <p className="text-red-500 text-sm">{error}</p>}

            <button type="submit" className="w-full py-2.5 rounded-lg bg-purple-600 hover:bg-purple-700 text-white text-sm font-medium">
              Create Account →
            </button>
          </form>

          <p className="text-sm text-gray-500 text-center mt-6">
            Already have an account?{" "}
            <Link to="/login" className="text-purple-600 hover:underline font-medium">
              Sign In
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

function MiniStat({ icon, value, label }) {
  return (
    <div className="bg-white/10 backdrop-blur rounded-xl p-3 flex flex-col items-center w-28">
      <div className="w-8 h-8 bg-white/15 rounded-lg flex items-center justify-center mb-1">{icon}</div>
      <p className="font-semibold text-sm">{value}</p>
      <p className="text-[11px] text-purple-200">{label}</p>
    </div>
  );
}

export default Register;