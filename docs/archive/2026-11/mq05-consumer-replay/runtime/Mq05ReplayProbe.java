import java.sql.*;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import org.apache.kafka.clients.admin.*;
import org.apache.kafka.clients.consumer.*;
import org.apache.kafka.clients.producer.*;
import org.apache.kafka.common.*;
import org.apache.kafka.common.serialization.*;
import org.apache.kafka.common.utils.internals.AppInfoParser;

/** Bounded real client/DB fixture; application failure is an intentional process halt. */
public class Mq05ReplayProbe {
 static final String VALUE="{\"eventId\":\"E01\",\"orderId\":7042,\"accountId\":17,\"delta\":10}";
 static String mode,bootstrap,jdbc,topic,group,branch,schema;static TopicPartition tp;static int checks;
 static String json(Object x){if(x==null)return"null";if(x instanceof Number||x instanceof Boolean)return x.toString();if(x instanceof Map<?,?>m){var a=new ArrayList<String>();for(var e:m.entrySet())a.add(json(String.valueOf(e.getKey()))+":"+json(e.getValue()));return"{"+String.join(",",a)+"}";}if(x instanceof Collection<?>c)return"["+String.join(",",c.stream().map(Mq05ReplayProbe::json).toList())+"]";return"\""+x.toString().replace("\\","\\\\").replace("\"","\\\"").replace("\n","\\n").replace("\r","\\r")+"\"";}
 static void obs(String kind,Object v){System.out.println("OBS "+kind+" "+json(Map.of("atUTC",Instant.now().toString(),"branch",branch,"process",mode,"data",v)));System.out.flush();}
 static void check(String name,boolean ok,Object actual){checks++;obs("ASSERT",Map.of("name",name,"pass",ok,"actual",actual));if(!ok)throw new AssertionError(name+": "+actual);}
 static Properties common(String id){Properties p=new Properties();p.put("bootstrap.servers",bootstrap);p.put("client.id",id);p.put("request.timeout.ms","15000");p.put("default.api.timeout.ms","30000");return p;}
 static Admin admin(){return Admin.create(common("mq05-observer-"+branch+"-"+mode));}
 static long committed()throws Exception{try(Admin a=admin()){var map=a.listConsumerGroupOffsets(group).partitionsToOffsetAndMetadata().get(30,TimeUnit.SECONDS);var m=map.get(tp);return m==null?-1:m.offset();}}
 static long offset(boolean earliest)throws Exception{try(Admin a=admin()){return a.listOffsets(Map.of(tp,earliest?OffsetSpec.earliest():OffsetSpec.latest())).all().get(30,TimeUnit.SECONDS).get(tp).offset();}}
 static Connection db()throws Exception{Connection c=DriverManager.getConnection(jdbc);c.setSchema(schema);return c;}
 static long n(Connection c,String q)throws Exception{try(Statement s=c.createStatement();ResultSet r=s.executeQuery(q)){r.next();return r.getLong(1);}}
 static Map<String,Object> snapshot()throws Exception{try(Connection c=db()){return Map.of("points",n(c,"SELECT points FROM account_points WHERE account_id=17"),"markerCount",n(c,"SELECT count(*) FROM processed_events"),"eventMarkerCount",n(c,"SELECT count(*) FROM processed_events WHERE logical_consumer='points' AND event_id='E01'"),"accountRows",n(c,"SELECT count(*) FROM account_points"));}}
 static void setup()throws Exception{
  try(Connection c=DriverManager.getConnection(jdbc);Statement s=c.createStatement()){
   s.execute("CREATE SCHEMA "+schema);s.execute("SET search_path TO "+schema);
   s.execute("CREATE TABLE processed_events(logical_consumer text NOT NULL,event_id text NOT NULL,PRIMARY KEY(logical_consumer,event_id))");
   s.execute("CREATE TABLE account_points(account_id bigint PRIMARY KEY,points int NOT NULL)");s.execute("INSERT INTO account_points VALUES(17,0)");
  }
  try(Admin a=admin()){
   a.createTopics(List.of(new NewTopic(topic,1,(short)1).configs(Map.of("min.insync.replicas","1","cleanup.policy","delete","retention.ms","86400000","segment.bytes","1048576")))).all().get(30,TimeUnit.SECONDS);
   var td=a.describeTopics(List.of(topic)).allTopicNames().get(30,TimeUnit.SECONDS).get(topic);obs("TOPIC_IDENTITY",Map.of("topic",topic,"topicId",td.topicId().toString(),"partitions",td.partitions().size()));
   a.alterConsumerGroupOffsets(group,Map.of(tp,new OffsetAndMetadata(0))).all().get(30,TimeUnit.SECONDS);
   obs("INITIAL_DURABLE_OFFSET",Map.of("method","Admin.alterConsumerGroupOffsets explicit map0; broker query", "committed",committed()));
  }
  Properties p=common("mq05-single-seed-"+branch);p.put("key.serializer",StringSerializer.class.getName());p.put("value.serializer",StringSerializer.class.getName());p.put("enable.idempotence","true");p.put("acks","all");p.put("max.in.flight.requests.per.connection","1");p.put("retries","3");p.put("linger.ms","0");
  obs("PRODUCER_CONFIG",Map.of("enable.idempotence",true,"acks","all","retries",3,"max.in.flight.requests.per.connection",1,"applicationSendCalls",1));
  try(KafkaProducer<String,String> producer=new KafkaProducer<>(p)){var m=producer.send(new ProducerRecord<>(topic,0,"7042",VALUE)).get(30,TimeUnit.SECONDS);check("only-seed-record-P0-offset0",m.partition()==0&&m.offset()==0,Map.of("partition",m.partition(),"offset",m.offset()));}
  check("durable-initial-committed0",committed()==0,committed());check("one-log-record-LEO1",offset(false)==1,offset(false));check("log-start0",offset(true)==0,offset(true));check("fresh-zero-before-first-business-transaction",((Number)snapshot().get("points")).intValue()==0&&((Number)snapshot().get("markerCount")).intValue()==0,snapshot());obs("SETUP",Map.of("group",group,"topic",topic,"database",snapshot(),"committed",committed(),"LEO",offset(false)));
 }
 static KafkaConsumer<String,String> consumer(){Properties p=common("mq05-"+branch+"-"+mode);p.put("group.id",group);p.put("group.protocol","classic");p.put("enable.auto.commit","false");p.put("max.poll.records","1");p.put("partition.assignment.strategy",RangeAssignor.class.getName());p.put("auto.offset.reset","earliest");p.put("session.timeout.ms","6000");p.put("heartbeat.interval.ms","1000");p.put("max.poll.interval.ms","60000");p.put("key.deserializer",StringDeserializer.class.getName());p.put("value.deserializer",StringDeserializer.class.getName());obs("CONSUMER_CONFIG",Map.of("group",group,"group.protocol","classic","enable.auto.commit",false,"max.poll.records",1,"partition.assignment.strategy","RangeAssignor","auto.offset.reset","earliest (fallback only; explicit durable offset already exists)"));return new KafkaConsumer<>(p);}
 static void business(boolean safe)throws Exception{
  try(Connection c=db()){
   c.setAutoCommit(false);boolean inserted=true;int update=0;
   try{
    if(safe)try(PreparedStatement s=c.prepareStatement("INSERT INTO processed_events(logical_consumer,event_id) VALUES('points','E01') ON CONFLICT DO NOTHING RETURNING event_id");ResultSet r=s.executeQuery()){inserted=r.next();}
    if(inserted)try(PreparedStatement s=c.prepareStatement("UPDATE account_points SET points=points+10 WHERE account_id=17")){update=s.executeUpdate();check("business-update-exactly-one-row-or-rollback",update==1,update);}
    c.commit();obs("DB_COMMITTED",Map.of("sameTransactionMarkerAndEffect",safe,"insertedNewBusinessKey",safe&&inserted,"updateRows",update,"outsideConnectionSnapshot",snapshot()));
   }catch(Throwable e){c.rollback();throw e;}
  }
 }
 static void halt(String why)throws Exception{obs("INTENTIONAL_HALT",Map.of("exitCode",86,"boundary",why,"database",snapshot(),"brokerCommitted",committed(),"LEO",offset(false)));System.out.flush();System.err.flush();Runtime.getRuntime().halt(86);}
 static void worker()throws Exception{
  final boolean isB=mode.equals("B"),early=branch.equals("early-commit"),safe=branch.equals("safe");final long restore=early&&isB?1:0;
  try(KafkaConsumer<String,String> c=consumer()){
   final boolean[]assigned={false};c.subscribe(List.of(topic),new ConsumerRebalanceListener(){public void onPartitionsRevoked(Collection<TopicPartition>p){obs("REVOKED",p.toString());}public void onPartitionsAssigned(Collection<TopicPartition>parts){try{check("single-assigned-P0",parts.size()==1&&parts.contains(tp),parts.toString());long stored=c.committed(Set.of(tp)).get(tp).offset(),position=c.position(tp);check("restored-from-explicit-durable-offset",stored==restore&&position==restore,Map.of("committed",stored,"position",position));obs("ASSIGNED_RESTORED",Map.of("storedBrokerOffset",stored,"positionBeforeRecordDelivery",position,"explicitSeekUsed",false,"autoResetUsed",false));assigned[0]=true;}catch(Exception e){throw new RuntimeException(e);}}});
   ConsumerRecord<String,String>record=null;long deadline=System.nanoTime()+TimeUnit.SECONDS.toNanos(45),assignedAt=0;int empty=0;
   while(System.nanoTime()<deadline){var rows=c.poll(Duration.ofMillis(150));if(assigned[0]&&assignedAt==0)assignedAt=System.nanoTime();if(rows.count()>0){check("one-record-returned-by-nonempty-poll",rows.count()==1,rows.count());record=rows.iterator().next();break;}empty++;if(early&&isB&&assignedAt!=0&&System.nanoTime()-assignedAt>TimeUnit.SECONDS.toNanos(2))break;}
   if(early&&isB){check("committed1-restart-no-redelivery",assigned[0]&&record==null&&c.position(tp)==1&&committed()==1,Map.of("assigned",assigned[0],"received",record==null?0:1,"position",c.position(tp),"committed",committed(),"boundedEmptyPolls",empty));check("early-commit-lost-business-points0",((Number)snapshot().get("points")).intValue()==0,snapshot());check("original-record-retained-logStart0-LEO1",offset(true)==0&&offset(false)==1,Map.of("logStart",offset(true),"LEO",offset(false)));obs("NO_REDELIVERY",Map.of("businessExecutions",0,"database",snapshot(),"position",c.position(tp),"committed",committed(),"retainedRecordOffset",0));return;}
   check("actual-seeded-E01-same-partition-offset-value",record!=null&&record.partition()==0&&record.offset()==0&&record.key().equals("7042")&&record.value().equals(VALUE),record==null?"null":Map.of("topic",record.topic(),"partition",record.partition(),"offset",record.offset(),"key",record.key(),"value",record.value()));
   check("poll-position1-while-durable-committed0",c.position(tp)==1&&committed()==0,Map.of("position",c.position(tp),"committed",committed()));obs("RECORD_DELIVERED",Map.of("partition",record.partition(),"offset",record.offset(),"value",record.value(),"position",c.position(tp),"committed",committed()));
   if(early){c.commitSync(Map.of(tp,new OffsetAndMetadata(1)));check("early-Kafka1-confirmed-before-any-business",committed()==1&&((Number)snapshot().get("points")).intValue()==0,Map.of("committed",committed(),"database",snapshot()));halt("AFTER_KAFKA_COMMIT1_BEFORE_ANY_DB_TRANSACTION");}
   business(safe);int expected=safe?10:(isB?20:10);check("outside-DB-points-after-local-commit",((Number)snapshot().get("points")).intValue()==expected,snapshot());check("DB-commit-did-not-change-Kafka0",committed()==0,committed());
   if(!isB)halt("AFTER_DB_COMMIT_BEFORE_KAFKA_COMMIT1");
   c.commitSync(Map.of(tp,new OffsetAndMetadata(record.offset()+1)));check("Kafka1-after-business-local-COMMIT",committed()==1,committed());check("only-one-log-record-after-recovery",offset(true)==0&&offset(false)==1,Map.of("logStart",offset(true),"LEO",offset(false)));obs("RECOVERY_FINAL",Map.of("database",snapshot(),"committed",committed(),"position",c.position(tp),"producerResendCalls",0));
  }
 }
 static void inspect()throws Exception{obs("INDEPENDENT_SNAPSHOT",Map.of("database",snapshot(),"committed",committed(),"logStart",offset(true),"LEO",offset(false)));}
 public static void main(String[]args)throws Exception{
  mode=args[0];bootstrap=args[1];jdbc=args[2];topic=args[3];group=args[4];branch=args[5];schema="mq05_"+branch.replace('-','_');tp=new TopicPartition(topic,0);
  check("Kafka4.4.0-fixed-build",AppInfoParser.getVersion().equals("4.4.0")&&AppInfoParser.getCommitId().equals("1156b2752aaa28ea"),Map.of("version",AppInfoParser.getVersion(),"commit",AppInfoParser.getCommitId()));
  try(Connection c=DriverManager.getConnection(jdbc)){check("real-PostgreSQL18.0",n(c,"SHOW server_version_num")==180000,c.getMetaData().getDatabaseProductVersion());}
  obs("PROCESS_START",Map.of("pid",ProcessHandle.current().pid(),"group",group,"topic",topic,"mode",mode));
  switch(mode){case"setup"->setup();case"A","B"->worker();case"inspect"->inspect();default->throw new IllegalArgumentException(mode);}
  obs("RESULT",Map.of("pass",true,"checks",checks));
 }
}
