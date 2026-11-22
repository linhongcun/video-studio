import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const DEFAULT_CONFIG_PATH = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  '../src/content/video-host.json',
);

const DEFAULT_CONFIG = {
  schemaVersion: 1,
  mode: 'local',
  provider: 'r2',
  baseUrl: '',
  pathTemplate: 'episodes/{slug}/{filename}',
  fallbackToLocalInDev: true,
};

export function readVideoHostConfig(configPath = DEFAULT_CONFIG_PATH) {
  if (!fs.existsSync(configPath)) return {...DEFAULT_CONFIG};
  const parsed = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  return {...DEFAULT_CONFIG, ...parsed};
}

/**
 * Resolve effective external-hosting configuration.
 * VIDEO_HOST_BASE_URL overrides video-host.json (and switches mode to 'external').
 * VIDEO_HOST_MODE=local forces local bundling even if video-host.json is external.
 */
export function resolveVideoHostConfig({env = process.env, config} = {}) {
  const base = config ? {...DEFAULT_CONFIG, ...config} : readVideoHostConfig();
  const envMode = String(env?.VIDEO_HOST_MODE ?? '').trim().toLowerCase();
  const envUrl = String(env?.VIDEO_HOST_BASE_URL ?? '').trim();
  const envTemplate = String(env?.VIDEO_HOST_PATH_TEMPLATE ?? '').trim();

  let mode = base.mode === 'external' ? 'external' : 'local';
  let baseUrl = String(base.baseUrl ?? '').trim();

  if (envUrl) {
    baseUrl = envUrl;
    mode = 'external';
  }
  if (envMode === 'local' || envMode === 'external') {
    mode = envMode;
  }

  baseUrl = baseUrl.replace(/\/+$/, '');
  if (mode === 'external' && !/^https:\/\//.test(baseUrl)) {
    throw new Error(
      `Invalid external video host baseUrl (${JSON.stringify(baseUrl)}): must start with https://`,
    );
  }

  return {
    ...base,
    mode,
    baseUrl,
    pathTemplate: envTemplate || base.pathTemplate || DEFAULT_CONFIG.pathTemplate,
    fallbackToLocalInDev: base.fallbackToLocalInDev !== false,
  };
}

export function isExternalVideoActive({env = process.env, config, isDev = false, isDraft = false} = {}) {
  const resolved = resolveVideoHostConfig({env, config});
  if (resolved.mode !== 'external') return false;
  if (isDraft) return false;
  if (isDev && resolved.fallbackToLocalInDev && env?.VIDEO_HOST_FORCE_IN_DEV !== '1') return false;
  return true;
}

/**
 * Determine whether copy-assets.mjs should place an episode's MP4 into site/public/episodes/.
 */
export function shouldCopyVideoToPublic({env = process.env, config, isDev = false, isDraft = false} = {}) {
  if (env?.COPY_LOCAL_VIDEOS === '1') return true;
  return !isExternalVideoActive({env, config, isDev, isDraft});
}

/**
 * Render the playback URL for an episode's video file.
 */
export function resolveVideoUrl(
  slug,
  filename,
  {base = '/video-studio/', env = process.env, config, isDev = false, isDraft = false, sha8 = ''} = {},
) {
  const normalizedBase = base.endsWith('/') ? base : `${base}/`;
  if (!isExternalVideoActive({env, config, isDev, isDraft})) {
    return `${normalizedBase}episodes/${slug}/${filename}`;
  }
  const resolved = resolveVideoHostConfig({env, config});
  const ext = path.posix.extname(filename);
  const stem = ext ? filename.slice(0, -ext.length) : filename;
  const rel = resolved.pathTemplate
    .replaceAll('{slug}', encodeURIComponent(slug))
    .replaceAll('{filename}', filename.split('/').map(encodeURIComponent).join('/'))
    .replaceAll('{stem}', encodeURIComponent(stem))
    .replaceAll('{ext}', ext)
    .replaceAll('{sha8}', encodeURIComponent(sha8))
    .replace(/^\/+/, '');
  return `${resolved.baseUrl}/${rel}`;
}

/**
 * Identify non-version infrastructure GitHub Release tags (e.g., archive-* / media-*)
 * so they never leak into the public /changelog/ page.
 */
export function isVersionReleaseTag(tag) {
  return /^v\d+\.\d+\.\d+(?:-[A-Za-z0-9.-]+)?$/.test(String(tag ?? '').trim());
}
