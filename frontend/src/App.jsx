import { useState } from "react";
import ChatTab from "./tabs/ChatTab";
import UploadTab from "./tabs/UploadTab";

const TABS = ["Retrieve", "Upload"];

export default function App() {
  const [activeTab, setActiveTab] = useState("Retrieve");

  return (
    <div className="app">
      <header className="app-header">
        <span className="app-logo">ClinIQ</span>
        <nav className="tab-nav">
          {TABS.map((tab) => (
            <button
              key={tab}
              className={`tab-btn ${activeTab === tab ? "active" : ""}`}
              onClick={() => setActiveTab(tab)}
            >
              {tab}
            </button>
          ))}
        </nav>
      </header>

      <main className="app-main">
        {activeTab === "Retrieve" && <ChatTab />}
        {activeTab === "Upload"   && <UploadTab />}
      </main>
    </div>
  );
}
