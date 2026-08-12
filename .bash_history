      createWindow();
    }
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});
EOF

cat > apps/desktop/electron/preload.ts <<'EOF'
import { contextBridge } from "electron";

const screenBridge = Object.freeze({
  version: "0.1.0-alpha.1",
  platform: process.platform,
  isElectron: true
});

contextBridge.exposeInMainWorld(
  "screenBridge",
  screenBridge
);
EOF

cat > apps/desktop/src/electron.d.ts <<'EOF'
export {};

declare global {
  interface Window {
    screenBridge: {
      version: string;
      platform: string;
      isElectron: boolean;
    };
  }
}
EOF

cat > apps/desktop/tsconfig.electron.json <<'EOF'
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "lib": ["ES2022"],
    "strict": true,
    "noEmitOnError": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "outDir": "dist-electron",
    "rootDir": "electron",
    "types": ["node", "electron"]
  },
  "include": [
    "electron/main.ts",
    "electron/preload.ts"
  ]
}
EOF

cat > apps/desktop/vite.config.ts <<'EOF'
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],

  server: {
    host: "127.0.0.1",
    port: 5173,
    strictPort: true
  },

  build: {
    outDir: "dist",
    emptyOutDir: true
  }
});
EOF

cat > apps/desktop/package.json <<'EOF'
{
  "name": "@screenbridge/desktop",
  "version": "0.1.0-alpha.1",
  "private": true,
  "type": "module",
  "main": "dist-electron/main.js",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "build:electron": "tsc -p tsconfig.electron.json",
    "build:all": "pnpm run typecheck && pnpm run typecheck:electron && pnpm run build && pnpm run build:electron",
    "typecheck": "tsc -p tsconfig.json --noEmit",
    "typecheck:electron": "tsc -p tsconfig.electron.json --noEmit",
    "electron": "electron .",
    "start": "pnpm run build:all && pnpm run electron"
  },
  "dependencies": {
    "electron": "^43.3.0",
    "react": "^19.2.8",
    "react-dom": "^19.2.8"
  },
  "devDependencies": {
    "@types/node": "^26.2.0",
    "@types/react": "^19.2.18",
    "@types/react-dom": "^19.2.4",
    "@vitejs/plugin-react": "^5.2.0",
    "typescript": "^5.9.3",
    "vite": "^7.3.6"
  }
}
EOF

pnpm install
pnpm --filter @screenbridge/desktop run typecheck
pnpm --filter @screenbridge/desktop run typecheck:electron
pnpm --filter @screenbridge/desktop run build
pnpm --filter @screenbridge/desktop run build:electron
git status --short --branch
git add apps/desktop pnpm-workspace.yaml pnpm-lock.yaml
git commit -m "feat: prepare desktop electron runtime"
git push origin main
cd ~/screenbridge
cat > apps/desktop/electron/main.ts <<'EOF'
import {
  app,
  BrowserWindow,
  desktopCapturer,
  ipcMain,
  session
} from "electron";
import { randomBytes } from "node:crypto";
import { fileURLToPath } from "node:url";
import path from "node:path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const isDev = !app.isPackaged;
const rendererUrl =
  process.env.SCREENBRIDGE_RENDERER_URL ?? "http://127.0.0.1:5173";

type SessionState =
  | "idle"
  | "waiting"
  | "sharing"
  | "ended";

interface ScreenSource {
  id: string;
  name: string;
  type: "screen" | "window";
  thumbnail: string;
}

interface ScreenBridgeSession {
  id: string;
  status: SessionState;
  createdAt: string;
  sourceId: string | null;
}

let mainWindow: BrowserWindow | null = null;
let activeSession: ScreenBridgeSession | null = null;

function createSessionId(): string {
  const value = randomBytes(6)
    .toString("base64url")
    .toUpperCase()
    .replace(/[^A-Z0-9]/g, "")
    .slice(0, 8);

  return `SB-${value.slice(0, 4)}-${value.slice(4, 8)}`;
}

function createSession(): ScreenBridgeSession {
  const nextSession: ScreenBridgeSession = {
    id: createSessionId(),
    status: "waiting",
    createdAt: new Date().toISOString(),
    sourceId: null
  };

  activeSession = nextSession;

  return nextSession;
}

function endSession(): ScreenBridgeSession | null {
  if (!activeSession) {
    return null;
  }

  activeSession = {
    ...activeSession,
    status: "ended"
  };

  const endedSession = activeSession;
  activeSession = null;

  return endedSession;
}

async function getScreenSources(): Promise<ScreenSource[]> {
  const sources = await desktopCapturer.getSources({
    types: ["screen", "window"],
    thumbnailSize: {
      width: 320,
      height: 180
    },
    fetchWindowIcons: true
  });

  return sources.map((source) => ({
    id: source.id,
    name: source.name,
    type: source.id.startsWith("screen:") ? "screen" : "window",
    thumbnail: source.thumbnail.toDataURL()
  }));
}

function registerIpcHandlers(): void {
  ipcMain.handle("screenbridge:get-sources", async () => {
    return getScreenSources();
  });

  ipcMain.handle("screenbridge:create-session", () => {
    return createSession();
  });

  ipcMain.handle("screenbridge:get-session", () => {
    return activeSession;
  });

  ipcMain.handle(
    "screenbridge:start-sharing",
    (_event, sourceId: string) => {
      if (!activeSession) {
        createSession();
      }

      activeSession = {
        ...activeSession!,
        status: "sharing",
        sourceId
      };

      return activeSession;
    }
  );

  ipcMain.handle("screenbridge:end-session", () => {
    return endSession();
  });
}

function createWindow(): void {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1100,
    minHeight: 700,
    show: false,
    title: "ScreenBridge",
    backgroundColor: "#020b1c",

    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true
    }
  });

  mainWindow.once("ready-to-show", () => {
    mainWindow?.show();
  });

  if (isDev) {
    void mainWindow.loadURL(rendererUrl);
    mainWindow.webContents.openDevTools({ mode: "detach" });
  } else {
    void mainWindow.loadFile(
      path.join(__dirname, "../dist/index.html")
    );
  }

  mainWindow.on("closed", () => {
    mainWindow = null;
  });
}

app.whenReady().then(() => {
  session.defaultSession.setDisplayMediaRequestHandler(
    async (_request, callback) => {
      try {
        const sources = await desktopCapturer.getSources({
          types: ["screen", "window"],
          thumbnailSize: {
            width: 320,
            height: 180
          }
        });

        const screen = sources.find((source) =>
          source.id.startsWith("screen:")
        );

        if (screen) {
          callback({
            video: screen
          });
        } else {
          callback({});
        }
      } catch {
        callback({});
      }
    },
    {
      useSystemPicker: true
    }
  );

  registerIpcHandlers();
  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});
EOF

cat > apps/desktop/electron/preload.ts <<'EOF'
import { contextBridge, ipcRenderer } from "electron";

interface ScreenSource {
  id: string;
  name: string;
  type: "screen" | "window";
  thumbnail: string;
}

type SessionState =
  | "idle"
  | "waiting"
  | "sharing"
  | "ended";

interface ScreenBridgeSession {
  id: string;
  status: SessionState;
  createdAt: string;
  sourceId: string | null;
}

const screenBridge = Object.freeze({
  version: "0.1.0-alpha.1",
  platform: process.platform,
  isElectron: true,

  getScreenSources(): Promise<ScreenSource[]> {
    return ipcRenderer.invoke("screenbridge:get-sources");
  },

  createSession(): Promise<ScreenBridgeSession> {
    return ipcRenderer.invoke("screenbridge:create-session");
  },

  getSession(): Promise<ScreenBridgeSession | null> {
    return ipcRenderer.invoke("screenbridge:get-session");
  },

  startSharing(
    sourceId: string
  ): Promise<ScreenBridgeSession> {
    return ipcRenderer.invoke(
      "screenbridge:start-sharing",
      sourceId
    );
  },

  endSession(): Promise<ScreenBridgeSession | null> {
    return ipcRenderer.invoke("screenbridge:end-session");
  }
});

contextBridge.exposeInMainWorld(
  "screenBridge",
  screenBridge
);
EOF

cat > apps/desktop/src/electron.d.ts <<'EOF'
export {};

declare global {
  interface ScreenBridgeSource {
    id: string;
    name: string;
    type: "screen" | "window";
    thumbnail: string;
  }

  type ScreenBridgeSessionState =
    | "idle"
    | "waiting"
    | "sharing"
    | "ended";

  interface ScreenBridgeSession {
    id: string;
    status: ScreenBridgeSessionState;
    createdAt: string;
    sourceId: string | null;
  }

  interface Window {
    screenBridge: {
      version: string;
      platform: string;
      isElectron: boolean;

      getScreenSources(): Promise<
        ScreenBridgeSource[]
      >;

      createSession(): Promise<ScreenBridgeSession>;

      getSession(): Promise<
        ScreenBridgeSession | null
      >;

      startSharing(
        sourceId: string
      ): Promise<ScreenBridgeSession>;

      endSession(): Promise<
        ScreenBridgeSession | null
      >;
    };
  }
}
EOF

pnpm --filter @screenbridge/desktop run typecheck
pnpm --filter @screenbridge/desktop run typecheck:electron
pnpm --filter @screenbridge/desktop run build
pnpm --filter @screenbridge/desktop run build:electron
import { useEffect, useState } from "react";
type ShareMode = "screen" | "window" | "application";
type Session = {
};
const fallbackSession: Session = {
};
function formatDate(value: string) {
}
export default function App() {
}
cd ~/screenbridge
pnpm --filter @screenbridge/desktop run typecheck
pnpm --filter @screenbridge/desktop run typecheck:electron
pnpm --filter @screenbridge/desktop run build
pnpm --filter @screenbridge/desktop run build:electron
import {
} from "react";
type ShareMode =
type Session = {
};
const fallbackSession: Session = {
};
function formatDate(value: string) {
}
export default function App() {
exit
set -e
echo "=============================================="
echo " CupidCreativeX GitHub Commit & Push"
echo "=============================================="
# 1. Give Termux access to Android storage
termux-setup-storage 2>/dev/null || true
echo
echo "Searching Downloads for the latest CupidCreativeX project..."
DOWNLOADS="$HOME/storage/downloads"
ZIP="$(find "$DOWNLOADS" -maxdepth 1 -type f \
  -name 'CupidCreativeX_FULL_SOURCE_EXAM_PROJECTS_v1_COMPANY_LOGO.zip' \
  -print -quit 2>/dev/null)"
if [ -z "$ZIP" ]; then   echo;   echo "ERROR: The project ZIP was not found.";   echo;   echo "Expected file:";   echo "CupidCreativeX_FULL_SOURCE_EXAM_PROJECTS_v1_COMPANY_LOGO.zip";   echo;   echo "Make sure you downloaded it to your Android Downloads folder,";   echo "then run this block again.";   exit 1; fi
