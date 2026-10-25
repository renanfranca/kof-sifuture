package sifuture.sensors;

import dev.kof.compiler.*;
import dev.kof.compiler.parser.Lexer;
import dev.kof.compiler.parser.Parser;
import java.lang.reflect.RecordComponent;
import java.util.*;

public final class Analyzer {
    public record FunctionMetrics(String name, String kind, int line, int column, int endLine,
                                  int lines, int complexity, int parameters, int depth, int statements) {}
    public record FileMetrics(String file, int lines, int tokens, List<FunctionMetrics> functions) {}
    record Callable(AstNode node, String name, String kind, List<?> parameters, List<?> body) {}

    static List<Token> tokens(String file, String source) {
        var diagnostics = new DiagnosticCollector();
        var tokens = new Lexer(source, file, diagnostics).tokenize();
        requireClean(diagnostics);
        return tokens;
    }

    static void requireClean(DiagnosticCollector diagnostics) {
        if (diagnostics.getDiagnostics().stream().anyMatch(d -> d.severity() == Diagnostic.Severity.ERROR)) {
            throw new IllegalArgumentException(diagnostics.getDiagnostics().toString());
        }
    }

    public static FileMetrics measure(String file, String source) {
        var tokens = tokens(file, source);
        var diagnostics = new DiagnosticCollector();
        var unit = new Parser(new ArrayList<>(tokens), diagnostics, file).parse();
        requireClean(diagnostics);
        var functions = new ArrayList<FunctionMetrics>();
        collect(unit, tokens, source, functions);
        functions.sort(Comparator.comparingInt(FunctionMetrics::line).thenComparingInt(FunctionMetrics::column));
        return new FileMetrics(file, (int) source.lines().filter(l -> !l.isBlank()).count(),
                tokens.size() - 1, List.copyOf(functions));
    }

    static Callable callable(Object node) {
        return switch (node) {
            case null -> null;
            case FunctionDeclarationNode f -> new Callable(f, f.name(), "function", f.parameters(), f.body());
            case MethodDeclarationNode f -> new Callable(f, f.name(), "method", f.parameters(), f.body());
            case ConstructorDeclarationNode f -> new Callable(f, f.name(), "constructor", f.parameters(), f.body());
            case LambdaExpr f -> new Callable(f, "lambda", "lambda", f.parameters(), f.body());
            case TestDeclarationNode f -> new Callable(f, f.name(), "test", List.of(), f.body());
            default -> null;
        };
    }

    static List<Object> children(Object object) {
        if (object instanceof List<?> values) return new ArrayList<>(values);
        if (!(object instanceof AstNode) || !object.getClass().isRecord()) return List.of();
        var result = new ArrayList<Object>();
        for (RecordComponent component : object.getClass().getRecordComponents()) {
            if (component.getName().equals("position")) continue;
            try {
                var value = component.getAccessor().invoke(object);
                if (value instanceof AstNode || value instanceof List<?>) result.add(value);
            } catch (ReflectiveOperationException exc) {
                throw new IllegalStateException("Cannot traverse official AST", exc);
            }
        }
        return result;
    }

    static void collect(Object object, List<Token> tokens, String source, List<FunctionMetrics> result) {
        var function = callable(object);
        if (function != null) {
            var span = Spans.callable(function, tokens);
            var first = tokens.get(span[0]);
            var last = tokens.get(span[1]);
            var lines = new HashSet<Integer>();
            for (int i = span[0]; i <= span[1]; i++) {
                var token = tokens.get(i);
                int end = token.line() + (int) source.substring(token.offset(), token.offset() + token.length())
                        .chars().filter(c -> c == '\n').count();
                for (int line = token.line(); line <= end; line++) lines.add(line);
            }
            var counts = new Counts();
            count(function.body(), 0, counts);
            result.add(new FunctionMetrics(function.name(), function.kind(), first.line(), first.column(), last.line(),
                    lines.size(), counts.complexity, function.parameters().size(), counts.depth, counts.statements));
        }
        for (var child : children(object)) collect(child, tokens, source, result);
    }

    static final class Counts {
        int complexity = 1;
        int depth;
        int statements;
    }

    static void count(Object node, int level, Counts counts) {
        if (callable(node) != null || node instanceof FunctionDeclStmt) return;
        if (node instanceof StatementNode && !(node instanceof BlockStmt)) counts.statements++;
        if (node instanceof IfStmt || node instanceof IfExpr || node instanceof ForStmt
                || node instanceof ForInStmt || node instanceof WhileStmt || node instanceof DoWhileStmt
                || node instanceof CatchClause || node instanceof SwitchCase || node instanceof SwitchExprCase) {
            counts.complexity++;
        }
        if (node instanceof BinaryExpr binary && Set.of("&&", "||").contains(binary.operator())) counts.complexity++;
        if (node instanceof IfStmt conditional) {
            counts.depth = Math.max(counts.depth, level + 1);
            count(conditional.condition(), level, counts);
            count(conditional.thenBranch(), level + 1, counts);
            count(conditional.elseBranch(), conditional.elseBranch() instanceof IfStmt ? level : level + 1, counts);
            return;
        }
        boolean control = node instanceof IfExpr || node instanceof ForStmt || node instanceof ForInStmt
                || node instanceof WhileStmt || node instanceof DoWhileStmt || node instanceof SwitchStmt
                || node instanceof SwitchExpr || node instanceof TryStmt;
        int next = level + (control ? 1 : 0);
        if (control) counts.depth = Math.max(counts.depth, next);
        for (var child : children(node)) count(child, next, counts);
    }
}
