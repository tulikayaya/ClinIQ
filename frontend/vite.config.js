import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/chat":     "http://localhost:8000",
      "/retrieve": "http://localhost:8000",
      "/convert":  "http://localhost:8000",
      "/segment":  "http://localhost:8000",
      "/features": "http://localhost:8000",
      "/images":   "http://localhost:8000",
      "/upload":   "http://localhost:8000",
    },
  },
});
