package sifuture.sensors;

import dev.kof.compiler.*;
import java.util.*;
import java.util.regex.Pattern;

final class TestRules {
    static final int MOST_ARRANGE = 8;
    static final Set<String> FILLING_HOOKS = Set.of("setup", "beforeEach", "beforeAll");
    static final Pattern ASSERTION = Pattern.compile("^(assert|fail|expect|verify|then|should)");

    static List<Findings.Finding> findings(String file, Analyzer.Parsed parsed) {
        var found = new ArrayList<Findings.Finding>();
        boolean hasTests = parsed.unit().declarations().stream().anyMatch(TestDeclarationNode.class::isInstance);
        for (var declaration : parsed.unit().declarations()) {
            if (hasTests && declaration instanceof FunctionDeclarationNode hook && FILLING_HOOKS.contains(hook.name())
                    && hook.parameters().isEmpty()) {
                found.addAll(guests(file, hook, parsed));
            }
            if (!(declaration instanceof TestDeclarationNode test)) continue;
            var start = parsed.tokens().get(Spans.at(parsed.tokens(), test.position().offset()));
            if (!asserts(test.body())) {
                found.add(new Findings.Finding("assertion-free-test", file, test.name(), start.line(), start.column(), null, null));
            }
            int arrange = arrangeLength(test.body());
            if (arrange > MOST_ARRANGE) {
                found.add(new Findings.Finding("unnamed-arrange", file, test.name(), start.line(), start.column(), arrange, MOST_ARRANGE));
            }
            found.addAll(each("branching-test", inside(test.body(), TestRules::branches), file, test, parsed));
            found.addAll(each("looping-test", inside(test.body(), TestRules::loops), file, test, parsed));
        }
        return found;
    }

    static List<Findings.Finding> each(String rule, List<Object> nodes, String file, TestDeclarationNode test, Analyzer.Parsed parsed) {
        return nodes.stream().map(node -> {
            var at = parsed.tokens().get(Spans.at(parsed.tokens(), ((AstNode) node).position().offset()));
            return new Findings.Finding(rule, file, test.name(), at.line(), at.column(), null, null);
        }).toList();
    }

    static List<Findings.Finding> guests(String file, FunctionDeclarationNode hook, Analyzer.Parsed parsed) {
        var locals = new HashSet<String>();
        inside(hook.body(), VarDeclStmt.class::isInstance).forEach(node -> locals.add(((VarDeclStmt) node).name()));
        var found = new ArrayList<Findings.Finding>();
        for (var node : inside(hook.body(), AssignmentExpr.class::isInstance)) {
            var assignment = (AssignmentExpr) node;
            String target = shared(assignment.target(), locals);
            if (target == null) continue;
            var at = parsed.tokens().get(Spans.at(parsed.tokens(), earliestOffset(assignment)));
            found.add(new Findings.Finding("mystery-guest", file, target, at.line(), at.column(), null, null));
        }
        return found;
    }

    static int earliestOffset(Object node) {
        int offset = node instanceof AstNode ast ? ast.position().offset() : Integer.MAX_VALUE;
        for (var child : Analyzer.children(node)) offset = Math.min(offset, earliestOffset(child));
        return offset;
    }

    static String shared(ExpressionNode target, Set<String> locals) {
        if (target instanceof IdentifierExpr identifier) return locals.contains(identifier.name()) ? null : identifier.name();
        if (target instanceof FieldAccessExpr field) {
            String receiver = field.receiver() instanceof IdentifierExpr owner ? owner.name() : "…";
            return receiver + "." + field.fieldName();
        }
        return null;
    }

    static int arrangeLength(List<StatementNode> body) {
        for (int index = 0; index < body.size(); index++) {
            if (assertsHere(body.get(index))) return index;
        }
        return body.size();
    }

    static boolean assertsHere(StatementNode statement) {
        if (statement instanceof AssertStmt) return true;
        return statement instanceof ExpressionStmt expression && expression.expression() instanceof MethodCallExpr call
                && ASSERTION.matcher(call.methodName()).find();
    }

    static boolean loops(Object node) {
        return node instanceof ForStmt || node instanceof ForInStmt || node instanceof WhileStmt || node instanceof DoWhileStmt;
    }

    static boolean branches(Object node) {
        return node instanceof IfStmt || node instanceof IfExpr || node instanceof SwitchStmt || node instanceof SwitchExpr;
    }

    static List<Object> inside(Object node, java.util.function.Predicate<Object> wanted) {
        var found = new ArrayList<Object>();
        if (wanted.test(node)) found.add(node);
        for (var child : Analyzer.children(node)) found.addAll(inside(child, wanted));
        return found;
    }

    static boolean asserts(Object node) {
        if (node instanceof AssertStmt) return true;
        if (node instanceof MethodCallExpr call && ASSERTION.matcher(call.methodName()).find()) return true;
        return Analyzer.children(node).stream().anyMatch(TestRules::asserts);
    }
}
