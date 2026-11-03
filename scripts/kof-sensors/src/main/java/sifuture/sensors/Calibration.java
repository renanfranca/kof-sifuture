package sifuture.sensors;

import java.util.List;

public final class Calibration {
    public static boolean exceeds(int value, int limit) { return value > limit; }

    public static int propose(List<Integer> values, int reference) {
        int limit = reference;
        while (true) {
            int current = limit;
            if (values.stream().filter(v -> exceeds(v, current)).count() < 20) return limit;
            limit = values.stream().filter(v -> exceeds(v, current)).min(Integer::compareTo).orElseThrow();
        }
    }
}
