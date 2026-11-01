import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import java.io.*;
import org.apache.kafka.clients.admin.*;
import org.apache.kafka.clients.consumer.*;
import org.apache.kafka.clients.producer.*;
import org.apache.kafka.common.*;
import org.apache.kafka.common.config.ConfigResource;
import org.apache.kafka.common.serialization.*;
import org.apache.kafka.common.utils.internals.AppInfoParser;

/** Actual Kafka I/O; controlled faults and disk snapshots are driven externally. */
public final class Mq15Probe {
    final Admin admin;
    final KafkaConsumer<String,String> consumer;
    final String bootstrap;
    final Map<String,KafkaProducer<String,String>> producers = new HashMap<>();
    final Map<String,Future<RecordMetadata>> sends = new HashMap<>();
    Mq15Probe(String bootstrap) {
        this.bootstrap=bootstrap;
        Properties a=new Properties();a.put("bootstrap.servers",bootstrap);a.put("default.api.timeout.ms","10000");
        a.put("request.timeout.ms","5000");a.put("client.id","mq15-admin");admin=Admin.create(a);
        Properties c=new Properties();c.putAll(a);c.put("key.deserializer",StringDeserializer.class.getName());
        c.put("value.deserializer",StringDeserializer.class.getName());c.put("enable.auto.commit","false");
        c.put("isolation.level","read_uncommitted");c.put("client.id","mq15-observer");
        consumer=new KafkaConsumer<>(c);
    }
    static Map<String,Object> obj(Object... kv){Map<String,Object> m=new LinkedHashMap<>();for(int i=0;i<kv.length;i+=2)m.put(kv[i].toString(),kv[i+1]);return m;}
    static String json(Object x) {
        if(x==null)return "null";if(x instanceof Number||x instanceof Boolean)return x.toString();
        if(x instanceof Map<?,?> m){List<String> a=new ArrayList<>();for(var e:m.entrySet())a.add(json(e.getKey().toString())+":"+json(e.getValue()));return "{"+String.join(",",a)+"}";}
        if(x instanceof Iterable<?> a){List<String>b=new ArrayList<>();for(Object y:a)b.add(json(y));return "["+String.join(",",b)+"]";}
        String s=x.toString().replace("\\","\\\\").replace("\"","\\\"").replace("\n","\\n").replace("\r","\\r");return "\""+s+"\"";
    }
    KafkaProducer<String,String> producer(String acks) {
        return producers.computeIfAbsent(acks,a->{
            Properties p=new Properties();p.put("bootstrap.servers",bootstrap);p.put("acks",a);p.put("enable.idempotence","false");
            p.put("retries","0");p.put("max.in.flight.requests.per.connection","1");p.put("linger.ms","0");
            p.put("compression.type","none");p.put("max.block.ms","10000");p.put("request.timeout.ms","120000");
            p.put("delivery.timeout.ms","150000");p.put("key.serializer",StringSerializer.class.getName());
            p.put("value.serializer",StringSerializer.class.getName());p.put("client.id","mq15-acks-"+a);
            return new KafkaProducer<>(p);
        });
    }
    Object command(String[] x) throws Exception {
        String op=x[0];
        if(op.equals("features")) {
            var f=admin.describeFeatures().featureMetadata().get(10,TimeUnit.SECONDS);Map<String,Object> sup=new TreeMap<>(),fin=new TreeMap<>();
            f.supportedFeatures().forEach((k,v)->sup.put(k,obj("min",v.minVersion(),"max",v.maxVersion())));
            f.finalizedFeatures().forEach((k,v)->fin.put(k,obj("min",v.minVersionLevel(),"max",v.maxVersionLevel())));
            return obj("version",AppInfoParser.getVersion(),"commit",AppInfoParser.getCommitId(),"supported",sup,"finalized",fin,"epoch",f.finalizedFeaturesEpoch().orElse(-1L));
        }
        if(op.equals("create")) {
            var topic=new NewTopic(x[1],Map.of(0,List.of(1,2,3))).configs(Map.of("min.insync.replicas","2","unclean.leader.election.enable","false","cleanup.policy","delete"));
            admin.createTopics(List.of(topic)).all().get(10,TimeUnit.SECONDS);return obj("created",x[1],"replicaAssignment",List.of(1,2,3));
        }
        if(op.equals("meta")) {
            var t=admin.describeTopics(List.of(x[1])).allTopicNames().get(10,TimeUnit.SECONDS).get(x[1]);var p=t.partitions().get(0);
            return obj("topic",x[1],"leader",p.leader()==null?-1:p.leader().id(),"replicas",p.replicas().stream().map(Node::id).toList(),"isr",p.isr().stream().map(Node::id).toList());
        }
        if(op.equals("config")) {
            var cr=new ConfigResource(ConfigResource.Type.TOPIC,x[1]);var cfg=admin.describeConfigs(List.of(cr)).all().get(10,TimeUnit.SECONDS).get(cr);
            return obj("topic",x[1],"min.insync.replicas",cfg.get("min.insync.replicas").value(),"unclean.leader.election.enable",cfg.get("unclean.leader.election.enable").value());
        }
        if(op.equals("controller")) {
            var q=admin.describeMetadataQuorum().quorumInfo().get(10,TimeUnit.SECONDS);
            return obj("leaderId",q.leaderId(),"leaderEpoch",q.leaderEpoch(),"highWatermark",q.highWatermark(),"voters",q.voters().stream().map(v->obj("id",v.replicaId(),"logEndOffset",v.logEndOffset())).toList());
        }
        if(op.equals("prepare")) {
            producer(x[1]).partitionsFor(x[2]);return obj("preparedAcks",x[1],"topic",x[2],"enable.idempotence",false,"retries",0,"max.in.flight.requests.per.connection",1,"request.timeout.ms",120000,"delivery.timeout.ms",150000,"compression.type","none");
        }
        if(op.equals("send")) {
            sends.put(x[1],producer(x[3]).send(new ProducerRecord<>(x[2],0,"7042",x[4])));
            return obj("label",x[1],"acks",x[3],"futureDoneImmediately",sends.get(x[1]).isDone());
        }
        if(op.equals("result")) {
            Future<RecordMetadata> f=sends.get(x[1]);if(!f.isDone())return obj("label",x[1],"state","pending");
            try {var r=f.get();return obj("label",x[1],"state","success","topic",r.topic(),"partition",r.partition(),"offset",r.offset());}
            catch(ExecutionException e){Throwable t=e.getCause();return obj("label",x[1],"state","failure","exception",t.getClass().getName(),"message",t.getMessage());}
        }
        if(op.equals("hw")) {
            var p=new TopicPartition(x[1],0);return obj("topic",x[1],"consumerEndOffset",consumer.endOffsets(List.of(p),Duration.ofSeconds(5)).get(p),"isolation.level","read_uncommitted");
        }
        if(op.equals("read")) {
            var p=new TopicPartition(x[1],0);consumer.assign(List.of(p));consumer.seek(p,0);var out=new ArrayList<Object>();
            long deadline=System.nanoTime()+TimeUnit.SECONDS.toNanos(2);
            while(System.nanoTime()<deadline){for(var r:consumer.poll(Duration.ofMillis(100)))out.add(obj("offset",r.offset(),"key",r.key(),"value",r.value()));}
            return obj("topic",x[1],"records",out);
        }
        throw new IllegalArgumentException("Unknown command "+op);
    }
    public static void main(String[] args) throws Exception {
        Mq15Probe p=new Mq15Probe(args[0]);try(var lines=new BufferedReader(new InputStreamReader(System.in))){
            String line;while((line=lines.readLine())!=null){if(line.equals("quit"))break;
                try{System.out.println(json(obj("atUTC",Instant.now().toString(),"command",line,"ok",true,"result",p.command(line.split("\\|",-1)))));}
                catch(Throwable e){System.out.println(json(obj("atUTC",Instant.now().toString(),"command",line,"ok",false,"exception",e.getClass().getName(),"message",e.toString())));}
                System.out.flush();
            }
        }finally{for(var pr:p.producers.values())pr.close(Duration.ofSeconds(1));p.consumer.close(Duration.ofSeconds(1));p.admin.close(Duration.ofSeconds(1));}
    }
}
