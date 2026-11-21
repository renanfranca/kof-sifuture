import { spawnSync } from 'node:child_process';
import { accessSync, constants, existsSync, readFileSync, realpathSync, statSync } from 'node:fs';
import { homedir } from 'node:os';
import path from 'node:path';

import { sensorArguments } from './sensor-arguments.mjs';
import { HOOK_EVENTS, lastSeen } from './sensor-liveness.mjs';

function executable(file) {
  try {
    accessSync(file, constants.X_OK);
    return statSync(file).isFile();
  } catch {
    return false;
  }
}

function located(command) {
  const directories = (process.env.PATH ?? '').split(path.delimiter).filter(Boolean);
  return directories.map((directory) => path.join(directory, command)).find(executable) ?? null;
}

function firstLine(command, args, pattern = /./) {
  const run = spawnSync(command, args, { encoding: 'utf8' });
  if (run.error) return null;
  return `${run.stdout}\n${run.stderr}`.split('\n').find((line) => pattern.test(line))?.trim() ?? null;
}

function kofMutVersion(executable) {
  const version = firstLine(executable, ['--version']);
  const image = path.join(path.dirname(realpathSync(executable)), 'image.json');
  const id = existsSync(image) ? JSON.parse(readFileSync(image, 'utf8')).id?.slice(0, 12) : null;
  return version && `${version} image ${id ?? 'MISSING'}`;
}

const tools = [
  { name: 'kof', version: (bin) => firstLine(bin, ['version']) },
  { name: 'kof-mut', version: kofMutVersion },
  { name: 'node', version: (bin) => firstLine(bin, ['--version']) },
  { name: 'mvn', version: (bin) => firstLine(bin, ['-v'], /Apache Maven/) },
  { name: 'java', version: (bin) => firstLine(bin, ['-version'], /version/) },
  { name: 'gitleaks', version: (bin) => firstLine(bin, ['version']) },
  { name: 'python3', version: (bin) => firstLine(bin, ['--version']) },
];

function examineTool(tool) {
  const executable = located(tool.name);
  const version = executable && tool.version(executable);
  return { label: tool.name, detail: version ?? '—', where: executable ?? '—', ok: Boolean(version) };
}

function scriptFile(command) {
  return command.match(/^node (\S+\.mjs)/)?.[1] ?? null;
}

function examineCommands(root) {
  const scripts = JSON.parse(readFileSync(path.join(root, 'package.json'), 'utf8')).scripts ?? {};
  return Object.entries(scripts)
    .map(([name, command]) => ({ name, file: scriptFile(command) }))
    .filter((entry) => entry.file)
    .map((entry) => ({ label: entry.name, detail: entry.file, ok: existsSync(path.join(root, entry.file)) }));
}

const MANIFEST = '.codex/hooks.json';
const ROOTED = /\$\(git rev-parse --show-toplevel\)\/([^"'\s]+)/;

function readManifest(root) {
  try {
    return JSON.parse(readFileSync(path.join(root, MANIFEST), 'utf8'));
  } catch {
    return null;
  }
}

function scriptsOf(groups = []) {
  return groups.flatMap((group) => group.hooks ?? []).map((hook) => hook.command?.match(ROOTED)?.[1]).filter(Boolean);
}

function lastFired(root, event) {
  const at = lastSeen(root, event);
  if (at === null) return { label: `last ${event}`, detail: 'never fired', ok: true, state: 'UNAVAILABLE' };
  return { label: `last ${event}`, detail: new Date(at).toISOString(), ok: true };
}

function hookNode() {
  const appNode = path.join(homedir(), '.local', 'bin', 'node');
  const version = executable(appNode) && firstLine(appNode, ['--version']);
  return { label: 'hook node', detail: version || '—', where: appNode, ok: Boolean(version) };
}

function examineHooks(root) {
  const manifest = readManifest(root);
  if (manifest === null) return [{ label: 'manifest', detail: MANIFEST, ok: false }];

  const scripts = HOOK_EVENTS.flatMap((event) =>
    scriptsOf(manifest.hooks?.[event]).map((script) => ({ label: event, detail: script, ok: existsSync(path.join(root, script)) })),
  );
  return [{ label: 'manifest', detail: MANIFEST, ok: true }, ...scripts, ...HOOK_EVENTS.map((event) => lastFired(root, event)), hookNode()];
}

function row(entry, width) {
  const where = entry.where ? `  ${entry.where}` : '';
  return `    ${entry.label.padEnd(width)}  ${entry.detail}${where}  ${entry.state ?? (entry.ok ? 'ok' : 'MISSING')}`;
}

function section(title, entries) {
  const width = Math.max(...entries.map((entry) => entry.label.length), 0);
  return [`  ${title}`, ...entries.map((entry) => row(entry, width))].join('\n');
}

const { root } = sensorArguments();
const toolStates = tools.map(examineTool);
const commandStates = examineCommands(root);
const hookStates = examineHooks(root);
const broken = [...toolStates, ...commandStates, ...hookStates].filter((entry) => !entry.ok);

process.stdout.write(
  [
    'SENSORS DOCTOR',
    '',
    section('Tools', toolStates),
    '',
    section('Commands', commandStates),
    '',
    section('Codex hooks', hookStates),
    '',
    '  This report checks configuration and liveness; it is not a quality certificate.',
    '',
  ].join('\n'),
);
process.exitCode = broken.length === 0 ? 0 : 1;
