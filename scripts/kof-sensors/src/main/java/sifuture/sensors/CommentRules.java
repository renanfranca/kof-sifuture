package sifuture.sensors;

import dev.kof.compiler.*;
import dev.kof.compiler.parser.Parser;
import java.nio.file.*;
import java.util.*;
import java.util.regex.Pattern;

final class CommentRules {
    record Comment(boolean line, String text, int startLine, int endLine, int column) {}
    record Block(List<Comment> comments) {
        int startLine() { return comments.getFirst().startLine(); }
        int column() { return comments.getFirst().column(); }
        int height() { return comments.getLast().endLine() - startLine() + 1; }
        String text() { return String.join("\n", comments.stream().map(Comment::text).toList()); }
    }

    static final Pattern DEFERRED = Pattern.compile("\\b(todo|fixme|xxx|hack)\\b", Pattern.CASE_INSENSITIVE);

    static final Pattern BACKTICKED = Pattern.compile("`([^`\\n]+)`");
    static final Pattern IDENTIFIER = Pattern.compile("^[A-Za-z_$][\\w$]*(\\(\\))?$");
    static final Pattern CAMEL_OR_SNAKE = Pattern.compile("[a-z][A-Z]|_");
    static final Pattern PATHLIKE = Pattern.compile("^[\\w.@/-]+/[\\w.@/-]+$");

    static List<Findings.Finding> findings(Path root, String file, String source, Analyzer.Parsed parsed) {
        var found = new ArrayList<Findings.Finding>();
        var comments = comments(source, parsed.tokens());
        var known = new HashSet<String>();
        parsed.tokens().stream().filter(t -> t.type() == TokenType.IDENTIFIER).forEach(t -> known.add(t.value()));
        for (var comment : comments) {
            var references = BACKTICKED.matcher(comment.text());
            while (references.find()) {
                String reference = references.group(1).trim();
                if (stale(reference, known, root, file)) {
                    found.add(new Findings.Finding("stale-comment", file, reference, comment.startLine(), comment.column(), null, null));
                }
            }
        }
        for (var comment : comments) {
            if (looksLikeCode(comment.text())) {
                found.add(new Findings.Finding("commented-out-code", file, "comment", comment.startLine(), comment.column(), null, null));
            }
            var deferred = DEFERRED.matcher(comment.text());
            if (deferred.find()) {
                found.add(new Findings.Finding("deferred-work", file, deferred.group(), comment.startLine(), comment.column(), null, null));
            }
        }
        for (var block : blocks(comments)) {
            if (block.height() > 1) {
                found.add(new Findings.Finding("long-comment", file, "comment", block.startLine(), block.column(), block.height(), 1));
            }
        }
        return found;
    }

    static boolean looksLikeCode(String raw) {
        String text = raw.trim();
        if (text.length() < 6) return false;
        var wrapped = parsedOrNull("main() {\n" + text + "\n}\n");
        if (wrapped != null && wrapped.declarations().getFirst() instanceof FunctionDeclarationNode main
                && !main.body().isEmpty() && main.body().stream().allMatch(CommentRules::isCode)) return true;
        var declarations = parsedOrNull(text + "\n");
        return declarations != null && !declarations.declarations().isEmpty();
    }

    static CompilationUnitNode parsedOrNull(String source) {
        try {
            return Analyzer.parse("comment.kf", source).unit();
        } catch (RuntimeException exc) {
            return null;
        }
    }

    static boolean isCode(StatementNode statement) {
        return switch (statement) {
            case VarDeclStmt declaration -> declaration.initializer() != null;
            case ExpressionStmt expression -> expression.expression() instanceof MethodCallExpr
                    || expression.expression() instanceof AssignmentExpr || expression.expression() instanceof BinaryExpr
                    || expression.expression() instanceof NewExpr || expression.expression() instanceof UnaryExpr;
            case ReturnStmt returned -> !(returned.value() instanceof IdentifierExpr);
            case ThrowStmt thrown -> !(thrown.expression() instanceof IdentifierExpr);
            case BlockStmt block -> false;
            default -> true;
        };
    }

    static boolean stale(String reference, Set<String> known, Path root, String file) {
        if (PATHLIKE.matcher(reference).matches()) {
            Path beside = root.resolve(file).getParent().resolve(reference);
            return !Files.exists(beside) && !Files.exists(root.resolve(reference));
        }
        if (!IDENTIFIER.matcher(reference).matches()) return false;
        if (!reference.endsWith("()") && !CAMEL_OR_SNAKE.matcher(reference).find()) return false;
        return !known.contains(reference.replaceAll("\\(\\)$", ""));
    }

    static List<Block> blocks(List<Comment> comments) {
        var blocks = new ArrayList<Block>();
        var current = new ArrayList<Comment>();
        for (var comment : comments) {
            if (!current.isEmpty() && !continues(current.getLast(), comment)) {
                blocks.add(new Block(List.copyOf(current)));
                current.clear();
            }
            current.add(comment);
        }
        if (!current.isEmpty()) blocks.add(new Block(List.copyOf(current)));
        return blocks;
    }

    static boolean continues(Comment previous, Comment next) {
        return previous.line() && next.line() && previous.endLine() == next.startLine() - 1;
    }

    static List<Comment> comments(String source, List<Token> tokens) {
        var lines = new Lines(source);
        var found = new ArrayList<Comment>();
        int from = 0;
        for (var token : tokens) {
            int to = token.type() == TokenType.EOF ? source.length() : token.offset();
            if (to > from) found.addAll(inGap(source, from, to, lines));
            if (token.type() == TokenType.EOF) break;
            from = token.offset() + token.length();
        }
        return found;
    }

    static List<Comment> inGap(String source, int from, int to, Lines lines) {
        var found = new ArrayList<Comment>();
        int at = from;
        while (at < to) {
            if (source.startsWith("//", at)) {
                int end = source.indexOf('\n', at);
                end = end == -1 || end > to ? to : end;
                found.add(new Comment(true, source.substring(at + 2, end), lines.of(at), lines.of(at), lines.column(at)));
                at = end;
            } else if (source.startsWith("/*", at)) {
                int close = source.indexOf("*/", at + 2);
                int end = close == -1 || close + 2 > to ? to : close + 2;
                String body = source.substring(at + 2, Math.max(at + 2, close == -1 ? end : close));
                found.add(new Comment(false, body, lines.of(at), lines.of(end - 1), lines.column(at)));
                at = end;
            } else {
                at++;
            }
        }
        return found;
    }

    static final class Lines {
        final List<Integer> starts = new ArrayList<>(List.of(0));

        Lines(String source) {
            for (int i = 0; i < source.length(); i++) if (source.charAt(i) == '\n') starts.add(i + 1);
        }

        int of(int offset) {
            int index = Collections.binarySearch(starts, offset);
            return (index >= 0 ? index : -index - 2) + 1;
        }

        int column(int offset) {
            return offset - starts.get(of(offset) - 1) + 1;
        }
    }
}
