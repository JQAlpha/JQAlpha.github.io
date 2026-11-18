#!/usr/bin/env node
/**
 * Astro CLI 启动器
 *
 * 背景：本机的系统 Node 是 22.22.2，而 Astro 7 要求 >= 22.23.4，
 * 直接跑 `npm run build` 会报 "Node.js v22.22.2 is not supported by Astro!"。
 * 我们在项目内的 tools/node22 放了一份便携版 Node 22.23.5 专门给这个项目用。
 *
 * 这个脚本的逻辑：
 *   1. 如果项目内的便携版 Node 存在且版本满足要求 → 用它
 *   2. 否则退回系统 Node（万一你以后升级了系统 Node，也能正常工作）
 *
 * 用法：node scripts/astro.mjs build|dev|preview|check
 */

import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const siteRoot = resolve(__dirname, '..');
const portableNode = resolve(siteRoot, 'tools', 'node22', 'node.exe');
const astroBin = join(siteRoot, 'node_modules', 'astro', 'bin', 'astro.mjs');

const MIN_MAJOR = 22;
const MIN_MINOR = 23;
const MIN_PATCH = 4;

function satisfies(nodeVersion) {
  const m = /^v?(\d+)\.(\d+)\.(\d+)/.exec(nodeVersion);
  if (!m) return false;
  const [, major, minor, patch] = m.map(Number);
  if (major > MIN_MAJOR) return true;
  if (major < MIN_MAJOR) return false;
  if (minor > MIN_MINOR) return true;
  if (minor < MIN_MINOR) return false;
  return patch >= MIN_PATCH;
}

function probeVersion(execPath) {
  return new Promise((resolve) => {
    const child = spawn(execPath, ['--version'], { stdio: ['ignore', 'pipe', 'ignore'] });
    let out = '';
    child.stdout.on('data', (d) => (out += d));
    child.on('error', () => resolve(null));
    child.on('close', () => resolve(out.trim() || null));
  });
}

async function pickNode() {
  // 优先用便携版
  if (existsSync(portableNode)) {
    const v = await probeVersion(portableNode);
    if (v && satisfies(v)) {
      return { exec: portableNode, version: v, source: 'portable' };
    }
  }
  // 退回系统 Node
  const sysVersion = process.version;
  if (satisfies(sysVersion)) {
    return { exec: process.execPath, version: sysVersion, source: 'system' };
  }
  return null;
}

const args = process.argv.slice(2);
if (args.length === 0) args.push('dev');

const picked = await pickNode();

if (!picked) {
  console.error(
    '\n[astro.mjs] 找不到满足要求的 Node 版本。\n' +
      `  需要 >= ${MIN_MAJOR}.${MIN_MINOR}.${MIN_PATCH}，当前 ${process.version}\n` +
      '  修复方式：升级系统 Node，或重新下载便携版到 .tools/node22\n'
  );
  process.exit(1);
}

if (picked.source === 'portable') {
  console.log(`[astro.mjs] 使用便携版 Node ${picked.version} (.tools/node22)`);
} else {
  console.log(`[astro.mjs] 使用系统 Node ${picked.version}`);
}

const child = spawn(picked.exec, [astroBin, ...args], {
  stdio: 'inherit',
  cwd: siteRoot,
  env: process.env,
});

child.on('close', (code) => process.exit(code ?? 0));
child.on('error', (err) => {
  console.error('[astro.mjs] 启动失败:', err.message);
  process.exit(1);
});
