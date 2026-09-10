import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { loginUser, googleLogin } from "../services/authService";
import { useAuth } from "../context/AuthContext";
import { Sparkles, Mail, Lock, Coins, LineChart, FileBadge, Eye, EyeOff, ShieldCheck } from "lucide-react";
import { GoogleLogin } from "@react-oauth/google";

function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [remember, setRemember] = useState(false);
  const [error, setError] = useState("");
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const data = await loginUser({ email, password });
      login(data.access_token);
      navigate("/dashboard");
    } catch (err) {
      setError("Invalid email or password");
    }
  };

  return (
    <div className="min-h-screen grid grid-cols-2 bg-white">
      {/* Left panel */}
      <div className="hidden md:flex relative flex-col justify-between bg-gradient-to-br from-purple-700 via-purple-600 to-indigo-700 p-12 overflow-hidden text-white">
        <div className="absolute -top-24 -right-24 w-80 h-80 rounded-full bg-white/10 blur-3xl" />
        <div className="absolute -bottom-24 -left-24 w-80 h-80 rounded-full bg-fuchsia-400/20 blur-3xl" />

        <div className="relative z-10 flex items-center gap-2">
          <div className="w-9 h-9 bg-white/15 rounded-xl flex items-center justify-center backdrop-blur">
            <Sparkles size={18} className="text-white" />
          </div>
          <span className="font-semibold text-lg">InnovaFund AI</span>
        </div>

        <div className="relative z-10">
          <h2 className="text-3xl font-bold leading-tight mb-4">
            Empowering Research<br />Through AI
          </h2>
          <p className="text-purple-100 text-sm mb-10 max-w-xs">
            Discover funding, track research trends, and analyze patent landscapes — all in one place.
          </p>

          <div className="space-y-3">
            <PanelStat icon={<Coins size={16} />} label="Funding matches" value="12 active" />
            <PanelStat icon={<LineChart size={16} />} label="Research trends" value="+42% growth" />
            <PanelStat icon={<FileBadge size={16} />} label="Patent records" value="340 mapped" />
          </div>
        </div>

        <div className="relative z-10 flex items-center gap-2 text-purple-200 text-xs">
          <ShieldCheck size={14} /> Secured with enterprise-grade encryption
        </div>
      </div>

      {/* Right form panel */}
      <div className="flex items-center justify-center px-8">
        <div className="w-full max-w-sm">
          <div className="flex items-center gap-2 mb-8">
            <div className="w-9 h-9 bg-gradient-to-br from-purple-600 to-indigo-600 rounded-xl flex items-center justify-center shadow-sm shadow-purple-200">
              <Sparkles size={18} className="text-white" />
            </div>
            <span className="font-semibold text-lg text-gray-900">InnovaFund AI</span>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-1">Welcome Back</h2>
          <p className="text-sm text-gray-500 mb-6">Sign in to access your personalized dashboard.</p>

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
              width="380"
            />
          </div>

          <div className="flex items-center gap-3 mb-4">
            <div className="flex-1 h-px bg-gray-200" />
            <span className="text-xs text-gray-400">or</span>
            <div className="flex-1 h-px bg-gray-200" />
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-700">Email Address</label>
              <div className="relative mt-1">
                <Mail size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input
                  type="email"
                  placeholder="name@company.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-9 pr-3 py-2.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:border-purple-400 focus:ring-1 focus:ring-purple-400"
                  required
                />
              </div>
            </div>
            <div>
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium text-gray-700">Password</label>
                <span className="text-xs text-purple-600 hover:underline cursor-pointer">Forgot password?</span>
              </div>
              <div className="relative mt-1">
                <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input
                  type={showPassword ? "text" : "password"}
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-9 pr-9 py-2.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:border-purple-400 focus:ring-1 focus:ring-purple-400"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400"
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <label className="flex items-center gap-2 text-sm text-gray-600">
              <input
                type="checkbox"
                checked={remember}
                onChange={(e) => setRemember(e.target.checked)}
                className="accent-purple-600"
              />
              Remember me
            </label>

            {error && <p className="text-red-500 text-sm">{error}</p>}
            <button
              type="submit"
              className="w-full py-2.5 rounded-lg bg-purple-600 hover:bg-purple-700 text-white text-sm font-medium"
            >
              Sign In →
            </button>
          </form>

          <p className="text-sm text-gray-500 text-center mt-6">
            No account?{" "}
            <Link to="/register" className="text-purple-600 hover:underline font-medium">
              Register
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

function PanelStat({ icon, label, value }) {
  return (
    <div className="flex items-center gap-3 bg-white/10 backdrop-blur rounded-lg px-4 py-3">
      <div className="w-8 h-8 bg-white/15 rounded-lg flex items-center justify-center">{icon}</div>
      <div>
        <p className="text-[11px] text-purple-200">{label}</p>
        <p className="text-sm font-semibold">{value}</p>
      </div>
    </div>
  );
}

export default Login;