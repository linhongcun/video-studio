package org.apache.kafka.storage.internals.log;

import java.lang.reflect.Proxy;
import java.util.ArrayList;
import java.util.List;
import org.apache.kafka.common.record.internal.RecordBatch;

/** A source-level unit fixture, not a Broker, network or serialized-record test. */
public final class ProducerStateEntryProbe {
    private static int checks = 0;
    private static final List<String> calls = new ArrayList<>();
    private static void check(boolean value, String label) {
        checks++;
        if (!value) throw new AssertionError(label);
    }
    private static RecordBatch batch(short epoch, int first, int last) {
        return (RecordBatch) Proxy.newProxyInstance(RecordBatch.class.getClassLoader(),
            new Class<?>[]{RecordBatch.class}, (object, method, args) -> {
                calls.add(method.getName());
                return switch (method.getName()) {
                    case "producerEpoch" -> epoch;
                    case "baseSequence" -> first;
                    case "lastSequence" -> last;
                    default -> throw new AssertionError("Unexpected field read: " + method.getName());
                };
            });
    }
    public static void main(String[] args) {
        ProducerStateEntry a = ProducerStateEntry.empty(501L);
        check(a.findDuplicateBatch(batch((short) 0, 0, 0)).isEmpty(), "empty state cannot match");
        a.addBatch((short) 0, 0, 0L, 0, 1000L);
        var duplicate = a.findDuplicateBatch(batch((short) 0, 0, 0));
        check(duplicate.isPresent(), "same epoch and exact sequence match");
        check(duplicate.orElseThrow().firstOffset() == 0L, "reuse original first offset");
        check(duplicate.orElseThrow().lastOffset() == 0L, "reuse original last offset");
        check(a.findDuplicateBatch(batch((short) 1, 0, 0)).isEmpty(), "different epoch cannot match");
        check(a.findDuplicateBatch(batch((short) 0, 1, 1)).isEmpty(), "different sequence cannot match");
        check(a.findDuplicateBatch(batch((short) 0, 0, 1)).isEmpty(), "same first sequence but different range cannot match");
        ProducerStateEntry b = ProducerStateEntry.empty(902L);
        check(b.findDuplicateBatch(batch((short) 0, 0, 0)).isEmpty(), "new producer entry has no A batch");
        for (int i = 1; i <= 5; i++) a.addBatch((short) 0, i, i, 0, 1000L + i);
        check(a.findDuplicateBatch(batch((short) 0, 0, 0)).isEmpty(), "oldest metadata evicted from bounded cache");
        check(a.batchMetadata().size() == ProducerStateEntry.NUM_BATCHES_TO_RETAIN, "retains five recent batches");
        a.addBatch((short) 1, 0, 6L, 0, 2000L);
        check(a.batchMetadata().size() == 1, "epoch change clears old cached metadata");
        check(a.findDuplicateBatch(batch((short) 1, 0, 0)).orElseThrow().firstOffset() == 6L, "new epoch matches only new batch");
        ProducerStateEntry range = ProducerStateEntry.empty(777L);
        range.addBatch((short) 0, 5, 20L, 2, 3000L);
        check(range.findDuplicateBatch(batch((short) 0, 3, 5)).isPresent(), "full three-record range matches");
        check(range.findDuplicateBatch(batch((short) 0, 3, 4)).isEmpty(), "partial range cannot match");
        check(calls.stream().allMatch(x -> List.of("producerEpoch", "baseSequence", "lastSequence").contains(x)), "no business eventId or payload read");
        System.out.println("{\"passed\":true,\"checks\":" + checks + ",\"fixture\":\"actual ProducerStateEntry and BatchMetadata sources plus official RecordBatch interface; dynamic proxy supplies only tested batch fields\",\"brokerRun\":false}");
    }
}
