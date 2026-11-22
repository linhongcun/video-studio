import test from 'node:test';
import assert from 'node:assert/strict';
import {
  resolveVideoHostConfig,
  resolveVideoUrl,
  shouldCopyVideoToPublic,
  isExternalVideoActive,
  isVersionReleaseTag,
} from './video-host.mjs';

test('defaults to local mode using repository site base path', () => {
  const cfg = {mode: 'local', baseUrl: '', pathTemplate: 'episodes/{slug}/{filename}', fallbackToLocalInDev: true};
  assert.equal(isExternalVideoActive({config: cfg, env: {}}), false);
  assert.equal(shouldCopyVideoToPublic({config: cfg, env: {}}), true);
  assert.equal(
    resolveVideoUrl('http-request', 'video.mp4', {config: cfg, env: {}, base: '/video-studio/'}),
    '/video-studio/episodes/http-request/video.mp4',
  );
});

test('external mode via VIDEO_HOST_BASE_URL rewrites playback URL and skips Pages bundling', () => {
  const cfg = {mode: 'local', baseUrl: '', pathTemplate: 'episodes/{slug}/{filename}', fallbackToLocalInDev: true};
  const env = {VIDEO_HOST_BASE_URL: 'https://media.example.com/'};
  assert.equal(isExternalVideoActive({config: cfg, env}), true);
  assert.equal(shouldCopyVideoToPublic({config: cfg, env}), false);
  assert.equal(
    resolveVideoUrl('two-sum', 'video.mp4', {config: cfg, env}),
    'https://media.example.com/episodes/two-sum/video.mp4',
  );
});

test('supports content-addressed sha8 path template', () => {
  const cfg = {
    mode: 'external',
    baseUrl: 'https://cdn.example.com/video-studio',
    pathTemplate: 'episodes/{slug}/{stem}-{sha8}{ext}',
    fallbackToLocalInDev: true,
  };
  assert.equal(
    resolveVideoUrl('two-sum', 'video.mp4', {config: cfg, env: {}, sha8: 'a1b2c3d4'}),
    'https://cdn.example.com/video-studio/episodes/two-sum/video-a1b2c3d4.mp4',
  );
});

test('drafts and local dev fall back to local videos unless forced', () => {
  const cfg = {
    mode: 'external',
    baseUrl: 'https://media.example.com',
    pathTemplate: 'episodes/{slug}/{filename}',
    fallbackToLocalInDev: true,
  };
  assert.equal(shouldCopyVideoToPublic({config: cfg, env: {}, isDraft: true}), true);
  assert.equal(
    resolveVideoUrl('draft-ep', 'video.mp4', {config: cfg, env: {}, isDraft: true}),
    '/video-studio/episodes/draft-ep/video.mp4',
  );
  assert.equal(shouldCopyVideoToPublic({config: cfg, env: {}, isDev: true}), true);
  assert.equal(shouldCopyVideoToPublic({config: cfg, env: {VIDEO_HOST_FORCE_IN_DEV: '1'}, isDev: true}), false);
  assert.equal(shouldCopyVideoToPublic({config: cfg, env: {COPY_LOCAL_VIDEOS: '1'}, isDev: false}), true);
});

test('rejects insecure or missing external baseUrl', () => {
  assert.throws(
    () => resolveVideoHostConfig({config: {mode: 'external', baseUrl: 'http://insecure.example.com'}, env: {}}),
    /must start with https:\/\//,
  );
  assert.throws(
    () => resolveVideoHostConfig({config: {mode: 'external', baseUrl: ''}, env: {}}),
    /must start with https:\/\//,
  );
});

test('isVersionReleaseTag accepts semver tags and rejects infrastructure tags', () => {
  assert.equal(isVersionReleaseTag('v0.111.1'), true);
  assert.equal(isVersionReleaseTag('v1.0.0'), true);
  assert.equal(isVersionReleaseTag('archive-assets-20261122'), false);
  assert.equal(isVersionReleaseTag('media-videos-v1'), false);
  assert.equal(isVersionReleaseTag(''), false);
});
