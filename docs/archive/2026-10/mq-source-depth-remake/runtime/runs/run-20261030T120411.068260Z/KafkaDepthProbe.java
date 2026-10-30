import java.time.Duration;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicBoolean;
import org.apache.kafka.clients.admin.*;
import org.apache.kafka.clients.consumer.*;
import org.apache.kafka.clients.producer.*;
import org.apache.kafka.common.TopicPartition;
import org.apache.kafka.common.errors.WakeupException;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.apache.kafka.common.serialization.StringSerializer;
import org.apache.kafka.common.utils.internals.AppInfoParser;

/** Real localhost Kafka API observations, with no application business handler. */
public class KafkaDepthProbe {
    static final String BOOTSTRAP = "127.0.0.1:19092";
    static final String TOPIC = "mq-depth-orders";
    static final TopicPartition P0 = new TopicPartition(TOPIC, 0);
    static final TopicPartition P1 = new TopicPartition(TOPIC, 1);
    static int assertions = 0;
    static void check(String name, boolean value, Object observed) {
        if (!value) throw new AssertionError(name + " observed=" + observed);
        assertions++;
        System.out.println("ASSERT PASS " + name + " observed=" + observed);
    }
    static Properties adminProperties() {
        Properties p = new Properties(); p.put("bootstrap.servers", BOOTSTRAP);
        p.put("request.timeout.ms", "10000"); p.put("default.api.timeout.ms", "20000"); return p;
    }
    static Properties producerProperties() {
        Properties p = new Properties(); p.putAll(adminProperties());
        p.put("client.id", "mq-depth-producer");
        p.put("key.serializer", StringSerializer.class.getName()); p.put("value.serializer", StringSerializer.class.getName());
        p.put("acks", "all"); p.put("enable.idempotence", "true"); p.put("retries", "3");
        p.put("max.in.flight.requests.per.connection", "1"); p.put("linger.ms", "0");
        p.put("compression.type", "none"); p.put("delivery.timeout.ms", "60000"); p.put("max.block.ms", "30000");
        return p;
    }
    static Properties consumerProperties(String group, String client, String instance) {
        Properties p = new Properties(); p.putAll(adminProperties());
        p.put("group.id", group); p.put("client.id", client);
        if (instance != null) p.put("group.instance.id", instance);
        p.put("key.deserializer", StringDeserializer.class.getName()); p.put("value.deserializer", StringDeserializer.class.getName());
        p.put("enable.auto.commit", "false"); p.put("auto.offset.reset", "earliest"); p.put("max.poll.records", "1");
        p.put("group.protocol", "classic"); p.put("partition.assignment.strategy", RangeAssignor.class.getName());
        p.put("session.timeout.ms", "10000"); p.put("heartbeat.interval.ms", "1000");
        return p;
    }
    static void version(String mode) {
        System.out.println("MODE " + mode + " kafkaClientVersion=" + AppInfoParser.getVersion() + " kafkaClientCommit=" + AppInfoParser.getCommitId());
        System.out.println("JAVA " + System.getProperty("java.version") + " BOOTSTRAP " + BOOTSTRAP);
        check("client-is-4.4.0", "4.4.0".equals(AppInfoParser.getVersion()), AppInfoParser.getVersion());
    }
    static void producer() throws Exception {
        System.out.println("PRODUCER_CONFIG " + new TreeMap<>(producerProperties()));
        try (Admin admin = Admin.create(adminProperties())) {
            admin.createTopics(List.of(new NewTopic(TOPIC, 2, (short)1).configs(Map.of("min.insync.replicas", "1", "cleanup.policy", "delete", "retention.ms", "3600000")))).all().get(20, TimeUnit.SECONDS);
            System.out.println("CLUSTER id=" + admin.describeCluster().clusterId().get(20, TimeUnit.SECONDS));
            System.out.println("TOPIC " + admin.describeTopics(List.of(TOPIC)).allTopicNames().get(20, TimeUnit.SECONDS));
            try (KafkaProducer<String,String> producer = new KafkaProducer<>(producerProperties())) {
                String[] ids = {"E01", "E02", "E03", "E04"};
                String[] orders = {"7042", "7043", "7044", "7045"};
                for (int i=0; i<ids.length; i++) {
                    int partition = i % 2;
                    String body = "{\"eventId\":\"" + ids[i] + "\",\"orderId\":\"" + orders[i] + "\"}";
                    RecordMetadata m = producer.send(new ProducerRecord<>(TOPIC, partition, orders[i], body)).get(30, TimeUnit.SECONDS);
                    System.out.println("PRODUCE_CONFIRMED eventId=" + ids[i] + " partition=" + m.partition() + " offset=" + m.offset() + " value=" + body);
                    check("confirmed-position-"+ids[i], m.partition()==partition && m.offset()==i/2, m);
                    if (i==0) {
                        long end = admin.listOffsets(Map.of(P0, OffsetSpec.latest())).partitionResult(P0).get(20, TimeUnit.SECONDS).offset();
                        check("E01-confirmed-before-any-consumer-constructed", end==1, "P0 endOffset="+end+" constructedConsumers=0 businessHandlersInvoked=0");
                    }
                }
            }
            var ends = admin.listOffsets(Map.of(P0, OffsetSpec.latest(), P1, OffsetSpec.latest())).all().get(20, TimeUnit.SECONDS);
            check("two-records-each-partition", ends.get(P0).offset()==2 && ends.get(P1).offset()==2, ends);
        }
        System.out.println("BUSINESS no business callback exists in this probe; no notifications, points updates or external effects executed.");
    }
    static final class Worker implements Runnable {
        final String group, client, instance;
        final AtomicBoolean readGate, stop = new AtomicBoolean(false);
        final Set<String> events = ConcurrentHashMap.newKeySet();
        final List<String> observations = new CopyOnWriteArrayList<>();
        volatile KafkaConsumer<String,String> consumer;
        volatile Throwable failure;
        Worker(String group,String client,String instance,AtomicBoolean readGate) { this.group=group; this.client=client; this.instance=instance; this.readGate=readGate; }
        public void run() {
            try (KafkaConsumer<String,String> c = new KafkaConsumer<>(consumerProperties(group,client,instance))) {
                consumer=c;
                c.subscribe(List.of(TOPIC), new ConsumerRebalanceListener() {
                    public void onPartitionsRevoked(Collection<TopicPartition> p) { System.out.println("REVOKED client="+client+" partitions="+p); }
                    public void onPartitionsAssigned(Collection<TopicPartition> p) {
                        c.pause(p);
                        System.out.println("ASSIGNED_PAUSED client="+client+" partitions="+p);
                    }
                });
                while (!stop.get()) {
                    if (readGate.get()) c.resume(c.assignment());
                    ConsumerRecords<String,String> records=c.poll(Duration.ofMillis(200));
                    for (ConsumerRecord<String,String> r:records) {
                        String id=r.value().contains("E01")?"E01":r.value().contains("E02")?"E02":r.value().contains("E03")?"E03":"E04";
                        events.add(id); observations.add(r.partition()+":"+r.offset()+":"+id);
                        System.out.println("READ group="+group+" client="+client+" partition="+r.partition()+" offset="+r.offset()+" eventId="+id+" value="+r.value());
                    }
                }
            } catch (WakeupException e) { if (!stop.get()) failure=e; }
              catch (Throwable t) { failure=t; t.printStackTrace(); }
        }
        void shutdown() { stop.set(true); KafkaConsumer<String,String> c=consumer; if(c!=null)c.wakeup(); }
    }
    static void groups() throws Exception {
        System.out.println("CONSUMER_CONFIG " + new TreeMap<>(consumerProperties("notify","notify-N1",null)));
        AtomicBoolean gate=new AtomicBoolean(false);
        List<Worker> workers=List.of(new Worker("notify","notify-N1",null,gate),new Worker("notify","notify-N2",null,gate),new Worker("notify","notify-N3",null,gate),new Worker("points","points-S1",null,gate));
        List<Thread> threads=new ArrayList<>();
        for(Worker w:workers) {Thread t=new Thread(w,w.client);threads.add(t);t.start();}
        try (Admin admin=Admin.create(adminProperties())) {
            Map<String,ConsumerGroupDescription> descriptions=null;
            long deadline=System.nanoTime()+Duration.ofSeconds(60).toNanos();
            while(System.nanoTime()<deadline) {
                for(Worker w:workers)if(w.failure!=null)throw new RuntimeException(w.failure);
                try {
                    var current=admin.describeConsumerGroups(List.of("notify","points")).all().get(10,TimeUnit.SECONDS);
                    if(current.get("notify").members().size()==3 && current.get("points").members().size()==1 && current.values().stream().allMatch(g->g.groupState().toString().equals("Stable"))) {descriptions=current;break;}
                } catch(ExecutionException e) { System.out.println("WAIT_GROUPS "+e.getCause().getClass().getSimpleName()); }
                Thread.sleep(100);
            }
            check("classic-groups-stable", descriptions!=null, descriptions);
            ConsumerGroupDescription notify=descriptions.get("notify"), points=descriptions.get("points");
            System.out.println("ADMIN_GROUP notify="+notify);
            System.out.println("ADMIN_GROUP points="+points);
            List<Integer> counts=notify.members().stream().map(m->m.assignment().topicPartitions().size()).sorted().toList();
            check("notify-three-members-two-partitions-0-1-1",counts.equals(List.of(0,1,1)),counts);
            check("dynamic-members-have-no-group-instance-id",notify.members().stream().allMatch(m->m.groupInstanceId().isEmpty()) && points.members().stream().allMatch(m->m.groupInstanceId().isEmpty()),"notify+points group.instance.id absent");
            var ordered=notify.members().stream().sorted(Comparator.comparing(MemberDescription::consumerId)).toList();
            System.out.println("DYNAMIC_MEMBER_ID_SORT "+ordered.stream().map(m->m.consumerId()+" / client="+m.clientId()+" / assignment="+m.assignment().topicPartitions()).toList());
            check("range-follows-real-member-id-order",ordered.get(0).assignment().topicPartitions().equals(Set.of(P0)) && ordered.get(1).assignment().topicPartitions().equals(Set.of(P1)) && ordered.get(2).assignment().topicPartitions().isEmpty(),ordered.stream().map(m->m.consumerId()+":"+m.assignment().topicPartitions()).toList());

            Set<TopicPartition> partitions=new HashSet<>();int assigned=0;
            for(var member:notify.members()) {System.out.println("STABLE_MEMBER group=notify client="+member.clientId()+" instance="+member.groupInstanceId()+" assignment="+member.assignment().topicPartitions());partitions.addAll(member.assignment().topicPartitions());assigned+=member.assignment().topicPartitions().size();}
            check("notify-partition-ownership-exclusive",assigned==2 && partitions.equals(Set.of(P0,P1)),partitions);
            var pointsMember=points.members().iterator().next();
            check("points-own-member-gets-both",pointsMember.assignment().topicPartitions().equals(Set.of(P0,P1)),pointsMember.assignment());
            check("no-poll-records-before-stable-reading-gate",workers.stream().allMatch(w->w.observations.isEmpty()),workers.stream().map(w->w.client+":"+w.observations).toList());
            gate.set(true);
            deadline=System.nanoTime()+Duration.ofSeconds(30).toNanos();
            Set<String> required=Set.of("E01","E02","E03","E04");
            Set<String> notifyEvents=new HashSet<>();
            while(System.nanoTime()<deadline) {
                for(Worker w:workers)if(w.failure!=null)throw new RuntimeException(w.failure);
                notifyEvents.clear();for(int i=0;i<3;i++)notifyEvents.addAll(workers.get(i).events);
                if(notifyEvents.equals(required)&&workers.get(3).events.equals(required))break;
                Thread.sleep(100);
            }
            check("notify-group-received-all-four",notifyEvents.equals(required),new TreeSet<>(notifyEvents));
            check("points-group-independently-received-all-four",workers.get(3).events.equals(required),new TreeSet<>(workers.get(3).events));
            check("same-E01-read-in-both-groups",notifyEvents.contains("E01")&&workers.get(3).events.contains("E01"),"notify and points E01 present");
            int notifyCount=0;for(int i=0;i<3;i++)notifyCount+=workers.get(i).observations.size();
            check("stable-notify-run-four-observations",notifyCount==4,notifyCount);
            check("points-run-four-observations",workers.get(3).observations.size()==4,workers.get(3).observations);
        } finally {
            for(Worker w:workers)w.shutdown();
            for(Thread t:threads)t.join(15000);
            check("worker-threads-stopped",threads.stream().noneMatch(Thread::isAlive),threads.stream().map(t->t.getName()+":"+t.isAlive()).toList());
        }
    }
    static ConsumerRecord<String,String> one(KafkaConsumer<String,String> c) {
        long deadline=System.nanoTime()+Duration.ofSeconds(20).toNanos();
        while(System.nanoTime()<deadline) {var rs=c.poll(Duration.ofMillis(200));if(!rs.isEmpty()){check("max-poll-one",rs.count()==1,rs.count());return rs.iterator().next();}}
        throw new AssertionError("no record received");
    }
    static long committed(KafkaConsumer<String,String> c) {return c.committed(Set.of(P0)).get(P0).offset();}
    static void position() throws Exception {
        System.out.println("POSITION_SCOPE manual assign(P0), group.id=progress; this isolates position/commit/recovery, not a dynamic-group assignment test.");
        System.out.println("POSITION_CONFIG "+new TreeMap<>(consumerProperties("progress","position-1",null)));
        try(KafkaConsumer<String,String> c=new KafkaConsumer<>(consumerProperties("progress","position-1",null))) {
            c.assign(List.of(P0));c.seek(P0,0);c.commitSync(Map.of(P0,new OffsetAndMetadata(0)));
            System.out.println("INITIAL_COMMIT position="+c.position(P0)+" committed="+committed(c));
            ConsumerRecord<String,String> r=one(c);long p=c.position(P0),saved=committed(c);
            System.out.println("AFTER_POLL_FIRST record="+r.offset()+" value="+r.value()+" position="+p+" committed="+saved);
            check("poll-advances-position-not-committed",r.offset()==0 && p==1 && saved==0,"offset="+r.offset()+" position="+p+" committed="+saved);
        }
        try(KafkaConsumer<String,String> c=new KafkaConsumer<>(consumerProperties("progress","position-2",null))) {
            c.assign(List.of(P0));long p=c.position(P0);check("restart-recovers-committed-zero",p==0,p);
            ConsumerRecord<String,String> r=one(c);System.out.println("REOPEN_BEFORE_COMMIT record="+r.offset()+" value="+r.value());
            check("uncommitted-record-re-read-zero",r.offset()==0 && r.value().contains("E01"),r.offset()+":"+r.value());
            c.commitSync(Map.of(P0,new OffsetAndMetadata(1)));
            check("explicit-commit-next-one",committed(c)==1,committed(c));
        }
        try(KafkaConsumer<String,String> c=new KafkaConsumer<>(consumerProperties("progress","position-3",null))) {
            c.assign(List.of(P0));long p=c.position(P0);check("next-restart-recovers-committed-one",p==1,p);
            ConsumerRecord<String,String> r=one(c);System.out.println("REOPEN_AFTER_COMMIT record="+r.offset()+" value="+r.value()+" position="+c.position(P0)+" committed="+committed(c));
            check("committed-one-continues-at-E03",r.offset()==1 && r.value().contains("E03") && c.position(P0)==2 && committed(c)==1,r.offset()+":"+r.value());
        }
    }
    public static void main(String[] args) throws Exception {
        if(args.length!=1)throw new IllegalArgumentException("producer|groups|position");
        version(args[0]);
        switch(args[0]) {case "producer"->producer();case "groups"->groups();case "position"->position();default->throw new IllegalArgumentException(args[0]);}
        System.out.println("RESULT PASS mode="+args[0]+" assertions="+assertions);
    }
}
