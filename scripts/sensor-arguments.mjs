import path from 'node:path';

export const repositoryRoot = path.resolve(import.meta.dirname, '..');

export function sensorArguments(argv = process.argv.slice(2)) {
  const at = argv.indexOf('--root');
  if (at === -1) return { root: repositoryRoot, paths: argv };

  return { root: path.resolve(argv[at + 1]), paths: argv.filter((_, index) => index !== at && index !== at + 1) };
}
