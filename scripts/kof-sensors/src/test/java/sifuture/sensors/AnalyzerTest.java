package sifuture.sensors;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.concurrent.TimeUnit;
import static org.junit.jupiter.api.Assertions.*;

class AnalyzerTest {
    @TempDir Path root;

    Analyzer.FileMetrics measure(String source) {
        return Analyzer.measure("Probe.kf", source);
    }

    void checkWithOfficialCompiler(String source, String target) throws Exception {
        var sourceFile = root.resolve("Probe.kf");
        Files.writeString(sourceFile, source);
        var executable = System.getenv().getOrDefault("KOF", "kof");
        var reportFile = root.resolve("check-" + target + ".json");
        var process = new ProcessBuilder(executable, "check", sourceFile.toString(), "--target", target, "--json")
                .redirectErrorStream(true).redirectOutput(reportFile.toFile()).start();
        if (!process.waitFor(60, TimeUnit.SECONDS)) {
            process.destroyForcibly();
            fail("Kof check timed out for " + target);
        }
        var output = Files.readString(reportFile);
        var report = new ObjectMapper().readTree(output);
        assertEquals(0, process.exitValue(), output);
        assertTrue(report.path("success").asBoolean(false), output);
        assertEquals(0, report.path("errorCount").asInt(-1), output);
        assertTrue(report.path("filesChecked").asInt(0) > 0, output);
        assertTrue(report.path("diagnostics").isArray(), output);
        for (var diagnostic : report.path("diagnostics")) {
            assertNotEquals("ERROR", diagnostic.path("severity").asText(), output);
        }
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

    @Test void compoundReturnTypesLocateTwelveDeclarationShapes() {
        for (String type : List.of("Int", "List<Int>", "Int[]")) {
            for (boolean afterParameters : List.of(false, true)) {
                for (boolean multiline : List.of(false, true)) {
                    String declaration = switch (type) {
                        case "Int" -> "return 1";
                        case "List<Int>" -> "return listOf(1)";
                        case "Int[]" -> "return new Int[1]";
                        default -> throw new IllegalStateException(type);
                    };
                    String header = afterParameters
                            ? (multiline ? "value()\n: " + type : "value(): " + type)
                            : (multiline ? type + "\nvalue()" : type + " value()");
                    String source = "class Box {\n" + header + " { " + declaration + " }\n}\n";
                    String context = type + ", after=" + afterParameters + ", multiline=" + multiline;
                    assertAll(context, () -> {
                        var function = measure(source).functions().getFirst();
                        assertEquals(2, function.line());
                        assertEquals(multiline ? 3 : 2, function.endLine());
                        assertEquals(multiline ? 2 : 1, function.lines());
                        assertEquals(1, function.complexity());
                        assertEquals(0, function.parameters());
                        assertEquals(0, function.depth());
                        assertEquals(1, function.statements());
                    });
                }
            }
        }
    }

    @Test void constructorCallToItsClassDoesNotBecomeTheDeclarationStart() {
        var file = measure("class Box {\n"
                + "    constructor(Int depth) {\n"
                + "        if (depth > 0) { var child = new Box(depth - 1) }\n"
                + "    }\n"
                + "}\n"
                + "main() { var box = new Box(1) }\n");
        var constructor = file.functions().stream().filter(f -> f.kind().equals("constructor")).findFirst().orElseThrow();
        assertEquals(2, constructor.line());
        assertEquals(5, constructor.column());
        assertEquals(4, constructor.endLine());
        assertEquals(3, constructor.lines());
        assertEquals(1, constructor.parameters());
        assertEquals(2, constructor.complexity());
        assertEquals(1, constructor.depth());
        assertEquals(2, constructor.statements());
        var main = file.functions().stream().filter(f -> f.name().equals("main")).findFirst().orElseThrow();
        assertEquals(6, main.line());
        assertEquals(6, main.endLine());
        assertEquals(1, main.lines());
    }

    @Test void namedConstructorCallToItsClassDoesNotBecomeTheDeclarationStart() {
        var constructor = measure("class Box {\n"
                + "    Box(Int depth) {\n"
                + "        if (depth > 0) { var child = new Box(depth - 1) }\n"
                + "    }\n"
                + "}\n").functions().getFirst();
        assertEquals(2, constructor.line());
        assertEquals(5, constructor.column());
        assertEquals(4, constructor.endLine());
        assertEquals(3, constructor.lines());
        assertEquals(1, constructor.parameters());
        assertEquals(2, constructor.complexity());
        assertEquals(1, constructor.depth());
        assertEquals(2, constructor.statements());
    }

    @Test void overloadedConstructorsRemainAssociatedWithTheirOwnParametersAndBodies() {
        var constructors = measure("class Box {\n"
                + "    constructor() {}\n"
                + "    constructor(Int depth) { if (depth > 0) { var child = new Box() } }\n"
                + "}\n").functions().stream().filter(f -> f.kind().equals("constructor")).toList();
        assertEquals(2, constructors.size());
        assertEquals(2, constructors.get(0).line());
        assertEquals(2, constructors.get(0).endLine());
        assertEquals(0, constructors.get(0).parameters());
        assertEquals(3, constructors.get(1).line());
        assertEquals(5, constructors.get(1).column());
        assertEquals(3, constructors.get(1).endLine());
        assertEquals(1, constructors.get(1).parameters());
        assertEquals(2, constructors.get(1).complexity());
        assertEquals(1, constructors.get(1).depth());
        assertEquals(2, constructors.get(1).statements());
    }

    @Test void zeroParameterConstructorsStayAssociatedWithTheirOwnBodies() {
        for (String declaration : List.of("constructor()", "Box()")) {
            for (String call : List.of("new Box()", "new Box(1)")) {
                var source = "class Box {\n"
                        + "    " + declaration + " {\n"
                        + "        var child = " + call + "\n"
                        + "        if (true) { println(child) }\n"
                        + "    }\n"
                        + "    constructor(Int value) {}\n"
                        + "}\n"
                        + "main() { var box = new Box() }\n";
                var file = measure(source);
                assertEquals(3, file.functions().size(), declaration + " / " + call);
                var constructor = file.functions().stream().filter(f -> f.kind().equals("constructor"))
                        .filter(f -> f.parameters() == 0).findFirst().orElseThrow();
                assertEquals(2, constructor.line(), declaration + " / " + call);
                assertEquals(5, constructor.column(), declaration + " / " + call);
                assertEquals(5, constructor.endLine(), declaration + " / " + call);
                assertEquals(4, constructor.lines(), declaration + " / " + call);
                assertEquals(2, constructor.complexity(), declaration + " / " + call);
                assertEquals(1, constructor.depth(), declaration + " / " + call);
                assertEquals(3, constructor.statements(), declaration + " / " + call);
                var auxiliary = file.functions().stream().filter(f -> f.kind().equals("constructor"))
                        .filter(f -> f.parameters() == 1).findFirst().orElseThrow();
                assertEquals(6, auxiliary.line());
                assertEquals(5, auxiliary.column());
                assertEquals(6, auxiliary.endLine());
                assertEquals(1, auxiliary.lines());
                var main = file.functions().stream().filter(f -> f.name().equals("main")).findFirst().orElseThrow();
                assertEquals(8, main.line());
                assertEquals(1, main.column());
                assertEquals(8, main.endLine());
                assertEquals(1, main.lines());
            }
        }
    }

    @Test void zeroParameterConstructorSpanMatrixCoversBodiesAndDeclarationStyles() {
        for (String declaration : List.of("constructor()", "Box()")) {
            for (String body : List.of("{}", "{\n        println(1)\n    }",
                    "{\n        var child = new Box()\n        if (true) { println(child) }\n    }")) {
                var constructor = measure("class Box {\n    " + declaration + " " + body + "\n}\n")
                        .functions().getFirst();
                assertEquals(2, constructor.line(), declaration + " / " + body);
                assertEquals(5, constructor.column(), declaration + " / " + body);
                assertEquals(body.equals("{}") ? 2 : body.startsWith("{\n        println") ? 4 : 5,
                        constructor.endLine(), declaration + " / " + body);
                assertEquals(body.equals("{}") ? 1 : body.startsWith("{\n        println") ? 3 : 4,
                        constructor.lines(), declaration + " / " + body);
                assertEquals(0, constructor.parameters());
                assertEquals(body.startsWith("{\n        var") ? 2 : 1, constructor.complexity());
                assertEquals(body.startsWith("{\n        var") ? 1 : 0, constructor.depth());
                assertEquals(body.equals("{}") ? 0 : body.startsWith("{\n        println") ? 1 : 3,
                        constructor.statements());
            }
        }
    }

    @Test void constructorSpanMatrixCoversParameterCountsDeclarationStylesAndBodies() throws Exception {
        for (String declaration : List.of("constructor", "Box")) {
            for (boolean parameterized : List.of(false, true)) {
                for (int bodyShape = 0; bodyShape < 3; bodyShape++) {
                    String signature = declaration + (parameterized ? "(Int value)" : "()");
                    String body = switch (bodyShape) {
                        case 0 -> "{}";
                        case 1 -> "{\n        println(1)\n    }";
                        default -> "{\n        var child = new Box(" + (parameterized ? "value" : "")
                                + ")\n        if (true) { println(child) }\n    }";
                    };
                    String source = "class Box {\n    " + signature + " " + body + "\n}\n";
                    String context = declaration + ", parameterized=" + parameterized + ", body=" + bodyShape;
                    int expectedEndLine = bodyShape == 0 ? 2 : bodyShape == 1 ? 4 : 5;
                    int expectedLines = bodyShape == 0 ? 1 : bodyShape == 1 ? 3 : 4;
                    int expectedComplexity = bodyShape == 2 ? 2 : 1;
                    int expectedDepth = bodyShape == 2 ? 1 : 0;
                    int expectedStatements = bodyShape == 0 ? 0 : bodyShape == 1 ? 1 : 3;
                    assertAll(context, () -> {
                        checkWithOfficialCompiler(source, "jvm");
                        checkWithOfficialCompiler(source, "js");
                        var constructor = measure(source).functions().getFirst();
                        assertEquals(2, constructor.line());
                        assertEquals(5, constructor.column());
                        assertEquals(expectedEndLine, constructor.endLine());
                        assertEquals(expectedLines, constructor.lines());
                        assertEquals(parameterized ? 1 : 0, constructor.parameters());
                        assertEquals(expectedComplexity, constructor.complexity());
                        assertEquals(expectedDepth, constructor.depth());
                        assertEquals(expectedStatements, constructor.statements());
                    });
                }
            }
        }
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
