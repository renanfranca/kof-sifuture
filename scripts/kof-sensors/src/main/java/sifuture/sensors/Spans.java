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
        int declaration = at(tokens, function.node().position().offset());
        if (function.kind().equals("constructor")) declaration = constructorName(tokens, declaration, function);
        if (function.kind().equals("method")) declaration = methodName(tokens, declaration, function.name());
        int start = declaration;
        if (function.kind().equals("constructor")) start = declarationStart(tokens, declaration, null);
        if (function.kind().equals("method")) start = declarationStart(tokens, declaration, function.returnType());
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
        int header = function.kind().equals("lambda") ? start : declaration;
        if (function.kind().equals("lambda") && !function.parameters().isEmpty()) {
            while (header < tokens.size() - 1 && !symbol(tokens.get(header)).equals("(")) header++;
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

    static int declarationStart(List<Token> tokens, int declaration, String returnType) {
        int start = declaration;
        if (returnType != null) {
            String expected = returnType.replaceAll("\\s+", "");
            String actual = "";
            for (int i = declaration - 1; i >= 0; i--) {
                String value = symbol(tokens.get(i));
                if (List.of("{", "}", ";").contains(value)) break;
                actual = value + actual;
                if (actual.equals(expected)) {
                    start = i;
                    break;
                }
                if (!expected.startsWith(actual)) break;
            }
            if (start == declaration && !returnType.equals("void")
                    && !symbol(tokens.get(matching(tokens, declaration + 1) + 1)).equals(":")) {
                throw new IllegalArgumentException("Cannot locate declaration "
                        + symbol(tokens.get(declaration)) + " with return type " + returnType
                        + " at " + tokens.get(declaration));
            }
        }
        while (start > 0 && List.of("public", "private", "protected", "static", "abstract", "final")
                .contains(symbol(tokens.get(start - 1)))) start--;
        return start;
    }

    static int methodName(List<Token> tokens, int position, String name) {
        for (int i = Math.min(position, tokens.size() - 1); i >= 0; i--) {
            if (symbol(tokens.get(i)).equals(name) && i + 1 < tokens.size()
                    && symbol(tokens.get(i + 1)).equals("(")) return i;
            if (i < position && List.of("{", "}", ";").contains(symbol(tokens.get(i)))) break;
        }
        throw new IllegalArgumentException("Cannot locate method " + name + " at " + tokens.get(position));
    }

    static int constructorName(List<Token> tokens, int position, Analyzer.Callable function) {
        for (int i = Math.min(position, tokens.size() - 1); i >= 0; i--) {
            String value = symbol(tokens.get(i));
            boolean candidate = value.equals("constructor") || value.equals(function.name());
            if (candidate && i + 1 < tokens.size() && symbol(tokens.get(i + 1)).equals("(")) return i;
        }
        throw new IllegalArgumentException("Cannot locate constructor " + function.name()
                + " at " + tokens.get(position));
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
