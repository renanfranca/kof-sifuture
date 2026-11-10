package sifuture.sensors;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.TimeUnit;
import static org.junit.jupiter.api.Assertions.*;

class FindingsTest {
    @TempDir Path root;

    @Test void longFunctionIsReportedAboveTwentyFiveLinesAndNotAtTwentyFive() throws Exception {
        var source = function("atLimit", 23) + function("aboveLimit", 24);
        var file = aCheckedSource("src/main/kof/Long.kf", source);

        var report = findingsFor(0, file);

        var longFunctions = withRule(report, "long-function");
        assertEquals(1, longFunctions.size(), report.toPrettyString());
        var finding = longFunctions.getFirst();
        assertEquals("src/main/kof/Long.kf", finding.get("file").asText());
        assertEquals("aboveLimit", finding.get("name").asText());
        assertEquals(26, finding.get("line").asInt());
        assertEquals(1, finding.get("column").asInt());
        assertEquals(26, finding.get("value").asInt());
        assertEquals(25, finding.get("limit").asInt());
    }

    @Test void highComplexityIsReportedAboveTenAndNotAtTen() throws Exception {
        var source = deciding("atLimit", 9) + deciding("aboveLimit", 10);
        var file = aCheckedSource("src/main/kof/Complex.kf", source);

        var report = findingsFor(0, file);

        var complex = withRule(report, "high-complexity");
        assertEquals(1, complex.size(), report.toPrettyString());
        assertEquals("aboveLimit", complex.getFirst().get("name").asText());
        assertEquals(11, complex.getFirst().get("value").asInt());
        assertEquals(10, complex.getFirst().get("limit").asInt());
    }

    @Test void tooManyParametersIsReportedAboveFourAndNotAtFour() throws Exception {
        var source = """
            Int atLimit(Int a, Int b, Int c, Int d) { return a + b + c + d }
            Int aboveLimit(Int a, Int b, Int c, Int d, Int e) { return a + b + c + d + e }
            """;
        var file = aCheckedSource("src/main/kof/Wide.kf", source);

        var report = findingsFor(0, file);

        var wide = withRule(report, "too-many-parameters");
        assertEquals(1, wide.size(), report.toPrettyString());
        assertEquals("aboveLimit", wide.getFirst().get("name").asText());
        assertEquals(2, wide.getFirst().get("line").asInt());
        assertEquals(5, wide.getFirst().get("value").asInt());
        assertEquals(4, wide.getFirst().get("limit").asInt());
    }

    @Test void deepNestingIsReportedAboveTwoLevelsAndNotAtTwo() throws Exception {
        var source = """
            Int atLimit(Int a) {
                if (a > 0) {
                    if (a > 1) { return 2 }
                }
                return 0
            }
            Int aboveLimit(Int a) {
                if (a > 0) {
                    if (a > 1) {
                        if (a > 2) { return 3 }
                    }
                }
                return 0
            }
            """;
        var file = aCheckedSource("src/main/kof/Deep.kf", source);

        var report = findingsFor(0, file);

        var deep = withRule(report, "deep-nesting");
        assertEquals(1, deep.size(), report.toPrettyString());
        assertEquals("aboveLimit", deep.getFirst().get("name").asText());
        assertEquals(3, deep.getFirst().get("value").asInt());
        assertEquals(2, deep.getFirst().get("limit").asInt());
    }

    @Test void tooManyStatementsIsReportedAboveSeventeenAndNotAtSeventeen() throws Exception {
        var source = function("atLimit", 17) + function("aboveLimit", 18);
        var file = aCheckedSource("src/main/kof/Busy.kf", source);

        var report = findingsFor(0, file);

        var busy = withRule(report, "too-many-statements");
        assertEquals(1, busy.size(), report.toPrettyString());
        assertEquals("aboveLimit", busy.getFirst().get("name").asText());
        assertEquals(18, busy.getFirst().get("value").asInt());
        assertEquals(17, busy.getFirst().get("limit").asInt());
    }

    @Test void suitesAreExemptFromLengthAndStatementsButMeasuredForComplexity() throws Exception {
        var longTest = "test \"long journey\" {\n" + "    println(1)\n".repeat(30) + "    assert(true)\n}\n";
        var file = aCheckedSource("src/test/kof/JourneyTest.kf", longTest + deciding("aboveLimit", 10));

        var report = findingsFor(0, file);

        assertEquals(List.of(), withRule(report, "long-function"), report.toPrettyString());
        assertEquals(List.of(), withRule(report, "too-many-statements"), report.toPrettyString());
        assertEquals(1, withRule(report, "high-complexity").size(), report.toPrettyString());
    }

    @Test void longFileIsReportedAboveOneHundredFiftyLinesAndNotAtOneHundredFifty() throws Exception {
        var atLimit = aCheckedSource("src/main/kof/AtLimit.kf", oneLiners("at", 150));
        var aboveLimit = aCheckedSource("src/main/kof/AboveLimit.kf", oneLiners("above", 151));

        var report = findingsFor(0, atLimit, aboveLimit);

        var big = withRule(report, "long-file");
        assertEquals(1, big.size(), report.toPrettyString());
        assertEquals("src/main/kof/AboveLimit.kf", big.getFirst().get("file").asText());
        assertEquals(1, big.getFirst().get("line").asInt());
        assertEquals(151, big.getFirst().get("value").asInt());
        assertEquals(150, big.getFirst().get("limit").asInt());
    }

    @Test void testCodeLongFileIsReportedAboveOneThousandLinesAndNotAtOneThousand() throws Exception {
        var suiteAtLimit = aCheckedSource("src/test/kof/AtLimit.kf", oneLiners("at", 1000));
        var suiteAboveLimit = aCheckedSource("src/test/kof/AboveLimit.kf", oneLiners("above", 1001));
        var fixtureAboveLimit = aCheckedSource("tests/fixture.kf", oneLiners("fixture", 1001));

        var report = findingsFor(0, suiteAtLimit, suiteAboveLimit, fixtureAboveLimit);

        var big = withRule(report, "long-file");
        assertEquals(List.of("src/test/kof/AboveLimit.kf", "tests/fixture.kf"),
                big.stream().map(f -> f.get("file").asText()).sorted().toList(), report.toPrettyString());
        assertEquals(List.of(1001, 1001), big.stream().map(f -> f.get("value").asInt()).toList());
        assertEquals(List.of(1000, 1000), big.stream().map(f -> f.get("limit").asInt()).toList());
    }

    @Test void duplicationReportsAFiftyTokenFiveLineCloneWithRelativeLocations() throws Exception {
        var source = """
            main() {
                var alpha = 101 + 102 + 103 + 104 + 105
                var beta = 201 + 202 + 203 + 204 + 205
                var gamma = 301 + 302 + 303 + 304 + 305
                var delta = 401 + 402 + 403 + 404 + 405
                println(alpha + beta + gamma + delta)
            }
            """;
        var first = aCheckedSource("src/main/kof/First.kf", source);
        var second = aCheckedSource("src/main/kof/Second.kf", source);

        var duplication = findingsFor(0, first, second).get("duplication");

        assertEquals(50, duplication.get("minimumTokens").asInt());
        assertEquals(5, duplication.get("minimumLines").asInt());
        assertEquals(List.of("src/main/kof/First.kf", "src/main/kof/Second.kf"), texts(duplication.get("expected")));
        assertEquals(List.of("src/main/kof/First.kf", "src/main/kof/Second.kf"), texts(duplication.get("tokenized")));
        assertEquals(1, duplication.get("clones").size(), duplication.toPrettyString());
        var clone = duplication.get("clones").get(0);
        assertTrue(clone.get("tokens").asInt() >= 50);
        var files = new ArrayList<String>();
        clone.get("locations").forEach(location -> files.add(location.get("file").asText()));
        assertEquals(List.of("src/main/kof/First.kf", "src/main/kof/Second.kf"), files.stream().sorted().toList());
        assertEquals(1, clone.get("locations").get(0).get("line").asInt());
    }

    @Test void duplicationLeavesTestCodeOutAndStillReportsProductionClones() throws Exception {
        var source = """
            main() {
                var alpha = 101 + 102 + 103 + 104 + 105
                var beta = 201 + 202 + 203 + 204 + 205
                var gamma = 301 + 302 + 303 + 304 + 305
                var delta = 401 + 402 + 403 + 404 + 405
                println(alpha + beta + gamma + delta)
            }
            """;
        var suite = aCheckedSource("src/test/kof/Journey.kf", source);
        var fixture = aCheckedSource("tests/fixture.kf", source);
        var production = aCheckedSource("src/main/kof/First.kf", source);
        var copy = aCheckedSource("src/main/kof/Second.kf", source);

        var report = findingsFor(0, suite, fixture, production, copy);

        var duplication = report.get("duplication");
        assertEquals(List.of("src/test/kof/Journey.kf", "tests/fixture.kf", "src/main/kof/First.kf", "src/main/kof/Second.kf"),
                texts(report.get("expected")));
        assertEquals(List.of("src/main/kof/First.kf", "src/main/kof/Second.kf"), texts(duplication.get("expected")));
        assertEquals(List.of("src/main/kof/First.kf", "src/main/kof/Second.kf"), texts(duplication.get("tokenized")));
        assertEquals(1, duplication.get("clones").size(), duplication.toPrettyString());
        var files = new ArrayList<String>();
        duplication.get("clones").get(0).get("locations").forEach(location -> files.add(location.get("file").asText()));
        assertEquals(List.of("src/main/kof/First.kf", "src/main/kof/Second.kf"), files.stream().sorted().toList());
    }

    @Test void assertionFreeTestIsReportedWhileAssertingTestsAreNot() throws Exception {
        var source = """
            import kof.test

            test "only prints" {
                println(1)
            }

            test "asserts directly" {
                assert(1 + 1 == 2)
            }

            test "asserts with a helper" {
                assertEqualInt(2, 1 + 1, "sum")
            }

            test "asserts each row" {
                testRows(listOf(listOf("1", "1")), "identity", (r: List<String>) -> {
                    assertEqualString(r.get(0), r.get(1), "same")
                })
            }
            """;
        var file = aCheckedSource("src/test/kof/AssertionTest.kf", source);

        var report = findingsFor(0, file);

        var silent = withRule(report, "assertion-free-test");
        assertEquals(1, silent.size(), report.toPrettyString());
        assertEquals("only prints", silent.getFirst().get("name").asText());
        assertEquals(3, silent.getFirst().get("line").asInt());
        assertEquals(1, silent.getFirst().get("column").asInt());
    }

    @Test void branchingTestReportsEachConditionalInsideATest() throws Exception {
        var source = """
            test "branches" {
                var a = 2
                if (a > 1) {
                    assert(a == 2)
                }
                var b = if (a > 1) 1 else 0
                switch (b) {
                    case 1: assert(true)
                    default: assert(false)
                }
            }

            test "straight" {
                assert(1 == 1)
            }

            Int helper(Int a) {
                if (a > 0) { return 1 }
                return 0
            }
            """;
        var file = aCheckedSource("src/test/kof/BranchTest.kf", source);

        var report = findingsFor(0, file);

        var branching = withRule(report, "branching-test");
        assertEquals(List.of(3, 6, 7), branching.stream().map(f -> f.get("line").asInt()).toList(), report.toPrettyString());
        assertTrue(branching.stream().allMatch(f -> f.get("name").asText().equals("branches")));
    }

    @Test void loopingTestReportsEachLoopInsideATest() throws Exception {
        var source = """
            test "loops" {
                var total = 0
                for (var i = 0; i < 2; i = i + 1) {
                    total = total + i
                }
                for (var n in listOf(1, 2)) {
                    total = total + n
                }
                while (total < 10) {
                    total = total + 1
                }
                var steps = 0
                do {
                    steps = steps + 1
                } while (steps < 2)
                assert(total == 10)
            }
            """;
        var file = aCheckedSource("src/test/kof/LoopTest.kf", source);

        var report = findingsFor(0, file);

        var looping = withRule(report, "looping-test");
        assertEquals(List.of(3, 6, 9, 13), looping.stream().map(f -> f.get("line").asInt()).toList(), report.toPrettyString());
    }

    @Test void unnamedArrangeIsReportedAboveEightStatementsBeforeTheFirstAssertion() throws Exception {
        var source = arranging("eight before asserting", 8) + arranging("nine before asserting", 9);
        var file = aCheckedSource("src/test/kof/ArrangeTest.kf", source);

        var report = findingsFor(0, file);

        var unnamed = withRule(report, "unnamed-arrange");
        assertEquals(1, unnamed.size(), report.toPrettyString());
        assertEquals("nine before asserting", unnamed.getFirst().get("name").asText());
        assertEquals(9, unnamed.getFirst().get("value").asInt());
        assertEquals(8, unnamed.getFirst().get("limit").asInt());
    }

    static String arranging(String name, int statements) {
        var body = new StringBuilder();
        for (int number = 1; number <= statements; number++) body.append("    var v%d = %d\n".formatted(number, number));
        return "test \"" + name + "\" {\n" + body + "    assert(v1 == 1)\n    println(v1)\n}\n";
    }

    @Test void mysteryGuestIsReportedWhereAHookFillsSharedState() throws Exception {
        var guest = aCheckedSource("src/test/kof/GuestTest.kf", """
            class Fixture {
                static Int shared = 0
                static Int other = 0
            }

            void setup() {
                var local = 40
                local = local + 1
                Fixture.shared = local
            }

            void beforeAll() {
                Fixture.other = 1
            }

            test "reads what setup filled" {
                assert(Fixture.shared == 41)
            }
            """);
        var host = aCheckedSource("src/test/kof/HostTest.kf", """
            void setup() {
                var local = 1
                local = local + 1
                println(local)
            }

            test "builds its own world" {
                var world = 2
                assert(world == 2)
            }
            """);

        var report = findingsFor(0, guest, host);

        var guests = withRule(report, "mystery-guest");
        assertEquals(List.of("Fixture.shared", "Fixture.other"), guests.stream().map(f -> f.get("name").asText()).toList(),
                report.toPrettyString());
        assertEquals(List.of(9, 13), guests.stream().map(f -> f.get("line").asInt()).toList());
        assertTrue(guests.stream().allMatch(f -> f.get("file").asText().equals("src/test/kof/GuestTest.kf")));
    }

    @Test void longCommentReportsMultiLineCommentsButNotOneLinersOrStrings() throws Exception {
        var source = """
            // first line of a paragraph
            // second line of the paragraph
            Int one() { return 1 }

            // a single line is fine
            Int two() { return 2 }

            /* a block
               that keeps going
               for three lines */
            main() {
                var a = "// looks like a comment"
                var b = "// on the next line too /* and a block"
                println(a + b + one() + two())
            }
            """;
        var file = aCheckedSource("src/main/kof/Commented.kf", source);

        var report = findingsFor(0, file);

        var longComments = withRule(report, "long-comment");
        assertEquals(List.of(1, 8), longComments.stream().map(f -> f.get("line").asInt()).toList(), report.toPrettyString());
        assertEquals(List.of(2, 3), longComments.stream().map(f -> f.get("value").asInt()).toList());
        assertEquals(1, longComments.getFirst().get("limit").asInt());
    }

    @Test void deferredWorkIsReportedInCommentsButNotInStringsOrOtherWords() throws Exception {
        var source = """
            // TODO make it faster
            Int one() { return 1 }
            /* a Hack until the engine updates */
            main() {
                var note = "todo: not a comment"
                var word = "hackathon"
                println(note + word + one())
            }
            // the shacks and todolist are fine
            """;
        var file = aCheckedSource("src/main/kof/Deferred.kf", source);

        var report = findingsFor(0, file);

        var deferred = withRule(report, "deferred-work");
        assertEquals(List.of(1, 3), deferred.stream().map(f -> f.get("line").asInt()).toList(), report.toPrettyString());
        assertEquals(List.of("TODO", "Hack"), deferred.stream().map(f -> f.get("name").asText()).toList());
    }

    @Test void staleCommentReportsBacktickedNamesAndPathsThatAreNotThere() throws Exception {
        var source = """
            // `shipSpeed` limits the ship, see `src/main/kof/Stale.kf`
            Int shipSpeed() { return 5 }
            // `oldSpeed()` was the previous rule
            Int other() { return 1 }
            // the `speed` word and `docs/missing.md` guide
            main() { println(shipSpeed() + other()) }
            """;
        var file = aCheckedSource("src/main/kof/Stale.kf", source);

        var report = findingsFor(0, file);

        var stale = withRule(report, "stale-comment");
        assertEquals(List.of("oldSpeed()", "docs/missing.md"), stale.stream().map(f -> f.get("name").asText()).toList(),
                report.toPrettyString());
        assertEquals(List.of(3, 5), stale.stream().map(f -> f.get("line").asInt()).toList());
    }

    @Test void commentedOutCodeIsReportedWhenTheParserAcceptsTheCommentAsKof() throws Exception {
        var source = """
            // var speed = 4
            Int one() { return 1 }

            // the ship moves five units per step, then waits
            Int two() { return 2 }

            // Int old() { return 2 }
            /* if (one() > 1) { println(1) } */
            main() { println(one() + two()) }
            // player

            // first line of a paragraph

            // return early on failure

            // throw it away
            """;
        var file = aCheckedSource("src/main/kof/Dead.kf", source);

        var report = findingsFor(0, file);

        var dead = withRule(report, "commented-out-code");
        assertEquals(List.of(1, 7, 8), dead.stream().map(f -> f.get("line").asInt()).toList(), report.toPrettyString());
    }

    static List<String> texts(JsonNode array) {
        var values = new ArrayList<String>();
        array.forEach(value -> values.add(value.asText()));
        return values;
    }

    static String oneLiners(String prefix, int count) {
        var source = new StringBuilder();
        for (int number = 1; number <= count; number++) source.append("Int %s%d() { return %d }\n".formatted(prefix, number, number));
        return source.toString();
    }

    static String deciding(String name, int decisions) {
        var body = new StringBuilder();
        for (int value = 1; value <= decisions; value++) body.append("    if (a == %d) { return %d }\n".formatted(value, value));
        return "Int " + name + "(Int a) {\n" + body + "    return 0\n}\n";
    }

    static String function(String name, int printedLines) {
        return "void " + name + "() {\n" + "    println(1)\n".repeat(printedLines) + "}\n";
    }

    Path aCheckedSource(String relative, String source) throws Exception {
        var file = root.resolve(relative);
        Files.createDirectories(file.getParent());
        Files.writeString(file, source);
        for (var target : List.of("jvm", "js")) assertOfficialCheckPasses(file, target);
        return file;
    }

    void assertOfficialCheckPasses(Path file, String target) throws Exception {
        var executable = System.getenv().getOrDefault("KOF", "kof");
        var output = root.resolve("check-" + target + ".txt");
        var process = new ProcessBuilder(executable, "check", file.toString(), "--target", target)
                .redirectErrorStream(true).redirectOutput(output.toFile()).start();
        if (!process.waitFor(60, TimeUnit.SECONDS)) {
            process.destroyForcibly();
            fail("Kof check timed out for " + target);
        }
        assertEquals(0, process.exitValue(), Files.readString(output));
    }

    JsonNode findingsFor(int expectedExit, Path... files) throws Exception {
        var command = new ArrayList<>(List.of(Path.of(System.getProperty("java.home"), "bin/java").toString(),
                "-cp", System.getProperty("java.class.path"), "sifuture.sensors.Main", "--findings", root.toString()));
        for (var file : files) command.add(file.toString());
        var output = root.resolve("findings.json");
        var errors = root.resolve("findings.stderr");
        var process = new ProcessBuilder(command).redirectOutput(output.toFile()).redirectError(errors.toFile()).start();
        assertEquals(expectedExit, process.waitFor(), Files.readString(errors));
        return new ObjectMapper().readTree(output.toFile());
    }

    static List<JsonNode> withRule(JsonNode report, String rule) {
        var found = new ArrayList<JsonNode>();
        report.get("findings").forEach(finding -> {
            if (finding.get("rule").asText().equals(rule)) found.add(finding);
        });
        return found;
    }
}
