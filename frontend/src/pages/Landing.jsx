import { Link } from "react-router-dom";
import { Sparkles, Coins, LineChart, FileBadge, ArrowRight, CheckCircle2 } from "lucide-react";

function Landing() {
  return (
    <div className="min-h-screen bg-white text-gray-900">
      {/* Nav */}
      <div className="flex items-center justify-between px-10 py-5 border-b border-gray-100 sticky top-0 bg-white/80 backdrop-blur z-10">
        <div className="flex items-center gap-2">
          <div className="w-9 h-9 bg-gradient-to-br from-purple-600 to-indigo-600 rounded-xl flex items-center justify-center shadow-sm shadow-purple-200">
            <Sparkles size={18} className="text-white" />
          </div>
          <span className="text-lg font-semibold">InnovaFund AI</span>
        </div>
        <div className="hidden md:flex items-center gap-8 text-sm font-medium text-gray-600">
          <span className="hover:text-gray-900 cursor-pointer">Platform</span>
          <span className="hover:text-gray-900 cursor-pointer">Intelligence</span>
          <span className="hover:text-gray-900 cursor-pointer">Research</span>
        </div>
        <div className="flex items-center gap-3">
          <Link to="/login" className="text-sm font-medium text-gray-700 hover:text-gray-900">
            Sign In
          </Link>
          <Link
            to="/register"
            className="text-sm bg-purple-600 hover:bg-purple-700 text-white px-5 py-2.5 rounded-lg font-medium"
          >
            Get Started
          </Link>
        </div>
      </div>

      {/* Hero */}
      <div className="max-w-7xl mx-auto grid grid-cols-2 gap-12 items-center px-10 pt-20 pb-24">
        <div>
          <span className="inline-flex items-center gap-2 text-xs font-medium text-purple-700 bg-purple-50 px-3 py-1.5 rounded-full mb-6">
            <Sparkles size={12} /> Next-Gen AI for R&D Leaders
          </span>
          <h1 className="text-5xl font-bold leading-tight mb-6">
            Accelerate Research & <span className="text-purple-600">Innovation</span> with AI-Powered Intelligence
          </h1>
          <p className="text-gray-500 text-lg mb-8">
            Unlock deep discovery insights, automate funding searches, and analyze
            patent landscapes in seconds. The single source of truth for research intelligence.
          </p>
          <div className="flex items-center gap-3 mb-8">
            <Link
              to="/register"
              className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg font-medium text-sm flex items-center gap-2"
            >
              Get Started <ArrowRight size={16} />
            </Link>
            <Link
              to="/login"
              className="border border-gray-200 hover:border-gray-300 text-gray-800 px-6 py-3 rounded-lg font-medium text-sm"
            >
              Explore Platform
            </Link>
          </div>
          <div className="flex items-center gap-6 text-sm text-gray-500">
            <span className="flex items-center gap-1.5"><CheckCircle2 size={15} className="text-green-500" /> Free to start</span>
            <span className="flex items-center gap-1.5"><CheckCircle2 size={15} className="text-green-500" /> No credit card</span>
          </div>
        </div>

        {/* Hero visual */}
        <div className="relative">
          <div className="bg-gradient-to-br from-purple-100 via-indigo-50 to-fuchsia-50 rounded-3xl h-[420px] p-8 flex flex-col justify-center gap-4">
            <div className="bg-white rounded-xl shadow-md shadow-purple-100 p-4 flex items-center gap-3 w-64">
              <div className="w-9 h-9 bg-purple-100 rounded-lg flex items-center justify-center"><Coins size={18} className="text-purple-600" /></div>
              <div>
                <p className="text-xs text-gray-400">Funding matches</p>
                <p className="font-semibold">94% match found</p>
              </div>
            </div>
            <div className="bg-white rounded-xl shadow-md shadow-purple-100 p-4 flex items-center gap-3 w-72 ml-12">
              <div className="w-9 h-9 bg-indigo-100 rounded-lg flex items-center justify-center"><LineChart size={18} className="text-indigo-600" /></div>
              <div>
                <p className="text-xs text-gray-400">Research trend</p>
                <p className="font-semibold">+42% this quarter</p>
              </div>
            </div>
            <div className="bg-white rounded-xl shadow-md shadow-purple-100 p-4 flex items-center gap-3 w-64 ml-4">
              <div className="w-9 h-9 bg-fuchsia-100 rounded-lg flex items-center justify-center"><FileBadge size={18} className="text-fuchsia-600" /></div>
              <div>
                <p className="text-xs text-gray-400">Patent landscape</p>
                <p className="font-semibold">340 records mapped</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Feature cards */}
      <div className="max-w-6xl mx-auto grid grid-cols-3 gap-6 px-10 pb-24">
        <FeatureCard icon={<Coins size={22} className="text-purple-600" />} title="Funding discovery" desc="Get matched to grants and funding opportunities you're eligible for." />
        <FeatureCard icon={<LineChart size={22} className="text-purple-600" />} title="Research trends" desc="Track emerging topics and momentum in your field automatically." />
        <FeatureCard icon={<FileBadge size={22} className="text-purple-600" />} title="Patent intelligence" desc="Understand the patent landscape and spot commercialization gaps." />
      </div>
      {/* Social proof */}
<div className="border-t border-gray-100 py-16">
  <div className="max-w-6xl mx-auto px-10 text-center">
    <p className="text-sm text-gray-400 mb-8">Trusted by researchers and innovation teams</p>
    <div className="grid grid-cols-4 gap-8">
      <StatBlock value="1,204+" label="Funding sources tracked" />
      <StatBlock value="24.5K+" label="Publications analyzed" />
      <StatBlock value="15.8K+" label="Patent records mapped" />
      <StatBlock value="98.4%" label="System accuracy" />
    </div>
  </div>
</div>

{/* How it works */}
<div className="max-w-6xl mx-auto px-10 py-20">
  <h2 className="text-3xl font-bold text-center mb-3">How it works</h2>
  <p className="text-gray-500 text-center mb-12">From sign-up to insight in three simple steps</p>
  <div className="grid grid-cols-3 gap-8">
    <StepCard number="1" title="Create your profile" desc="Tell us your research interests, organization, and role." />
    <StepCard number="2" title="AI analyzes your field" desc="We match you to funding, trends, and patents relevant to you." />
    <StepCard number="3" title="Act on insights" desc="Apply for funding, track trends, and export reports instantly." />
  </div>
</div>

{/* CTA banner */}
<div className="bg-gradient-to-br from-purple-600 to-indigo-600 py-16">
  <div className="max-w-3xl mx-auto text-center px-6">
    <h2 className="text-3xl font-bold text-white mb-3">Ready to accelerate your research?</h2>
    <p className="text-purple-100 mb-8">Join researchers and innovators using InnovaFund AI today.</p>
    <Link
      to="/register"
      className="inline-flex items-center gap-2 bg-white text-purple-700 px-6 py-3 rounded-lg font-medium text-sm hover:bg-purple-50"
    >
      Get Started Free <ArrowRight size={16} />
    </Link>
  </div>
</div>
    </div>
  );
}

function FeatureCard({ icon, title, desc }) {
  return (
    <div className="bg-white border border-gray-100 shadow-sm rounded-xl p-6 hover:shadow-md hover:border-purple-100 transition">
      <div className="w-11 h-11 bg-purple-50 rounded-lg flex items-center justify-center mb-4">{icon}</div>
      <h3 className="font-semibold mb-2">{title}</h3>
      <p className="text-sm text-gray-500">{desc}</p>
    </div>
  );
}
function StatBlock({ value, label }) {
  return (
    <div>
      <p className="text-3xl font-bold text-purple-600">{value}</p>
      <p className="text-sm text-gray-500 mt-1">{label}</p>
    </div>
  );
}

function StepCard({ number, title, desc }) {
  return (
    <div className="text-center">
      <div className="w-10 h-10 rounded-full bg-purple-600 text-white font-semibold flex items-center justify-center mx-auto mb-4">
        {number}
      </div>
      <h3 className="font-semibold mb-2">{title}</h3>
      <p className="text-sm text-gray-500">{desc}</p>
    </div>
  );
}

export default Landing;