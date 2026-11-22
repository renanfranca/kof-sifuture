export async function readHookPayload(stream = process.stdin) {
  let input = '';

  for await (const chunk of stream) input += chunk;

  try {
    return JSON.parse(input);
  } catch {
    return {};
  }
}

export function answer(response) {
  process.stdout.write(JSON.stringify(response));
}
