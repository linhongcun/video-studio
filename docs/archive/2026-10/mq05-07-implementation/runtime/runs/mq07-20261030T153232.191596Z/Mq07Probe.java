import java.time.Duration;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import org.apache.kafka.clients.admin.*;
import org.apache.kafka.clients.consumer.*;
import org.apache.kafka.clients.producer.*;
import org.apache.kafka.common.TopicPartition;
import org.apache.kafka.common.errors.WakeupException;

/** Stable dynamic-group ownership and a separately controlled business gate. */
public class Mq07Probe extends KafkaProbeSupport {
 static class Worker implements Runnable {
  final String client,group;final AtomicBoolean stop=new AtomicBoolean(false);
  final AtomicReference<Set<TopicPartition>> installed=new AtomicReference<>(Set.of());
  volatile KafkaConsumer<String,String> consumer;volatile Throwable error;
  Worker(String group,String client){this.group=group;this.client=client;}
  public void run(){try(KafkaConsumer<String,String> c=new KafkaConsumer<>(consumerProps(group,client))){consumer=c;c.subscribe(List.of(TOPIC));while(!stop.get()){var rows=c.poll(Duration.ofMillis(150));installed.set(Set.copyOf(c.assignment()));if(!rows.isEmpty())throw new AssertionError("Assignment fixture topic must still be empty");}}catch(WakeupException e){if(!stop.get())error=e;}catch(Throwable e){error=e;}finally{consumer=null;}}
  void shutdown(){stop.set(true);var c=consumer;if(c!=null)c.wakeup();}
 }
 static ConsumerGroupDescription stable(Admin a,String group,List<Worker> workers,int n)throws Exception{
  long deadline=System.nanoTime()+TimeUnit.SECONDS.toNanos(60);
  while(System.nanoTime()<deadline){
   for(var w:workers)if(w.error!=null)throw new RuntimeException(w.client,w.error);
   ConsumerGroupDescription g;
   try{g=a.describeConsumerGroups(List.of(group)).all().get(10,TimeUnit.SECONDS).get(group);}
   catch(ExecutionException e){observe("WAIT_GROUP_STATE",Map.of("membersExpected",n,"cause",e.getCause().getClass().getSimpleName()));TimeUnit.MILLISECONDS.sleep(50);continue;}
   if(g.members().size()==n&&g.groupState().toString().equals("Stable")){
    boolean installed=true;
    for(var m:g.members()){var w=workers.stream().filter(x->x.client.equals(m.clientId())).findFirst().orElseThrow();if(!w.installed.get().equals(m.assignment().topicPartitions()))installed=false;}
    if(installed)return g;
   }
   // Observation polling only; this does not define membership or business order.
   TimeUnit.MILLISECONDS.sleep(50);
  }
  throw new AssertionError("No real stable/installed group of"+n);
 }
 static List<Map<String,Object>> members(ConsumerGroupDescription g){return g.members().stream().sorted(Comparator.comparing(MemberDescription::consumerId)).map(m->Map.<String,Object>of("memberId",m.consumerId(),"clientId",m.clientId(),"groupInstanceId",m.groupInstanceId().orElse("absent"),"partitions",m.assignment().topicPartitions().stream().map(TopicPartition::partition).sorted().toList())).toList();}
 static void assignment()throws Exception{
  String group="mq07-scale-"+suffix;List<Worker> workers=new ArrayList<>();List<Thread> threads=new ArrayList<>();
  observe("SCALE_CONSUMER_CONFIG",new TreeMap<>(consumerProps(group,"example-only")));
  try(Admin a=Admin.create(adminProps())){
   for(String id:List.of("mq07-original-A","mq07-original-B")){var w=new Worker(group,id);workers.add(w);var t=new Thread(w,id);threads.add(t);t.start();}
   var two=stable(a,group,workers,2);var before=members(two);observe("STABLE_TWO_DYNAMIC_MEMBERS",before);
   check("two-members-cover-two-partitions",two.members().stream().allMatch(m->m.assignment().topicPartitions().size()==1),before);
   for(int i=3;i<=12;i++){var w=new Worker(group,String.format("mq07-added-%02d",i));workers.add(w);var t=new Thread(w,w.client);threads.add(t);t.start();}
   var twelve=stable(a,group,workers,12);var after=members(twelve);observe("STABLE_TWELVE_DYNAMIC_MEMBERS",after);
   var sizes=twelve.members().stream().map(m->m.assignment().topicPartitions().size()).sorted().toList();
   check("twelve-members-only-two-nonempty",sizes.equals(List.of(0,0,0,0,0,0,0,0,0,0,1,1)),sizes);
   Set<TopicPartition> union=new HashSet<>();int total=0;for(var m:twelve.members()){union.addAll(m.assignment().topicPartitions());total+=m.assignment().topicPartitions().size();}
   check("exclusive-complete-two-partition-ownership",total==2&&union.equals(Set.of(P0,P1)),after);
   check("actual-members-dynamic-not-static",twelve.members().stream().allMatch(m->m.groupInstanceId().isEmpty()),after);
   check("Broker-observes-range-assignor","range".equals(twelve.partitionAssignor()),twelve.partitionAssignor());
   var ordered=twelve.members().stream().sorted(Comparator.comparing(MemberDescription::consumerId)).toList();
   check("Range-follows-current-member-order",ordered.get(0).assignment().topicPartitions().equals(Set.of(P0))&&ordered.get(1).assignment().topicPartitions().equals(Set.of(P1))&&ordered.subList(2,12).stream().allMatch(m->m.assignment().topicPartitions().isEmpty()),after);
   observe("MEMBERSHIP_CHANGE_OBSERVATION",Map.of("before",before,"after",after,"scope","Ownership identities derived from actual current members; no assumption original two retain partitions."));
   check("assignment-fixture-has-no-records",ends(a).equals(Map.of(0,0L,1,0L)),ends(a));
  }finally{
   for(var w:workers)w.shutdown();for(var t:threads)t.join(15000);
   check("all-twelve-owned-worker-threads-stopped",threads.stream().noneMatch(Thread::isAlive),threads.stream().map(t->t.getName()+":"+t.isAlive()).toList());
   for(var w:workers)if(w.error!=null)throw new RuntimeException(w.client,w.error);
  }
 }
 static void businessGate()throws Exception{
  // Separate single-member classic group; the12-member assignment fixture is closed.
  try(KafkaProducer<String,String> p=new KafkaProducer<>(producerProps())){
   for(int i=0;i<2;i++){String id=i==0?"E01":"E02";var m=p.send(new ProducerRecord<>(TOPIC,i,"7042",id)).get(20,TimeUnit.SECONDS);check("seed-business-P"+i+"-offset0",m.partition()==i&&m.offset()==0,Map.of("partition",m.partition(),"offset",m.offset(),"eventId",id));}
  }
  String group="mq07-business-"+suffix;AtomicInteger polled=new AtomicInteger(),completed=new AtomicInteger();CountDownLatch handlersStarted=new CountDownLatch(2),releaseBusiness=new CountDownLatch(1);ExecutorService pool=Executors.newFixedThreadPool(2);List<Future<?>> jobs=new ArrayList<>();List<Map<String,Object>> actualRecords=new ArrayList<>();
  try(KafkaConsumer<String,String> c=new KafkaConsumer<>(consumerProps(group,"mq07-business-single-poll-thread"))){
   c.subscribe(List.of(TOPIC));List<ConsumerRecord<String,String>> early=new ArrayList<>();long deadline=System.nanoTime()+TimeUnit.SECONDS.toNanos(40);
   while(c.assignment().size()!=2&&System.nanoTime()<deadline){for(var row:c.poll(Duration.ofMillis(150)))early.add(row);}
   check("business-group-actual-two-partition-install",c.assignment().equals(Set.of(P0,P1)),c.assignment().toString());
   c.commitSync(Map.of(P0,new OffsetAndMetadata(0),P1,new OffsetAndMetadata(0)));
   // Retain any initialization-poll record, without discarding it or executing a handler.
   List<ConsumerRecord<String,String>> pending=new ArrayList<>(early);
   while(polled.get()<2&&System.nanoTime()<deadline){
    for(var row:pending){check("business-record-real-offset0",row.offset()==0,record(row));actualRecords.add(record(row));polled.incrementAndGet();
     jobs.add(pool.submit(()->{handlersStarted.countDown();if(!releaseBusiness.await(10,TimeUnit.SECONDS))throw new AssertionError("business gate timeout");completed.incrementAndGet();observe("BUSINESS_STEP_COMPLETED",Map.of("partition",row.partition(),"offset",row.offset(),"eventId",row.value()));return null;}));
    }
    pending.clear();if(polled.get()<2)for(var row:c.poll(Duration.ofMillis(150)))pending.add(row);
   }
   check("two-real-records-polled",polled.get()==2,actualRecords);check("two-business-tasks-started",handlersStarted.await(5,TimeUnit.SECONDS),handlersStarted.getCount());
   c.pause(c.assignment());c.poll(Duration.ZERO);
   var before=Map.of("polled",polled.get(),"completed",completed.get(),"positionP0",c.position(P0),"positionP1",c.position(P1),"committedP0",c.committed(Set.of(P0,P1)).get(P0).offset(),"committedP1",c.committed(Set.of(P0,P1)).get(P1).offset());
   observe("POLL_IS_NOT_BUSINESS_COMPLETION",before);
   check("business-blocked-after-actual-poll",polled.get()==2&&completed.get()==0,before);
   check("positions-advance-while-commits-still-zero",c.position(P0)==1&&c.position(P1)==1&&c.committed(Set.of(P0,P1)).values().stream().allMatch(x->x.offset()==0),before);
   releaseBusiness.countDown();for(var job:jobs)job.get(5,TimeUnit.SECONDS);
   check("release-completes-exactly-two-business-steps",completed.get()==2,completed.get());
   c.commitSync(Map.of(P0,new OffsetAndMetadata(1),P1,new OffsetAndMetadata(1)));
   check("commit-one-each-only-after-completion",c.committed(Set.of(P0,P1)).values().stream().allMatch(x->x.offset()==1),c.committed(Set.of(P0,P1)).toString());
   observe("BUSINESS_AND_OFFSET_FINAL",Map.of("polled",polled.get(),"completed",completed.get(),"committedP0",1,"committedP1",1));
  }finally{releaseBusiness.countDown();pool.shutdownNow();pool.awaitTermination(5,TimeUnit.SECONDS);}
 }
 public static void main(String[] args)throws Exception{
  initialize(args,"mq07");assignment();businessGate();
  observe("SCOPE",Map.of("assignment","Real Kafka4.4 classic Range,2 partitions,2 then12 dynamic members,stable+local-install observations","business","Separate one-member group, actual polled records and controlled Java handler completion gate, not a production business service","throughput","No benchmark, throughput rate, forecast or assumed-rate validation."));done("mq07");
 }
}
