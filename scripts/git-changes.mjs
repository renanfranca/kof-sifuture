import { spawnSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import path from 'node:path';

export const BASE = 'main';

function git(root, ...args) {
  return spawnSync('git', args, { cwd: root, encoding: 'utf8' });
}

function paths(result) {
  return (result.stdout ?? '').split('\0').filter(Boolean);
}

export function changedAgainstBase(root, base = BASE) {
  const mergeBase = git(root, 'merge-base', base, 'HEAD');
  if (mergeBase.status !== 0) return { unavailable: [`cannot compare with \`${base}\`: ${mergeBase.stderr.trim()}`] };

  const changed = paths(git(root, 'diff', '--name-only', '-z', '--diff-filter=d', mergeBase.stdout.trim()));
  const untracked = paths(git(root, 'ls-files', '--others', '--exclude-standard', '-z'));

  return { files: [...new Set([...changed, ...untracked])].filter((file) => existsSync(path.join(root, file))).sort() };
}

export function changedKofFiles(root, base = BASE) {
  const changes = changedAgainstBase(root, base);
  if (changes.unavailable) return changes;

  return { files: changes.files.filter((file) => file.endsWith('.kf')) };
}

export function allKofFiles(root) {
  const tracked = paths(git(root, 'ls-files', '-z', '--', '*.kf'));
  const untracked = paths(git(root, 'ls-files', '--others', '--exclude-standard', '-z', '--', '*.kf'));

  return [...new Set([...tracked, ...untracked])].filter((file) => existsSync(path.join(root, file))).sort();
}

const RENAMED_OR_COPIED = /^[RC]/;

export function dirtyPaths(root) {
  const entries = paths(git(root, 'status', '--porcelain=v1', '-z', '--untracked-files=all'));
  const dirty = [];
  for (let at = 0; at < entries.length; at += 1) {
    dirty.push(entries[at].slice(3));
    if (RENAMED_OR_COPIED.test(entries[at])) at += 1;
  }
  return [...new Set(dirty)].sort();
}

export function publishableFiles(root) {
  return paths(git(root, 'ls-files', '-co', '--exclude-standard', '-z'))
    .filter((file) => existsSync(path.join(root, file)))
    .sort();
}
