// Electron 主进程：本地可安装软件的外壳。
// - 启动内置本地服务（server/index.mjs，持有密钥、转发模型请求）。
// - 加载打包后的前端（dist/），/api 请求指向本地服务端口。
// 开发期用 `npm run dev` + `npm run server` 即可，无需 Electron。

import { app, BrowserWindow, shell } from 'electron';
import { fork } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SERVER_PORT = 8787;

let serverProcess = null;

function startLocalServer() {
  const serverPath = path.join(__dirname, '../server/index.mjs');
  serverProcess = fork(serverPath, [], {
    env: {
      ...process.env,
      MACROMIND_UI_PORT: String(SERVER_PORT),
      // 打包后：本地服务同时提供 dist/ 静态文件
      MACROMIND_UI_DIST: path.join(__dirname, '../dist'),
      // 打包后模型配置放在用户数据目录；开发期回退仓库内路径
      MACROMIND_MODEL_CONFIG:
        process.env.MACROMIND_MODEL_CONFIG ||
        (app.isPackaged
          ? path.join(app.getPath('userData'), 'model.local.json')
          : path.join(__dirname, '../../macro-mind-engine/model.local.json')),
    },
    stdio: 'ignore',
  });
}

/** 等待本地服务就绪（最多 ~5 秒） */
async function waitForServer(port, tries = 25) {
  for (let i = 0; i < tries; i += 1) {
    try {
      const res = await fetch(`http://127.0.0.1:${port}/api/health`);
      if (res.ok) return true;
    } catch {
      /* 继续等待 */
    }
    await new Promise((r) => setTimeout(r, 200));
  }
  return false;
}

function createWindow() {
  const win = new BrowserWindow({
    width: 1440,
    height: 900,
    minWidth: 760,
    minHeight: 560,
    title: 'MacroMind',
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
  });
  // 外部链接用系统浏览器打开
  win.webContents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith('http')) shell.openExternal(url);
    return { action: 'deny' };
  });

  if (app.isPackaged) {
    // 前端由本地服务提供（http 源，/api 同源可达）
    win.loadURL(`http://127.0.0.1:${SERVER_PORT}/`);
  } else {
    win.loadURL('http://localhost:5173');
  }
}

app.whenReady().then(async () => {
  startLocalServer();
  if (app.isPackaged) await waitForServer(SERVER_PORT);
  createWindow();
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

app.on('quit', () => {
  serverProcess?.kill();
});
