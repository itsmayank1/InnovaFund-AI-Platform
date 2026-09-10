import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
import {
  BarChart3, LayoutDashboard, UserCircle, FlaskConical, Coins,
  FileBadge, Settings, HelpCircle, LogOut, Search, Bell, FileText, TrendingUp,
} from "lucide-react";
import { useEffect, useState } from "react";
import { getMyProfile } from "../services/profileService";

const [profileCompletion, setProfileCompletion] = useState(0);

useEffect(() => {
  getMyProfile()
    .then((data) => {
      const fields = [
        data.research_domains, data.keywords, data.bio,
        data.publications, data.patents, data.technology_areas,
      ];
      const filled = fields.filter((f) => f && f.trim() !== "").length;
      setProfileCompletion(Math.round((filled / fields.length) * 100));
    })
    .catch(() => setProfileCompletion(0));
}, []);
const roleLabels = {
  researcher: "Researcher",
  startup_founder: "Startup Founder",
  innovation_manager: "Innovation Manager",
  administrator: "Administrator",
};

const roleContent = {
  researcher: {
    heading: "Researcher Dashboard",
    stats: [
      { label: "Innovation Score", value: "78/100", icon: <TrendingUp size={16} className="text-green-500" /> },
      { label: "Funding Matches", value: "12", icon: <Coins size={16} className="text-blue-500" /> },
      { label: "Publications", value: "24", icon: <FileText size={16} className="text-indigo-500" /> },
{ label: "Profile Completion", value: "65%", icon: <UserCircle size={16} className="text-gray-400" /> },    ],
    funding: [
      { name: "National Battery Research Grant", type: "Government grant", closesIn: "18 days", match: 94 },
      { name: "Clean Energy Innovation Fund", type: "Innovation fund", closesIn: "32 days", match: 81 },
      { name: "AI for Science Fellowship", type: "Research council", closesIn: "45 days", match: 73 },
    ],
  },
  startup_founder: {
    heading: "Startup Dashboard",
    stats: [
      { label: "Funding Opportunities", value: "8", icon: <Coins size={16} className="text-blue-500" /> },
      { label: "Tech Opportunities", value: "15", icon: <TrendingUp size={16} className="text-green-500" /> },
      { label: "Patent Intelligence", value: "340", icon: <FileText size={16} className="text-indigo-500" /> },
      { label: "Commercialization Score", value: "82%", icon: <UserCircle size={16} className="text-gray-400" /> },
    ],
    funding: [
      { name: "Startup Accelerator Fund", type: "Venture program", closesIn: "10 days", match: 88 },
      { name: "Seed Innovation Grant", type: "Government grant", closesIn: "25 days", match: 76 },
    ],
  },
  innovation_manager: {
    heading: "Innovation Manager Dashboard",
    stats: [
      { label: "Portfolio Projects", value: "34", icon: <TrendingUp size={16} className="text-green-500" /> },
      { label: "Funding Analytics", value: "$2.4M", icon: <Coins size={16} className="text-blue-500" /> },
      { label: "Patents Tracked", value: "340", icon: <FileText size={16} className="text-indigo-500" /> },
      { label: "Team Members", value: "12", icon: <UserCircle size={16} className="text-gray-400" /> },
    ],
    funding: [
      { name: "Portfolio-wide Innovation Fund", type: "Internal", closesIn: "N/A", match: 100 },
    ],
  },
  administrator: {
    heading: "Admin Dashboard",
    stats: [
      { label: "Total Users", value: "156", icon: <UserCircle size={16} className="text-gray-400" /> },
      { label: "Platform Activity", value: "98.4%", icon: <TrendingUp size={16} className="text-green-500" /> },
      { label: "Funding Records", value: "1,204", icon: <Coins size={16} className="text-blue-500" /> },
      { label: "System Reports", value: "42", icon: <FileText size={16} className="text-indigo-500" /> },
    ],
    funding: [],
  },
};

const DUMMY_TREND = [30, 45, 55, 80, 100];

function Dashboard() {
  const { logout, role } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const current = roleContent[role] || roleContent.researcher;

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <div className="w-60 bg-white border-r border-gray-100 flex flex-col justify-between">
        <div>
          <div className="flex items-center gap-2 px-5 py-5">
            <div className="w-8 h-8 bg-purple-600 rounded-lg flex items-center justify-center">
              <BarChart3 size={18} className="text-white" />
            </div>
            <div>
              <p className="font-semibold text-sm leading-tight">InnovaFund AI</p>
              <p className="text-xs text-gray-400 leading-tight">Enterprise Intelligence</p>
            </div>
          </div>
          <div className="px-3 space-y-1">
            <NavItem icon={<LayoutDashboard size={16} />} label="Dashboard" active />
<NavItem icon={<UserCircle size={16} />} label="Research Profile" onClick={() => navigate("/profile")} />            <NavItem icon={<FlaskConical size={16} />} label="Research" />
            <NavItem icon={<Coins size={16} />} label="Funding" />
            <NavItem icon={<FileBadge size={16} />} label="Patent Intelligence" />
          </div>
          <p className="text-xs font-medium text-gray-400 px-5 mt-6 mb-1">SYSTEM</p>
          <div className="px-3 space-y-1">
            <NavItem icon={<Settings size={16} />} label="Settings" />
            <NavItem icon={<HelpCircle size={16} />} label="Help" />
          </div>
        </div>
        <div className="px-3 pb-4">
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-gray-500 hover:bg-gray-50"
          >
            <LogOut size={16} /> Logout
          </button>
        </div>
      </div>

      {/* Main */}
      <div className="flex-1">
        {/* Top bar */}
        <div className="flex items-center justify-between px-8 py-4 border-b border-gray-100 bg-white">
          <div className="relative w-96">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              placeholder="Search funding, patents, or research..."
              className="w-full pl-9 pr-3 py-2 rounded-lg bg-gray-50 border border-gray-100 text-sm focus:outline-none"
            />
          </div>
          <div className="flex items-center gap-4">
            <Bell size={18} className="text-gray-400" />
            <div className="w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center text-white text-sm font-medium">
              K
            </div>
          </div>
        </div>

        <div className="p-8">
          <p className="text-sm font-medium text-purple-600 mb-1">{roleLabels[role] || "Dashboard"}</p>
          <h1 className="text-3xl font-bold mb-2">{current.heading}</h1>
          <p className="text-gray-500 mb-8">You're logged in to InnovaFund AI.</p>

          {/* Stat cards */}
          <div className="grid grid-cols-4 gap-4 mb-8">
  {current.stats.map((s, i) => (
    <StatCard
      key={i}
      label={s.label}
      value={s.label === "Profile Completion" ? `${profileCompletion}%` : s.value}
      icon={s.icon}
    />
  ))}
</div>

          <div className="grid grid-cols-2 gap-6">
            {/* Funding matches */}
            <div className="bg-white border border-gray-100 rounded-xl p-5">
              <p className="font-semibold mb-4">Top Funding Matches</p>
              {current.funding.length === 0 ? (
                <p className="text-sm text-gray-400">No funding data yet.</p>
              ) : (
                <div className="space-y-3">
                  {current.funding.map((item, i) => (
                    <div key={i} className="flex items-center justify-between border border-gray-100 rounded-lg px-4 py-3">
                      <div>
                        <p className="text-sm font-medium">{item.name}</p>
                        <p className="text-xs text-gray-400">{item.type} · Closes in {item.closesIn}</p>
                      </div>
                      <span className="text-xs font-medium bg-purple-50 text-purple-700 px-2.5 py-1 rounded-full">
                        {item.match}% match
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Trend chart */}
            <div className="bg-white border border-gray-100 rounded-xl p-5">
              <p className="font-semibold mb-4">Research Trend</p>
              <div className="flex items-end gap-2 h-32">
                {DUMMY_TREND.map((height, i) => (
                  <div key={i} className="flex-1 bg-purple-100 rounded" style={{ height: `${height}%` }}>
                    <div className="w-full h-full bg-purple-500 rounded opacity-80" />
                  </div>
                ))}
              </div>
              <p className="text-xs text-gray-400 mt-3">Publication activity, last 5 quarters</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function NavItem({ icon, label, active, onClick }) {
  return (
    <div
      onClick={onClick}
      className={`flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm cursor-pointer ${
        active ? "bg-purple-50 text-purple-700 font-medium" : "text-gray-600 hover:bg-gray-50"
      }`}
    >
      {icon} {label}
    </div>
  );
}

function StatCard({ label, value, icon }) {
  return (
    <div className="bg-white border border-gray-100 rounded-xl p-5">
      <div className="w-9 h-9 bg-gray-50 rounded-lg flex items-center justify-center mb-3">{icon}</div>
      <p className="text-sm text-gray-500 mb-1">{label}</p>
      <p className="text-2xl font-bold">{value}</p>
    </div>
  );
}

export default Dashboard;