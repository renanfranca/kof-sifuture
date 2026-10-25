package sifuture.sensors;

import com.fasterxml.jackson.databind.ObjectMapper;
import dev.kof.compiler.parser.Lexer;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;
import java.util.function.ToIntFunction;

public final class Main {
    record Finding(String file, String name, int line, int value) {}
    record Metric(String name, int reference, int proposed, int referenceFindings, int proposedFindings,
                  int previousFindings, SortedMap<Integer, Long> distribution,
                  List<Finding> affectedAtReference, List<Finding> affectedAtProposed) {}

    static Metric metric(String name, int reference, List<Finding> values) {
        var integers = values.stream().map(Finding::value).toList();
        int proposed = Calibration.propose(integers, reference);
        var distribution = new TreeMap<Integer, Long>();
        integers.forEach(value -> distribution.merge(value, 1L, Long::sum));
        var atReference = values.stream().filter(v -> Calibration.exceeds(v.value(), reference)).toList();
        var atProposed = values.stream().filter(v -> Calibration.exceeds(v.value(), proposed)).toList();
        return new Metric(name, reference, proposed, atReference.size(), atProposed.size(),
                (int) integers.stream().filter(v -> Calibration.exceeds(v, proposed - 1)).count(),
                distribution, atReference, atProposed);
    }

    static Metric functions(String name, int reference, List<Analyzer.FileMetrics> files,
                            ToIntFunction<Analyzer.FunctionMetrics> value, boolean exemptSuites) {
        var values = new ArrayList<Finding>();
        for (var file : files) {
            if (exemptSuites && file.file().startsWith("src/test/kof/")) continue;
            for (var function : file.functions()) values.add(new Finding(file.file(), function.name(), function.line(), value.applyAsInt(function)));
        }
        return metric(name, reference, values);
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
                functions("functionLines", 25, inventory, Analyzer.FunctionMetrics::lines, true),
                functions("complexity", 5, inventory, Analyzer.FunctionMetrics::complexity, false),
                functions("parameters", 4, inventory, Analyzer.FunctionMetrics::parameters, false),
                functions("depth", 2, inventory, Analyzer.FunctionMetrics::depth, false),
                functions("statements", 15, inventory, Analyzer.FunctionMetrics::statements, true));
        Path jar = Path.of(Lexer.class.getProtectionDomain().getCodeSource().getLocation().toURI()).toRealPath();
        var report = new LinkedHashMap<String, Object>();
        report.put("schemaVersion", 1);
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
