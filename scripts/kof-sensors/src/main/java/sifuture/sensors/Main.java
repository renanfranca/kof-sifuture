package sifuture.sensors;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.databind.ObjectMapper;
import dev.kof.compiler.parser.Lexer;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;
import java.util.function.ToIntFunction;

public final class Main {
    record Finding(String file, String name, int line, int value) {}
    @JsonInclude(JsonInclude.Include.NON_NULL)
    record Metric(String name, String calibratedOn, int reference, int proposed, int referenceFindings,
                  int proposedFindings, int previousFindings, SortedMap<Integer, Long> distribution,
                  List<Finding> affectedAtReference, List<Finding> affectedAtProposed,
                  Integer suiteFindingsAtReference, Integer suiteFindingsAtProposed,
                  List<Finding> suiteAffectedAtProposed, SortedMap<Integer, Long> suiteDistribution) {
        Metric measuringSuitesAgainstProposed(List<Finding> suites) {
            var suitesAtProposed = exceeding(suites, proposed);
            return new Metric(name, PRODUCTION_SOURCES, reference, proposed, referenceFindings, proposedFindings,
                    previousFindings, distribution, affectedAtReference, affectedAtProposed,
                    exceeding(suites, reference).size(), suitesAtProposed.size(), suitesAtProposed, distributionOf(suites));
        }
    }
    enum SuitePolicy { EXEMPT, MEASURED }

    static final String PRODUCTION_SOURCES = "src/main/kof";
    static final String SUITE_SOURCES = "src/test/kof/";

    static List<Finding> exceeding(List<Finding> values, int limit) {
        return values.stream().filter(v -> Calibration.exceeds(v.value(), limit)).toList();
    }

    static SortedMap<Integer, Long> distributionOf(List<Finding> values) {
        var distribution = new TreeMap<Integer, Long>();
        values.forEach(value -> distribution.merge(value.value(), 1L, Long::sum));
        return distribution;
    }

    static Metric metric(String name, int reference, List<Finding> values) {
        int proposed = Calibration.propose(values.stream().map(Finding::value).toList(), reference);
        var atReference = exceeding(values, reference);
        var atProposed = exceeding(values, proposed);
        return new Metric(name, null, reference, proposed, atReference.size(), atProposed.size(),
                exceeding(values, proposed - 1).size(), distributionOf(values), atReference, atProposed,
                null, null, null, null);
    }

    static List<Finding> functionFindings(List<Analyzer.FileMetrics> files, ToIntFunction<Analyzer.FunctionMetrics> value,
                                          boolean suites) {
        var values = new ArrayList<Finding>();
        for (var file : files) {
            if (file.file().startsWith(SUITE_SOURCES) != suites) continue;
            for (var function : file.functions()) values.add(new Finding(file.file(), function.name(), function.line(), value.applyAsInt(function)));
        }
        return values;
    }

    static Metric functions(String name, int reference, List<Analyzer.FileMetrics> files,
                            ToIntFunction<Analyzer.FunctionMetrics> value, SuitePolicy suitePolicy) {
        var production = metric(name, reference, functionFindings(files, value, false));
        return switch (suitePolicy) {
            case EXEMPT -> production;
            case MEASURED -> production.measuringSuitesAgainstProposed(functionFindings(files, value, true));
        };
    }

    public static void main(String[] args) throws Exception {
        Path root = Path.of(args.length == 0 ? "." : args[0]).toRealPath();
        var paths = new TreeSet<Path>();
        var failures = new ArrayList<String>();
        var scopes = args.length > 1 ? Arrays.asList(args).subList(1, args.length) : List.of("src/main/kof", "src/test/kof");
        for (var scope : scopes) {
            Path path = root.resolve(scope).normalize();
            try {
                if (Files.isDirectory(path)) {
                    try (var stream = Files.walk(path)) {
                        var found = stream.filter(p -> p.toString().endsWith(".kf")).toList();
                        if (found.isEmpty()) failures.add(path + ": no Kof files");
                        paths.addAll(found);
                    }
                } else if (path.toString().endsWith(".kf")) paths.add(path);
                else failures.add(path + ": expected Kof source or directory");
            } catch (Exception exc) { failures.add(path + ": " + exc.getMessage()); }
        }
        var inventory = new ArrayList<Analyzer.FileMetrics>();
        for (var path : paths) {
            try { inventory.add(Analyzer.measure(root.relativize(path).toString().replace('\\', '/'), Files.readString(path))); }
            catch (Exception exc) { failures.add(path + ": " + exc.getMessage()); }
        }
        var duplication = Duplications.analyze(new ArrayList<>(paths));
        failures.addAll(duplication.failures());
        if (paths.isEmpty()) failures.add("No expected source files");
        var metrics = List.of(
                metric("fileLines", 150, inventory.stream().map(f -> new Finding(f.file(), "file", 1, f.lines())).toList()),
                functions("functionLines", 25, inventory, Analyzer.FunctionMetrics::lines, SuitePolicy.EXEMPT),
                functions("complexity", 5, inventory, Analyzer.FunctionMetrics::complexity, SuitePolicy.MEASURED),
                functions("parameters", 4, inventory, Analyzer.FunctionMetrics::parameters, SuitePolicy.MEASURED),
                functions("depth", 2, inventory, Analyzer.FunctionMetrics::depth, SuitePolicy.MEASURED),
                functions("statements", 15, inventory, Analyzer.FunctionMetrics::statements, SuitePolicy.EXEMPT));
        Path jar = Path.of(Lexer.class.getProtectionDomain().getCodeSource().getLocation().toURI()).toRealPath();
        var report = new LinkedHashMap<String, Object>();
        report.put("schemaVersion", 2);
        report.put("success", failures.isEmpty());
        report.put("frontend", Map.of("jar", jar.toString(), "sha256", HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(Files.readAllBytes(jar))),
                "version", System.getProperty("kof.version", "unrecorded")));
        report.put("scope", scopes);
        report.put("expected", paths.stream().map(Path::toString).toList());
        report.put("files", inventory);
        report.put("failures", failures);
        report.put("calibration", metrics);
        report.put("cpd", Map.of("version", "7.17.0", "minimumTokens", 50, "minimumLines", 5, "result", duplication));
        new ObjectMapper().writerWithDefaultPrettyPrinter().writeValue(System.out, report);
        if (!failures.isEmpty()) System.exit(1);
    }
}
