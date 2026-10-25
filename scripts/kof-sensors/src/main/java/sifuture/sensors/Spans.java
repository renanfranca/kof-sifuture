package sifuture.sensors;

import dev.kof.compiler.*;
import java.util.List;

final class Spans {
    static String symbol(Token token) {
        return token.type().name().endsWith("LITERAL") ? "" : token.value();
    }

    static int at(List<Token> tokens, int offset) {
        int index = 0;
        while (index + 1 < tokens.size() && tokens.get(index).offset() < offset) index++;
        return index;
    }

    static int[] callable(Analyzer.Callable function, List<Token> tokens) {
        int start = at(tokens, function.node().position().offset());
        if (function.kind().equals("constructor")) {
            while (start > 0 && !symbol(tokens.get(start)).equals("constructor")) start--;
            start = declarationStart(tokens, start);
        }
        if (function.kind().equals("method")) {
            if (!function.parameters().isEmpty()) {
                start = at(tokens, ((AstNode) function.parameters().getFirst()).position().offset());
            }
            while (start > 0 && !symbol(tokens.get(start)).equals(function.name())) start--;
            start = declarationStart(tokens, start);
        }
        if (function.kind().equals("lambda")) {
            if (!function.parameters().isEmpty()) {
                start = at(tokens, ((AstNode) function.parameters().getFirst()).position().offset());
                while (start > 0 && !List.of("(", "{").contains(symbol(tokens.get(start)))) start--;
            } else if (symbol(tokens.get(start)).equals("{")) {
                if (start > 0 && symbol(tokens.get(start - 1)).equals("->")) start = opening(tokens, start - 2);
                else return new int[]{start, matching(tokens, start)};
            } else if (start > 0 && symbol(tokens.get(start - 1)).equals("->")) {
                start = opening(tokens, start - 2);
            } else if (start > 0 && symbol(tokens.get(start - 1)).equals("}")) {
                start = opening(tokens, start - 1);
                return new int[]{start, start == 0 ? start : matching(tokens, start)};
            } else {
                throw new IllegalArgumentException("Cannot locate lambda at " + function.node().position());
            }
        }
        if (function.kind().equals("test") || symbol(tokens.get(start)).equals("{")) {
            int brace = start;
            while (brace < tokens.size() - 1 && !symbol(tokens.get(brace)).equals("{")) brace++;
            return new int[]{start, matching(tokens, brace)};
        }
        int header = start;
        if (!function.kind().equals("lambda")) {
            String name = function.kind().equals("constructor") ? "constructor" : function.name();
            while (header < tokens.size() - 1 && !symbol(tokens.get(header)).equals(name)) header++;
        }
        while (header < tokens.size() - 1 && !symbol(tokens.get(header)).equals("(")) header++;
        int after = matching(tokens, header) + 1;
        if (function.body().isEmpty() && !symbol(tokens.get(after)).equals("{")) return new int[]{start, after - 1};
        while (after < tokens.size() - 1 && !List.of("{", "=", "->").contains(symbol(tokens.get(after)))) after++;
        if (symbol(tokens.get(after)).equals("->")) after++;
        if (symbol(tokens.get(after)).equals("{")) return new int[]{start, matching(tokens, after)};
        if (symbol(tokens.get(after)).equals("=")) after++;
        int end = expressionEnd(tokens, after, exclusiveEnd(function.body(), tokens));
        return new int[]{start, end};
    }

    static int declarationStart(List<Token> tokens, int name) {
        int start = name;
        int line = tokens.get(name).line();
        while (start > 0 && tokens.get(start - 1).line() == line
                && !List.of("{", "}", ";").contains(symbol(tokens.get(start - 1)))) start--;
        while (start > 0 && List.of("public", "private", "protected", "static", "abstract", "final")
                .contains(symbol(tokens.get(start - 1)))) start--;
        return start;
    }

    static int exclusiveEnd(Object object, List<Token> tokens) {
        int offset = 0;
        if (object instanceof ExpressionNode node) {
            offset = node.position().offset();
            if (node instanceof IdentifierExpr) {
                var token = tokens.get(at(tokens, offset));
                offset = token.offset() + token.length();
            }
        }
        for (var child : Analyzer.children(object)) offset = Math.max(offset, exclusiveEnd(child, tokens));
        return offset;
    }

    static int expressionEnd(List<Token> tokens, int start, int exclusiveEnd) {
        int end = start;
        for (int i = start; i < tokens.size() - 1 && tokens.get(i).offset() < exclusiveEnd; i++) {
            if (List.of("(", "[", "{").contains(symbol(tokens.get(i)))) i = matching(tokens, i);
            end = i;
        }
        return end;
    }

    static int matching(List<Token> tokens, int start) {
        String opening = symbol(tokens.get(start));
        String closing = switch (opening) { case "(" -> ")"; case "[" -> "]"; case "{" -> "}"; default -> ""; };
        int depth = 0;
        for (int i = start; i < tokens.size(); i++) {
            if (symbol(tokens.get(i)).equals(opening)) depth++;
            if (symbol(tokens.get(i)).equals(closing) && --depth == 0) return i;
        }
        throw new IllegalArgumentException("Unclosed official token at " + tokens.get(start));
    }

    static int opening(List<Token> tokens, int end) {
        String closing = symbol(tokens.get(end));
        String opening = switch (closing) { case ")" -> "("; case "]" -> "["; case "}" -> "{"; default -> ""; };
        int depth = 0;
        for (int i = end; i >= 0; i--) {
            if (symbol(tokens.get(i)).equals(closing)) depth++;
            if (symbol(tokens.get(i)).equals(opening) && --depth == 0) return i;
        }
        throw new IllegalArgumentException("Unmatched official token at " + tokens.get(end));
    }
}
