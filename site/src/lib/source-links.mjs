import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';

const repositoryRoot = fileURLToPath(new URL('../../../', import.meta.url));
const repository = 'https://github.com/linhongcun/video-studio';
const rawRepository = 'https://raw.githubusercontent.com/linhongcun/video-studio';
let snapshot;

/** The checked-out tree is the snapshot used to build this page, including its
 * published script/storyboard and the current production path in meta.json.
 * Pin that exact tree rather than a branch or a date-derived historical guess.
 * This also works with the shallow checkout used by GitHub Pages. */
export function sourceSnapshot() {
  if (!snapshot) {
    snapshot = execFileSync('git', ['rev-parse', '--verify', 'HEAD'], {cwd: repositoryRoot, encoding: 'utf8'}).trim();
    if (!/^[a-f0-9]{40}$/.test(snapshot)) throw new Error('无法确定制作文件的发布版本');
  }
  return snapshot;
}

export function episodeSourceLinks({slug, sourcePath}) {
  const ref = sourceSnapshot();
  const encodePath = (value) => {
    const parts = value.split('/');
    if (parts.some((part) => !part || part === '.' || part === '..')) throw new Error(`无效制作文件路径：${value}`);
    return parts.map(encodeURIComponent).join('/');
  };
  const episodePath = encodePath(`episodes/${slug}`);
  return [
    ...[['脚本', 'script.md'], ['分镜', 'storyboard.json']].map(([label, file]) => ({
      label, file,
      href: `${repository}/blob/${ref}/${episodePath}/${file}`,
      raw: `${rawRepository}/${ref}/${episodePath}/${file}`,
    })),
    {label: '源码', file: 'remotion/', href: `${repository}/tree/${ref}/${encodePath(sourcePath)}`},
  ];
}
