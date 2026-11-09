package sifuture.sensors;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.nio.file.*;
import java.util.*;
import java.util.function.ToIntFunction;

public final class Findings {
    @JsonInclude(JsonInclude.Include.NON_NULL)
    public record Finding(String rule, String file, String name, int line, int column, Integer value, Integer limit) {}
    public record Duplication(int minimumTokens, int minimumLines, List<String> expected, List<String> tokenized,
                              List<String> failures, List<Duplications.Clone> clones) {}
    record FunctionLimit(String rule, int limit, boolean suitesExempt, ToIntFunction<Analyzer.FunctionMetrics> value) {}

    static final List<FunctionLimit> FUNCTION_LIMITS = List.of(
            new FunctionLimit("long-function", 25, true, Analyzer.FunctionMetrics::lines),
            new FunctionLimit("high-complexity", 10, false, Analyzer.FunctionMetrics::complexity),
            new FunctionLimit("too-many-parameters", 4, false, Analyzer.FunctionMetrics::parameters),
            new FunctionLimit("deep-nesting", 2, false, Analyzer.FunctionMetrics::depth),
            new FunctionLimit("too-many-statements", 17, true, Analyzer.FunctionMetrics::statements));

    static final int FILE_LINES = 150;
    static final int TEST_CODE_FILE_LINES = 1000;
    static final List<String> TEST_CODE = List.of(Main.SUITE_SOURCES, "tests/");

    static boolean testCode(String file) {
        return TEST_CODE.stream().anyMatch(file::startsWith);
    }

    static List<Finding> structural(Analyzer.FileMetrics file) {
        boolean suite = file.file().startsWith(Main.SUITE_SOURCES);
        var found = new ArrayList<Finding>();
        int fileLines = testCode(file.file()) ? TEST_CODE_FILE_LINES : FILE_LINES;
        if (Calibration.exceeds(file.lines(), fileLines)) {
            found.add(new Finding("long-file", file.file(), "file", 1, 1, file.lines(), fileLines));
        }
        for (var function : file.functions()) {
            for (var limit : FUNCTION_LIMITS) {
                if (suite && limit.suitesExempt()) continue;
                int value = limit.value().applyAsInt(function);
                if (Calibration.exceeds(value, limit.limit())) {
                    found.add(new Finding(limit.rule(), file.file(), function.name(), function.line(), function.column(), value, limit.limit()));
                }
            }
        }
        return found;
    }

    static Duplication duplication(Path root, List<Path> paths) throws Exception {
        var result = Duplications.analyze(paths);
        var clones = result.matches().stream().map(clone -> new Duplications.Clone(clone.tokens(), clone.locations().stream()
                .map(l -> new Duplications.Location(relative(root, l.file()), l.line(), l.column(), l.endLine(), l.endColumn()))
                .toList())).toList();
        return new Duplication(50, 5, result.expected().stream().map(f -> relative(root, f)).toList(),
                result.tokenized().stream().map(f -> relative(root, f)).toList(), result.failures(), clones);
    }

    static String relative(Path root, String file) {
        return root.relativize(Path.of(file)).toString().replace('\\', '/');
    }

    static void run(List<String> args) throws Exception {
        Path root = Path.of(args.getFirst()).toRealPath();
        var expected = new ArrayList<String>();
        var failures = new ArrayList<String>();
        var findings = new ArrayList<Finding>();
        var paths = new ArrayList<Path>();
        for (var argument : args.subList(1, args.size())) {
            Path path = root.resolve(argument).normalize();
            String relative = root.relativize(path).toString().replace('\\', '/');
            expected.add(relative);
            if (!testCode(relative)) paths.add(path);
            try {
                String source = Files.readString(path);
                var parsed = Analyzer.parse(relative, source);
                findings.addAll(structural(Analyzer.measure(relative, source, parsed)));
                findings.addAll(TestRules.findings(relative, parsed));
                findings.addAll(CommentRules.findings(root, relative, source, parsed));
            } catch (Exception exc) {
                failures.add(relative + ": " + exc.getMessage());
            }
        }
        var duplication = duplication(root, paths);
        var report = new LinkedHashMap<String, Object>();
        report.put("schemaVersion", 1);
        report.put("success", failures.isEmpty() && duplication.failures().isEmpty());
        report.put("frontend", Main.frontend());
        report.put("root", root.toString());
        report.put("expected", expected);
        report.put("failures", failures);
        report.put("findings", findings);
        report.put("duplication", duplication);
        new ObjectMapper().writerWithDefaultPrettyPrinter().writeValue(System.out, report);
        if (!failures.isEmpty()) System.exit(1);
    }
}
