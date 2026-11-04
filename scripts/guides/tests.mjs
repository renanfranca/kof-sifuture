export const tests = {
  'assertion-free-test': [
    'Assertion Roulette without the roulette: this test passes as long as nothing throws, so it will keep passing after the behaviour it was written for is gone.',
    'Decide what the code is *for* and assert that. If the only honest assertion is that the call returns, the test is telling you the function has no observable behaviour worth naming — which is a finding about the design, not about the test.',
    'Not this: asserting that the result is not null, or only its size. A mutation that changes every value in that object survives both.',
  ],
  'mystery-guest': [
    'Mystery Guest. The value this test depends on is assigned in `setup`, so you cannot read the test from its own body — you have to scroll up, hold the hook in your head, and hope no other test changed it first.',
    'Product code is DRY; test code is WET. Build what the test needs *in* the test, and give the setup a name that reads as a sentence: a Test Data Builder for the value, or a `given…` function defined below the test in the same file.',
    'A shared static field is also how tests start depending on each other. If two tests need the same object, two builders calling the same defaults is cheaper than one field they both reach into.',
    'Not this: moving the assignment into each test but keeping the static field. The field is still shared, and the next hook can still fill it.',
  ],
  'branching-test': [
    'A test with a branch describes two behaviours and checks whichever one today happens to take. The other path is untested, and the test name can only be honest about one of them.',
    'Split it: one test per path, each named for the case it covers. The condition you were branching on is usually the sentence the two names are missing.',
    'Not this: asserting inside both arms. That is still one test with a name that describes half of it.',
  ],
  'looping-test': [
    'A loop over cases runs every case, so nothing is skipped — but when one fails, the report names the test and not the case, and you are left rerunning it by hand to find out which input broke.',
    'Use `testRows` from `kof.test` and put the case in the row. Every row runs in isolation and the failure names it (`row 0 [2, 5]: … expected 5, got 4`), which is the whole reason you wrote a table.',
    'If the loop is arranging the world rather than walking cases — advancing the game N steps, placing every meteor — it is a missing name, not a missing table: move it into a `given…` function below the tests, so the body reads as the sentence.',
    'Not this: a loop with an index in the assertion message. That is `testRows` with worse output, and the first failing case still stops the rest.',
  ],
  'unnamed-arrange': [
    'Everything before the first assertion is setup, and this much of it unnamed means the test opens with a paragraph of how before it says a word about what.',
    'Name it. A Test Data Builder for the values — `aTraveller().carrying(lamp)` — and a `given…` function for the arranging, defined in the same file below the tests so the reader never leaves the file to understand the test.',
    'The threshold is a conversation, not a law: a test that genuinely needs a lot of world is telling you the unit under test needs a lot of world, and that is worth hearing before you go quiet.',
    'Not this: moving the statements into a `setup` function. The count goes down and the test gets harder to read, because now the setup is invisible from the body.',
  ],
};
