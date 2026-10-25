package sifuture.sensors;

import dev.kof.compiler.TokenType;
import net.sourceforge.pmd.cpd.*;
import net.sourceforge.pmd.lang.*;
import java.nio.file.*;
import java.util.*;

public final class Duplications {
    public record Location(String file, int line, int column, int endLine, int endColumn) {}
    public record Clone(int tokens, List<Location> locations) {}
    public record Result(List<String> expected, List<String> tokenized, List<String> failures, List<Clone> matches) {}

    static final class KofLanguage extends LanguageModuleBase implements CpdCapableLanguage {
        KofLanguage() {
            super(LanguageMetadata.withId("kof").name("Kof").extensions("kf").addDefaultVersion("0.6.6"));
        }

        @Override public CpdLexer createCpdLexer(LanguagePropertyBundle bundle) {
            return (document, sink) -> {
                String text = document.getText().toString();
                var tokens = Analyzer.tokens(document.getFileId().getAbsolutePath(), text);
                for (var token : tokens) {
                    if (token.type() == TokenType.EOF) continue;
                    String raw = text.substring(token.offset(), token.offset() + token.length());
                    int endLine = token.line();
                    int endColumn = token.column();
                    for (int i = 0; i < raw.length(); i++) {
                        if (raw.charAt(i) == '\n') { endLine++; endColumn = 1; }
                        else endColumn++;
                    }
                    sink.recordToken(token.type().name() + ":" + raw, token.line(), token.column(), endLine, endColumn);
                }
            };
        }
    }

    public static Result analyze(List<Path> paths) throws Exception {
        var language = new KofLanguage();
        var config = new CPDConfiguration(LanguageRegistry.singleton(language));
        config.setOnlyRecognizeLanguage(language);
        config.setMinimumTileSize(50);
        config.setSkipDuplicates(false);
        var expected = paths.stream().map(p -> p.toAbsolutePath().normalize().toString()).toList();
        var tokenized = new ArrayList<String>();
        var failures = new ArrayList<String>();
        var matches = new ArrayList<Clone>();
        try (var analysis = CpdAnalysis.create(config)) {
            for (var path : paths) {
                try {
                    Analyzer.tokens(path.toString(), Files.readString(path));
                    if (!analysis.files().addFile(path, language)) throw new IllegalArgumentException("CPD refused file");
                } catch (Exception exc) {
                    failures.add(path + ": " + exc.getMessage());
                }
            }
            analysis.performAnalysis(report -> {
                report.getNumberOfTokensPerFile().keySet().forEach(id -> tokenized.add(id.getAbsolutePath()));
                report.getProcessingErrors().forEach(error -> failures.add(error.toString()));
                for (var match : report.getMatches()) {
                    var locations = new ArrayList<Location>();
                    for (var mark : match) {
                        var location = mark.getLocation();
                        if (location.getLineCount() >= 5) locations.add(new Location(location.getFileId().getAbsolutePath(),
                                location.getStartLine(), location.getStartColumn(), location.getEndLine(), location.getEndColumn()));
                    }
                    if (locations.size() >= 2) matches.add(new Clone(match.getTokenCount(), List.copyOf(locations)));
                }
            });
        }
        Collections.sort(tokenized);
        for (var path : expected) {
            if (!tokenized.contains(path) && failures.stream().noneMatch(f -> f.startsWith(path))) {
                failures.add(path + ": expected file was not tokenized");
            }
        }
        return new Result(expected, List.copyOf(tokenized), List.copyOf(failures), List.copyOf(matches));
    }
}
