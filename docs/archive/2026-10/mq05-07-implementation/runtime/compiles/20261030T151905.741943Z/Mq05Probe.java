import java.sql.*;
import java.time.Duration;
import java.util.*;
import java.util.concurrent.*;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.kafka.clients.admin.*;
import org.apache.kafka.clients.consumer.*;
import org.apache.kafka.clients.producer.*;
import org.apache.kafka.common.TopicPartition;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.apache.kafka.common.serialization.StringSerializer;
import org.apache.kafka.common.utils.internals.AppInfoParser;

/** Real temporary RF1 Kafka and PostgreSQL18 experiment, not a model/benchmark. */
public class Mq05Probe {
 static String bootstrap, pgurl, suffix;
 static final String TOPIC="mq05-orders";
 static final TopicPartition P0=new TopicPartition(TOPIC,0);
 static final String EVENT="E01", LOGICAL="points", KEY="7042";
 static final String BODY="{\"eventId\":\"E01\",\"orderId\":\"7042\",\"accountId\":17,\"delta\":10}";
 static final String INSERT="INSERT INTO processed_events(logical_consumer,event_id) VALUES (?,?) ON CONFLICT DO NOTHING RETURNING event_id";
 static final String UPDATE="UPDATE account_points SET points=points+? WHERE account_id=?";
 static final ObjectMapper JSON=new ObjectMapper();
 static int assertions=0;
 static String json(Object x) {try{return JSON.writeValueAsString(x);}catch(Exception e){throw new RuntimeException(e);}}
 static void observe(String kind,Object data){System.out.println("OBS "+kind+" "+json(data));System.out.flush();}
 static void check(String name,boolean pass,Object actual){if(!pass)throw new AssertionError(name+" actual="+json(actual));assertions++;System.out.println("ASSERT PASS "+name+" actual="+json(actual));System.out.flush();}
 static Properties adminProps(){Properties p=new Properties();p.put("bootstrap.servers",bootstrap);p.put("request.timeout.ms","15000");p.put("default.api.timeout.ms","30000");return p;}
 static Properties producerProps(){Properties p=adminProps();p.put("key.serializer",StringSerializer.class.getName());p.put("value.serializer",StringSerializer.class.getName());p.put("acks","all");p.put("enable.idempotence","true");p.put("max.in.flight.requests.per.connection","1");p.put("linger.ms","0");p.put("delivery.timeout.ms","60000");return p;}
 static Properties consumerProps(String group,String client){Properties p=adminProps();p.put("group.id",group);p.put("client.id",client);p.put("key.deserializer",StringDeserializer.class.getName());p.put("value.deserializer",StringDeserializer.class.getName());p.put("enable.auto.commit","false");p.put("auto.offset.reset","earliest");p.put("max.poll.records","1");p.put("group.protocol","classic");p.put("partition.assignment.strategy",RangeAssignor.class.getName());p.put("session.timeout.ms","6000");p.put("heartbeat.interval.ms","1000");return p;}
 static Connection db(String name)throws Exception{Properties p=new Properties();p.setProperty("user",System.getProperty("user.name"));p.setProperty("ApplicationName",name);p.setProperty("sslmode","disable");return DriverManager.getConnection(pgurl,p);}
 static long number(Connection c,String query)throws Exception{try(Statement s=c.createStatement();ResultSet r=s.executeQuery(query)){if(!r.next())throw new AssertionError("No scalar: "+query);return r.getLong(1);}}
 static long points(Connection c)throws Exception{return number(c,"SELECT points FROM account_points WHERE account_id=17");}
 static long markerCount(Connection c)throws Exception{return number(c,"SELECT count(*) FROM processed_events WHERE logical_consumer='points' AND event_id='E01'");}
 static Map<String,Object> snapshot()throws Exception{try(Connection c=db("mq05-observer")){var out=new LinkedHashMap<String,Object>();out.put("markerCount",markerCount(c));out.put("accountRows",number(c,"SELECT count(*) FROM account_points WHERE account_id=17"));if((long)out.get("accountRows")==1)out.put("points",points(c));return out;}}
 static void fixture(boolean account,int initial)throws Exception{try(Connection c=db("mq05-fixture")){c.setAutoCommit(false);try(Statement s=c.createStatement()){s.executeUpdate("TRUNCATE processed_events,account_points");if(account)s.executeUpdate("INSERT INTO account_points(account_id,points) VALUES (17,"+initial+")");}c.commit();}observe("FIXTURE_RESET",snapshot());}
 static String insert(Connection c)throws Exception{try(PreparedStatement p=c.prepareStatement(INSERT)){p.setString(1,LOGICAL);p.setString(2,EVENT);try(ResultSet r=p.executeQuery()){String value=r.next()?r.getString(1):"";check("at-most-one-returned-event",!r.next(),value);return value;}}}
 static int update(Connection c)throws Exception{try(PreparedStatement p=c.prepareStatement(UPDATE)){p.setInt(1,10);p.setLong(2,17);return p.executeUpdate();}}
 static class BusinessRowsException extends Exception{BusinessRowsException(int rows){super("UPDATE must affect exactly1 row, actual="+rows);}}
 static Map<String,Object> apply(Connection c,String label)throws Exception{
  c.setAutoCommit(false);boolean inserted=false;int updated=0;
  try{
   String returned=insert(c);inserted=!returned.isEmpty();
   observe("INSERT_RETURNING",Map.of("task",label,"returned",returned,"newRow",inserted));
   if(inserted){updated=update(c);if(updated!=1)throw new BusinessRowsException(updated);}
   c.commit();
   var result=Map.<String,Object>of("task",label,"inserted",inserted,"updateRows",updated,"points",points(c),"markerCount",markerCount(c),"databaseCommit",true);
   observe("DB_COMMIT",result);return result;
  }catch(Exception error){c.rollback();observe("DB_ROLLBACK",Map.of("task",label,"insertWasNew",inserted,"updateRowsBeforeFailure",updated,"errorType",error.getClass().getName(),"error",error.getMessage()));throw error;}
 }
 static ConsumerRecord<String,String> first(KafkaConsumer<String,String> c)throws Exception{
  c.subscribe(List.of(TOPIC));long deadline=System.nanoTime()+TimeUnit.SECONDS.toNanos(60);
  while(System.nanoTime()<deadline){ConsumerRecords<String,String> rows=c.poll(Duration.ofMillis(250));if(!rows.isEmpty()){check("max-poll-records-one",rows.count()==1,rows.count());var r=rows.iterator().next();check("same-E01-record",r.partition()==0&&r.offset()==0&&KEY.equals(r.key())&&BODY.equals(r.value()),Map.of("partition",r.partition(),"offset",r.offset(),"key",r.key(),"value",r.value()));return r;}}
  throw new AssertionError("No E01 before deadline");
 }
 static String group(boolean dedup){return "mq05-"+(dedup?"dedup-":"naive-")+suffix;}
 static void setup()throws Exception{
  try(Connection c=db("mq05-schema");Statement s=c.createStatement()){
   s.executeUpdate("CREATE TABLE processed_events(logical_consumer text NOT NULL,event_id text NOT NULL,PRIMARY KEY(logical_consumer,event_id))");
   s.executeUpdate("CREATE TABLE account_points(account_id bigint PRIMARY KEY,points int NOT NULL)");
  }
  fixture(true,0);
  try(Admin a=Admin.create(adminProps())){a.createTopics(List.of(new NewTopic(TOPIC,1,(short)1).configs(Map.of("min.insync.replicas","1")))).all().get(30,TimeUnit.SECONDS);}
  try(KafkaProducer<String,String> p=new KafkaProducer<>(producerProps())){var r=p.send(new ProducerRecord<>(TOPIC,0,KEY,BODY)).get(30,TimeUnit.SECONDS);check("seed-confirmed-P0-offset0",r.partition()==0&&r.offset()==0,Map.of("partition",r.partition(),"offset",r.offset()));}
  for(boolean d:new boolean[]{false,true})try(KafkaConsumer<String,String> c=new KafkaConsumer<>(consumerProps(group(d),"mq05-initialize-"+d))){first(c);c.commitSync(Map.of(P0,new OffsetAndMetadata(0)));check("initial-committed-zero",c.committed(Set.of(P0)).get(P0).offset()==0,c.committed(Set.of(P0)).get(P0).offset());observe("GROUP_INITIALIZED_NO_BUSINESS",Map.of("group",group(d),"committed",0,"businessHandlersExecuted",0));}
 }
 static void worker(boolean dedup,boolean crash)throws Exception{
  String name=(dedup?"dedup":"naive")+(crash?"-crash":"-replay");
  observe("CONSUMER_CONFIG",new TreeMap<>(consumerProps(group(dedup),name)));
  try(KafkaConsumer<String,String> c=new KafkaConsumer<>(consumerProps(group(dedup),name));Connection sql=db("mq05-"+name)){
   var row=first(c);long committed=c.committed(Set.of(P0)).get(P0).offset();
   check("stored-offset-zero-before-handler",committed==0,committed);check("position-is-next-one",c.position(P0)==1,c.position(P0));
   if(dedup){var outcome=apply(sql,name);check("dedup-insert-result-matches-phase",(boolean)outcome.get("inserted")==crash,outcome);}
   else{sql.setAutoCommit(false);check("naive-update-one-row",update(sql)==1,"account17");sql.commit();observe("DB_COMMIT",Map.of("task",name,"points",points(sql),"markerCount",markerCount(sql),"databaseCommit",true));}
   Map<String,Object> outside=snapshot();long expected=dedup?10:crash?10:20;
   check("database-committed-points-"+expected,((Number)outside.get("points")).longValue()==expected,outside);
   check("Kafka-still-zero-after-independent-DB-commit",c.committed(Set.of(P0)).get(P0).offset()==0,0);
   if(crash){observe("PROCESS_HALT_BEFORE_KAFKA_COMMIT",Map.of("expectedExitCode",dedup?24:23,"group",group(dedup),"KafkaCommitted",0,"database",outside));System.out.flush();System.err.flush();Runtime.getRuntime().halt(dedup?24:23);}
   c.commitSync(Map.of(P0,new OffsetAndMetadata(row.offset()+1)));
   check("Kafka-commit-one-after-local-DB-commit",c.committed(Set.of(P0)).get(P0).offset()==1,c.committed(Set.of(P0)).get(P0).offset());
   observe("KAFKA_COMMIT_AFTER_DB",Map.of("group",group(dedup),"offset",1,"database",outside));
  }
 }
 static int pid(Connection c)throws Exception{return (int)number(c,"SELECT pg_backend_pid()");}
 static Map<String,Object> waitForBlocked(Connection monitor,int a,int b)throws Exception{
  long deadline=System.nanoTime()+TimeUnit.SECONDS.toNanos(10);
  while(System.nanoTime()<deadline){
   try(PreparedStatement p=monitor.prepareStatement("SELECT state,wait_event_type,wait_event,pg_blocking_pids(pid)::text,?=ANY(pg_blocking_pids(pid)) FROM pg_stat_activity WHERE pid=?")){
    p.setInt(1,a);p.setInt(2,b);try(ResultSet r=p.executeQuery()){if(r.next()&&"Lock".equals(r.getString(2))&&r.getBoolean(5))return Map.of("A_pid",a,"B_pid",b,"B_state",r.getString(1),"waitType",r.getString(2),"waitEvent",r.getString(3),"blockingPids",r.getString(4));}
   }
   Thread.onSpinWait();
  }
  throw new AssertionError("B not actually observed waiting on A's PostgreSQL lock");
 }
 static void race(boolean commitA)throws Exception{
  fixture(true,0);String label=commitA?"A-commit":"A-rollback";ExecutorService pool=Executors.newSingleThreadExecutor();
  try(Connection a=db("mq05-"+label);Connection b=db("mq05-B-after-"+label);Connection monitor=db("mq05-monitor")){
   a.setAutoCommit(false);b.setAutoCommit(false);int aPid=pid(a),bPid=pid(b);
   check("A-new-key",EVENT.equals(insert(a)),label);check("A-updates-one-row",update(a)==1,label);
   check("A-sees-uncommitted-ten",points(a)==10,points(a));
   var external=snapshot();check("outsider-sees-uncommitted-neither-marker-nor-points",((Number)external.get("markerCount")).intValue()==0&&((Number)external.get("points")).intValue()==0,external);
   CountDownLatch started=new CountDownLatch(1);
   Future<Map<String,Object>> second=pool.submit(()->{started.countDown();return apply(b,"B-after-"+label);});
   check("B-task-started",started.await(5,TimeUnit.SECONDS),label);
   var wait=waitForBlocked(monitor,aPid,bPid);observe("ACTUAL_POSTGRES_BLOCKING",wait);check("B-actually-blocked-before-A-decision",!second.isDone(),wait);
   if(commitA)a.commit();else a.rollback();observe("A_TRANSACTION_DECISION",Map.of("decision",commitA?"COMMIT":"ROLLBACK","sameInitialFixture",true));
   var outcome=second.get(10,TimeUnit.SECONDS);check("B-gains-key-only-if-A-rolled-back",((Boolean)outcome.get("inserted"))==!commitA,outcome);
   check("B-update-count",((Number)outcome.get("updateRows")).intValue()==(commitA?0:1),outcome);
   var finalState=snapshot();check("exactly-ten-and-one-marker-after-race",((Number)finalState.get("points")).intValue()==10&&((Number)finalState.get("markerCount")).intValue()==1,finalState);observe("RACE_FINAL",Map.of("A_decision",commitA?"COMMIT":"ROLLBACK","database",finalState));
  }finally{pool.shutdownNow();pool.awaitTermination(5,TimeUnit.SECONDS);}
 }
 static void failures()throws Exception{
  fixture(false,0);boolean missingFailed=false;
  try(Connection c=db("mq05-missing-account")){try{apply(c,"missing-account");}catch(BusinessRowsException e){missingFailed=true;observe("EXPECTED_MISSING_ACCOUNT_FAILURE",Map.of("error",e.getMessage()));}}
  var missing=snapshot();check("missing-target-rolled-back-marker",missingFailed&&((Number)missing.get("markerCount")).intValue()==0&&((Number)missing.get("accountRows")).intValue()==0,missing);
  fixture(true,Integer.MAX_VALUE);String code="";
  try(Connection c=db("mq05-update-overflow")){try{apply(c,"integer-overflow");}catch(SQLException e){code=e.getSQLState();observe("EXPECTED_UPDATE_SQL_FAILURE",Map.of("SQLState",code,"error",e.getMessage()));}}
  var overflow=snapshot();check("update-error-rolled-back-marker-and-points","22003".equals(code)&&((Number)overflow.get("markerCount")).intValue()==0&&((Number)overflow.get("points")).longValue()==Integer.MAX_VALUE,overflow);
  fixture(true,0);try(Connection c=db("mq05-retry-after-failure")){var outcome=apply(c,"retry-after-failure");check("later-valid-attempt-can-acquire-key",(boolean)outcome.get("inserted"),outcome);}
 }
 static void verifyFinal()throws Exception{
  try(Admin a=Admin.create(adminProps())){
   var end=a.listOffsets(Map.of(P0,OffsetSpec.latest())).partitionResult(P0).get(20,TimeUnit.SECONDS).offset();check("Kafka-log-still-one-record-after-business-replays",end==1,end);
   for(boolean d:new boolean[]{false,true}){var offsets=a.listConsumerGroupOffsets(group(d)).partitionsToOffsetAndMetadata().get(20,TimeUnit.SECONDS);check("final-group-committed-one-"+d,offsets.get(P0).offset()==1,offsets.get(P0).offset());}
  }
  var s=snapshot();check("dedup-replay-final-ten-and-one-marker",((Number)s.get("points")).intValue()==10&&((Number)s.get("markerCount")).intValue()==1,s);
 }
 public static void main(String[] args)throws Exception{
  if(args.length!=4)throw new IllegalArgumentException("mode bootstrap pgurl suffix");bootstrap=args[1];pgurl=args[2];suffix=args[3];String mode=args[0];Class.forName("org.postgresql.Driver");
  observe("VERSIONS",Map.of("mode",mode,"kafka",AppInfoParser.getVersion(),"KafkaCommit",AppInfoParser.getCommitId(),"java",System.getProperty("java.version")));
  check("Kafka-client-4.4.0","4.4.0".equals(AppInfoParser.getVersion()),AppInfoParser.getVersion());
  try(Connection c=db("mq05-version")){check("PostgreSQL18.0",number(c,"SHOW server_version_num")==180000,c.getMetaData().getDatabaseProductVersion());observe("DATABASE_VERSION",Map.of("server",c.getMetaData().getDatabaseProductVersion(),"JDBC",c.getMetaData().getDriverVersion(),"isolation",c.getTransactionIsolation()));}
  switch(mode){case "setup"->setup();case "db-concurrency"->{race(true);race(false);failures();}case "reset"->fixture(true,0);case "naive-crash"->worker(false,true);case "naive-replay"->worker(false,false);case "dedup-crash"->worker(true,true);case "dedup-replay"->worker(true,false);case "verify-final"->verifyFinal();default->throw new IllegalArgumentException(mode);}
  System.out.println("RESULT PASS mode="+mode+" assertions="+assertions);
 }
}
