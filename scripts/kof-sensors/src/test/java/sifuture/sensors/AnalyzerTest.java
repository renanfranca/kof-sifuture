package sifuture.sensors;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import static org.junit.jupiter.api.Assertions.*;

class AnalyzerTest {
    @TempDir Path root;

    Analyzer.FileMetrics measure(String source) {
        return Analyzer.measure("Probe.kf", source);
    }

    @Test void literalCountsIgnoreCommentsAndStringContents() {
        var file = measure("""
            Int plain(Int a, Int b, Int c, Int d, Int e) {

                // if (a) { && }
                var text = "if && // {}"
                /* whole comment */
                return a
            }
            """);
        var function = file.functions().getFirst();
        assertEquals(6, file.lines());
        assertEquals(4, function.lines());
        assertEquals(1, function.complexity());
        assertEquals(5, function.parameters());
        assertEquals(0, function.depth());
        assertEquals(2, function.statements());
        assertEquals(1, function.line());
        assertEquals(7, function.endLine());
    }

    @Test void nestedFunctionsLambdasMethodsAndConstructorsOwnTheirCounts() {
        var file = measure("""
            class Box {
                constructor(Int a, Int b, Int c, Int d, Int e) {
                    if (a > 0) { println(a) }
                }
                Int value() { return 1 }
            }
            main() {
                Int nested(Int x) { if (x > 0) { return x } return 0 }
                var f = (x: Int) -> { if (x > 0) { return x } return 0 }
                println(f(nested(1)))
            }
            """);
        assertEquals(5, file.functions().size());
        var constructor = file.functions().stream().filter(f -> f.kind().equals("constructor")).findFirst().orElseThrow();
        assertEquals(2, constructor.line());
        assertEquals(4, constructor.endLine());
        assertEquals(5, constructor.parameters());
        assertEquals(2, constructor.complexity());
        var main = file.functions().stream().filter(f -> f.name().equals("main")).findFirst().orElseThrow();
        assertEquals(1, main.complexity());
        assertEquals(0, main.depth());
        assertEquals(2, main.statements());
        for (var f : file.functions()) {
            if (f.name().equals("nested") || f.kind().equals("lambda")) {
                assertEquals(2, f.complexity());
                assertEquals(3, f.statements());
                assertEquals(1, f.depth());
            }
        }
    }

    @Test void decisionsAndElseIfDepthHaveLiteralExpectations() {
        var f = measure("""
            Int choose(Int a) {
                if (a > 0 && a < 10 || a == 20) { return 1 }
                else if (a < 0) { while (a < 0) { a++ } }
                else { return 2 }
                for (var i = 0; i < 2; i++) { println(i) }
                try { println(a) } catch (String e) { println(e) }
                switch (a) { case 1: println(1); case 2: println(2); default: println(0) }
                return if (a > 0) 1 else 0
            }
            """).functions().getFirst();
        assertEquals(11, f.complexity());
        assertEquals(2, f.depth());
        assertEquals(17, f.statements());
    }

    @Test void expressionBodiesAndClosuresHaveAccurateEndLocations() {
        var file = measure("""
            Int twice(Int a) = a * 2
            main() {
                var f = (x: Int) -> twice(x + 1)
                println(f(2))
            }
            """);
        assertEquals(3, file.functions().size());
        var twice = file.functions().getFirst();
        assertEquals(1, twice.lines());
        assertEquals(1, twice.endLine());
        var lambda = file.functions().stream().filter(f -> f.kind().equals("lambda")).findFirst().orElseThrow();
        assertEquals(3, lambda.endLine());
    }

    @Test void multilineMethodHeadersAndExpressionMethodsIncludeDeclarations() {
        var file = measure("""
            class Box {
                public
                constructor(Int x) {
                    println(x)
                }
                private Int value(
                    Int a,
                    Int b
                ) {
                    return a + b
                }
                Int twice(Int a) = a * 2
            }
            """);
        var constructor = file.functions().get(0);
        assertEquals(2, constructor.line());
        assertEquals(5, constructor.endLine());
        var value = file.functions().get(1);
        assertEquals(6, value.line());
        assertEquals(6, value.lines());
        assertEquals(5, value.column());
        assertEquals(11, value.endLine());
        var twice = file.functions().get(2);
        assertEquals(12, twice.line());
        assertEquals(12, twice.endLine());
        assertEquals(1, twice.lines());
    }

    @Test void multilineReturnTypeBelongsToMethodSpanAndStrictSizeBoundary() {
        String body = "println(1)\n".repeat(22);
        var over = measure("class Box {\nInt\nvalue() {\n" + body + "return 1\n}\n}\n")
                .functions().getFirst();
        assertEquals(2, over.line());
        assertEquals(27, over.endLine());
        assertEquals(26, over.lines());
        assertTrue(Calibration.exceeds(over.lines(), 25));

        var at = measure("class Box {\nInt\nvalue() {\n" + body.replaceFirst("println\\(1\\)\\n", "")
                + "return 1\n}\n}\n").functions().getFirst();
        assertEquals(2, at.line());
        assertEquals(26, at.endLine());
        assertEquals(25, at.lines());
        assertFalse(Calibration.exceeds(at.lines(), 25));
    }

    @Test void namedAndExplicitConstructorsHaveIsolatedSpansAndParameterCounts() {
        var file = measure("class First {\nconstructor() {}\n}\n"
                + "class Second {\nconstructor(Int x) {}\n}\n"
                + "class Third {\nThird() {}\n}\n"
                + "class Fourth {\nFourth(Int x, Int y) {}\n}\n");
        assertEquals(2, file.functions().get(0).line());
        assertEquals(2, file.functions().get(0).endLine());
        assertEquals(0, file.functions().get(0).parameters());
        assertEquals(5, file.functions().get(1).line());
        assertEquals(5, file.functions().get(1).endLine());
        assertEquals(1, file.functions().get(1).parameters());
        assertEquals(8, file.functions().get(2).line());
        assertEquals(8, file.functions().get(2).endLine());
        assertEquals(0, file.functions().get(2).parameters());
        assertEquals(11, file.functions().get(3).line());
        assertEquals(11, file.functions().get(3).endLine());
        assertEquals(2, file.functions().get(3).parameters());
    }

    @Test void badSyntaxCannotProduceMetrics() {
        assertThrows(IllegalArgumentException.class, () -> measure("main() { var x = \"unterminated"));
        assertThrows(IllegalArgumentException.class, () -> measure("main() { if }"));
    }

    @Test void thresholdsAreStrictAndCalibrationAllowsNineteenNotTwenty() {
        assertFalse(Calibration.exceeds(25, 25));
        assertTrue(Calibration.exceeds(26, 25));
        assertEquals(25, Calibration.propose(List.of(26, 26, 26), 25));
        assertEquals(25, Calibration.propose(java.util.Collections.nCopies(19, 26), 25));
        assertEquals(26, Calibration.propose(java.util.Collections.nCopies(20, 26), 25));
        assertEquals(30, Calibration.propose(java.util.Collections.nCopies(20, 30), 25));
    }

    @Test void realCpdFindsFiftyTokensAndFiveLinesWithoutIdentifierNormalization() throws Exception {
        var source = """
            main() {
                var alpha = 101 + 102 + 103 + 104 + 105
                var beta = 201 + 202 + 203 + 204 + 205
                var gamma = 301 + 302 + 303 + 304 + 305
                var delta = 401 + 402 + 403 + 404 + 405
                println(alpha + beta + gamma + delta)
            }
            """;
        Files.writeString(root.resolve("A.kf"), source);
        Files.writeString(root.resolve("B.kf"), source);
        var found = Duplications.analyze(List.of(root.resolve("A.kf"), root.resolve("B.kf")));
        assertEquals(2, found.tokenized().size());
        assertTrue(found.failures().isEmpty());
        assertFalse(found.matches().isEmpty());
        assertTrue(found.matches().getFirst().tokens() >= 50);
        assertEquals(2, found.matches().getFirst().locations().size());
        assertTrue(found.matches().getFirst().locations().stream().allMatch(l -> l.endLine() - l.line() + 1 >= 5));
        Files.writeString(root.resolve("B.kf"), source.replace("alpha", "renamedAlpha").replace("beta", "renamedBeta")
                .replace("gamma", "renamedGamma").replace("delta", "renamedDelta"));
        assertTrue(Duplications.analyze(List.of(root.resolve("A.kf"), root.resolve("B.kf"))).matches().isEmpty());
        Files.writeString(root.resolve("B.kf"), source.replace('\n', ' '));
        assertTrue(Duplications.analyze(List.of(root.resolve("A.kf"), root.resolve("B.kf"))).matches().isEmpty());
        Files.writeString(root.resolve("A.kf"), "main() {\nprintln(1)\nprintln(2)\nprintln(3)\n}\n");
        Files.copy(root.resolve("A.kf"), root.resolve("C.kf"));
        assertTrue(Duplications.analyze(List.of(root.resolve("A.kf"), root.resolve("C.kf"))).matches().isEmpty());
    }

    @Test void cpdIncludesExactFiftyTokenFiveLineBoundary() throws Exception {
        String source = "main() {\n"
                + "println(101 + 102 + 103 + 104 + 105 + 106) println()\n"
                + "println(201 + 202 + 203 + 204 + 205 + 206)\n"
                + "println(301 + 302 + 303 + 304 + 305 + 306)\n}\n";
        assertEquals(50, measure(source).tokens());
        Files.writeString(root.resolve("A.kf"), source);
        Files.writeString(root.resolve("B.kf"), source);
        var matches = Duplications.analyze(List.of(root.resolve("A.kf"), root.resolve("B.kf"))).matches();
        assertEquals(1, matches.size());
        assertEquals(50, matches.getFirst().tokens());
        assertTrue(matches.getFirst().locations().stream().allMatch(l -> l.endLine() - l.line() + 1 == 5));
        String shortSource = source.replace("println()", "x++");
        assertEquals(49, measure(shortSource).tokens());
        Files.writeString(root.resolve("A.kf"), shortSource);
        Files.writeString(root.resolve("B.kf"), shortSource);
        assertTrue(Duplications.analyze(List.of(root.resolve("A.kf"), root.resolve("B.kf"))).matches().isEmpty());
        String fourLines = source.replace("println()\n", "println() ");
        assertEquals(50, measure(fourLines).tokens());
        Files.writeString(root.resolve("A.kf"), fourLines);
        Files.writeString(root.resolve("B.kf"), fourLines);
        assertTrue(Duplications.analyze(List.of(root.resolve("A.kf"), root.resolve("B.kf"))).matches().isEmpty());
    }

    @Test void multilineCommentsAndDelimiterStringsDoNotConfuseSpans() {
        var file = measure("main() {\n/* first\n second */\nprintln(\"}\")\n}\n");
        assertEquals(5, file.lines());
        assertEquals(3, file.functions().getFirst().lines());
        assertEquals(5, file.functions().getFirst().endLine());
        assertEquals(1, file.functions().getFirst().statements());
    }

    @Test void commandReconcilesScopeAndPreservesOnlyTwoSuiteExceptions() throws Exception {
        var production = root.resolve("src/main/kof");
        var suites = root.resolve("src/test/kof");
        Files.createDirectories(production);
        Files.createDirectories(suites);
        Files.writeString(production.resolve("Main.kf"), "main() {}\n");
        Files.writeString(suites.resolve("Suite.kf"), "test \"long suite\" {\n" + "println(1)\n".repeat(30) + "}\n");
        var output = root.resolve("report.json");
        var errors = root.resolve("stderr");
        var process = new ProcessBuilder(Path.of(System.getProperty("java.home"), "bin/java").toString(),
                "-cp", System.getProperty("java.class.path"), "sifuture.sensors.Main", root.toString())
                .redirectOutput(output.toFile()).redirectError(errors.toFile()).start();
        assertEquals(0, process.waitFor(), Files.readString(errors));
        var json = new com.fasterxml.jackson.databind.ObjectMapper().readTree(output.toFile());
        assertTrue(json.get("success").asBoolean());
        assertEquals(2, json.get("expected").size());
        assertEquals(2, json.get("cpd").get("result").get("tokenized").size());
        assertEquals(32, json.get("files").get(1).get("functions").get(0).get("lines").asInt());
        assertEquals(30, json.get("files").get(1).get("functions").get(0).get("statements").asInt());
        for (var metric : json.get("calibration")) {
            String name = metric.get("name").asText();
            int population = 0;
            for (var count : metric.get("distribution")) population += count.asInt();
            assertEquals(List.of("functionLines", "statements").contains(name) ? 1 : 2, population, name);
            assertEquals(0, metric.get("referenceFindings").asInt(), name);
        }
        Files.writeString(production.resolve("Main.kf"), "main() { println(\"unterminated }");
        var invalid = new ProcessBuilder(Path.of(System.getProperty("java.home"), "bin/java").toString(),
                "-cp", System.getProperty("java.class.path"), "sifuture.sensors.Main", root.toString())
                .redirectOutput(output.toFile()).redirectError(errors.toFile()).start();
        assertEquals(1, invalid.waitFor());
        var bad = new com.fasterxml.jackson.databind.ObjectMapper().readTree(output.toFile());
        assertFalse(bad.get("success").asBoolean());
        assertFalse(bad.get("failures").isEmpty());
        assertEquals(2, bad.get("cpd").get("result").get("expected").size());
        assertEquals(1, bad.get("cpd").get("result").get("tokenized").size());
    }

    @Test void tokenizationAndReadFailuresRemainVisible() throws Exception {
        Files.writeString(root.resolve("Bad.kf"), "main() { println(\"unterminated }");
        var result = Duplications.analyze(List.of(root.resolve("Bad.kf"), root.resolve("Missing.kf")));
        assertEquals(2, result.expected().size());
        assertEquals(0, result.tokenized().size());
        assertEquals(2, result.failures().size());
    }
}
