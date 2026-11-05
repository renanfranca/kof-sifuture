export function unavailableReport(sensor, reasons) {
  return [
    `SENSOR ${sensor}: UNAVAILABLE`,
    '',
    ...reasons.map((reason) => `  ${reason}`),
    '  A sensor that could not run has not passed.',
    '',
  ].join('\n');
}
