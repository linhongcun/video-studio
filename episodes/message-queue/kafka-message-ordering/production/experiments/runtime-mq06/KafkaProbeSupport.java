import java.time.Duration;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.kafka.clients.admin.*;
import org.apache.kafka.clients.consumer.*;
import org.apache.kafka.clients.producer.*;
import org.apache.kafka.common.TopicPartition;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.apache.kafka.common.serialization.StringSerializer;
import org.apache.kafka.common.utils.internals.AppInfoParser;

/** Shared only by these batch-owned real runtime probes, not production code. */
class KafkaProbeSupport {
 static String bootstrap,suffix;
 static final String TOPIC="orders";
 static final TopicPartition P0=new TopicPartition(TOPIC,0),P1=new TopicPartition(TOPIC,1);
 static final ObjectMapper JSON=new ObjectMapper();
 static final AtomicInteger assertions=new AtomicInteger();
 static String json(Object x){try{return JSON.writeValueAsString(x);}catch(Exception e){throw new RuntimeException(e);}}
 static void observe(String kind,Object x){System.out.println("OBS "+kind+" "+json(x));System.out.flush();}
 static void check(String label,boolean yes,Object actual){if(!yes)throw new AssertionError(label+" actual="+json(actual));assertions.incrementAndGet();System.out.println("ASSERT PASS "+label+" actual="+json(actual));System.out.flush();}
 static Properties adminProps(){Properties p=new Properties();p.put("bootstrap.servers",bootstrap);p.put("request.timeout.ms","15000");p.put("default.api.timeout.ms","25000");return p;}
 static Properties producerProps(){Properties p=adminProps();p.put("key.serializer",StringSerializer.class.getName());p.put("value.serializer",StringSerializer.class.getName());p.put("acks","all");p.put("enable.idempotence","true");p.put("max.in.flight.requests.per.connection","1");p.put("linger.ms","0");p.put("delivery.timeout.ms","60000");return p;}
 static Properties consumerProps(String group,String client){Properties p=adminProps();p.put("group.id",group);p.put("client.id",client);p.put("key.deserializer",StringDeserializer.class.getName());p.put("value.deserializer",StringDeserializer.class.getName());p.put("enable.auto.commit","false");p.put("auto.offset.reset","earliest");p.put("max.poll.records","1");p.put("group.protocol","classic");p.put("partition.assignment.strategy",RangeAssignor.class.getName());p.put("session.timeout.ms","10000");p.put("heartbeat.interval.ms","1000");return p;}
 static void initialize(String[] args,String label)throws Exception{if(args.length!=2)throw new IllegalArgumentException("bootstrap suffix");bootstrap=args[0];suffix=args[1];observe("VERSIONS",Map.of("probe",label,"KafkaVersion",AppInfoParser.getVersion(),"KafkaCommit",AppInfoParser.getCommitId(),"java",System.getProperty("java.version")));check("Kafka-client4.4.0","4.4.0".equals(AppInfoParser.getVersion()),AppInfoParser.getVersion());try(Admin a=Admin.create(adminProps())){a.createTopics(List.of(new NewTopic(TOPIC,2,(short)1).configs(Map.of("min.insync.replicas","1")))).all().get(30,TimeUnit.SECONDS);observe("TOPIC_CREATED",Map.of("name",TOPIC,"partitions",2,"replicationFactor",1));}}
 static Map<Integer,Long> ends(Admin a)throws Exception{var rows=a.listOffsets(Map.of(P0,OffsetSpec.latest(),P1,OffsetSpec.latest())).all().get(20,TimeUnit.SECONDS);return Map.of(0,rows.get(P0).offset(),1,rows.get(P1).offset());}
 static Map<String,Object> record(ConsumerRecord<String,String> r){return Map.of("partition",r.partition(),"offset",r.offset(),"key",r.key(),"value",r.value());}
 static void done(String probe){System.out.println("RESULT PASS probe="+probe+" assertions="+assertions.get());}
}
