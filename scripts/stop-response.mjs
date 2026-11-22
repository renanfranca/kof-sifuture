import { shouldPushBack } from './stop-continuation.mjs';

const OUTPUT_LIMIT = 6_000;

function head(report) {
  const text = report.trim();
  if (text.length <= OUTPUT_LIMIT) return text;

  return `${text.slice(0, OUTPUT_LIMIT)}\n\n… truncated. Run \`npm run check\` for the rest.`;
}

function failureMessage(report) {
  return [
    'The Stop sensors are not satisfied by the files this session changed.',
    'Fix the findings below, then try to finish again.',
    '',
    head(report),
  ].join('\n');
}

export function stopResponse(verdict, pushBack) {
  if (verdict.passed) return { continue: true, systemMessage: verdict.report.trim() };

  const message = failureMessage(verdict.report);
  if (pushBack) return { decision: 'block', reason: message };

  return { continue: true, systemMessage: `The Stop sensors still have findings; this session will not be pushed back again for them.\n\n${message}` };
}

export function stopAnswer(root, payload, verdict) {
  const pushBack = !verdict.passed && !payload.stop_hook_active && shouldPushBack(root, payload.session_id, verdict.findings);

  return stopResponse(verdict, pushBack);
}
