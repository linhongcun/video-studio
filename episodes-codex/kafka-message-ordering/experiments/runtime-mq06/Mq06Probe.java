import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicReference;
import org.apache.kafka.clients.admin.Admin;
import org.apache.kafka.clients.consumer.*;
import org.apache.kafka.clients.producer.*;
import org.apache.kafka.common.TopicPartition;

/** Same real log, two actual application schedules; no database/money effects. */
public class Mq06Probe extends KafkaProbeSupport {
 static String id(ConsumerRecord<String,String> r)throws Exception{return JSON.readTree(r.value()).get("eventId").asText();}
 static String status(ConsumerRecord<String,String> r)throws Exception{return JSON.readTree(r.value()).get("status").asText();}
 public static void main(String[] args)throws Exception{
  initialize(args,"mq06");String key="7042";byte[] utf=key.getBytes(StandardCharsets.UTF_8);
  check("key-UTF8-bytes",Arrays.equals(utf,new byte[]{55,48,52,50}),utf);
  observe("PRODUCER_CONFIG",new TreeMap<>(producerProps()));List<RecordMetadata> metadata=new ArrayList<>();
  try(KafkaProducer<String,String> p=new KafkaProducer<>(producerProps())){
   for(String[] e:new String[][]{{"E01","PAID"},{"E02","REFUNDED"}}){
    String value="{\"eventId\":\""+e[0]+"\",\"orderId\":\"7042\",\"status\":\""+e[1]+"\"}";
    // One calling thread; await E01 confirmation before invoking E02 send.
    var m=p.send(new ProducerRecord<>(TOPIC,key,value)).get(30,TimeUnit.SECONDS);metadata.add(m);
    observe("PRODUCE_CONFIRMED",Map.of("eventId",e[0],"key",key,"partition",m.partition(),"offset",m.offset(),"payload",value));
   }
  }
  int partition=metadata.get(0).partition();check("actual-same-key-partition",metadata.get(1).partition()==partition,metadata.stream().map(m->Map.of("partition",m.partition(),"offset",m.offset())).toList());
  check("actual-log-positions-zero-one",metadata.get(0).offset()==0&&metadata.get(1).offset()==1,metadata.stream().map(RecordMetadata::offset).toList());
  List<ConsumerRecord<String,String>> delivered=new ArrayList<>();
  observe("CONSUMER_CONFIG",new TreeMap<>(consumerProps("mq06-"+suffix,"mq06-single-poll-thread")));
  try(KafkaConsumer<String,String> c=new KafkaConsumer<>(consumerProps("mq06-"+suffix,"mq06-single-poll-thread"))){
   c.subscribe(List.of(TOPIC));long deadline=System.nanoTime()+TimeUnit.SECONDS.toNanos(45);
   while(delivered.size()<2&&System.nanoTime()<deadline){var rows=c.poll(Duration.ofMillis(200));for(var row:rows){delivered.add(row);observe("POLL_DELIVERED",record(row));}}
   check("two-records-actually-polled",delivered.size()==2,delivered.size());
   check("poll-preserves-this-partition-order",id(delivered.get(0)).equals("E01")&&id(delivered.get(1)).equals("E02")&&delivered.get(0).offset()==0&&delivered.get(1).offset()==1&&delivered.stream().allMatch(r->r.partition()==partition),delivered.stream().map(KafkaProbeSupport::record).toList());
   check("poll-position-two",c.position(new TopicPartition(TOPIC,partition))==2,c.position(new TopicPartition(TOPIC,partition)));
  }
  AtomicReference<String> projection=new AtomicReference<>("PENDING");List<String> serial=new ArrayList<>();
  for(var row:delivered){projection.set(status(row));serial.add(id(row));observe("SERIAL_COMPLETE",Map.of("eventId",id(row),"projection",projection.get()));}
  check("serial-completes-E01-then-E02",serial.equals(List.of("E01","E02"))&&projection.get().equals("REFUNDED"),Map.of("completionOrder",serial,"finalProjection",projection.get()));
  projection.set("PENDING");observe("PROJECTION_RESET_SAME_INPUT",Map.of("projection",projection.get(),"source","same two previously polled ConsumerRecords, no new Produce"));
  List<String> async=new CopyOnWriteArrayList<>();CountDownLatch paymentStarted=new CountDownLatch(1),allowPaymentWrite=new CountDownLatch(1),allowRefundWrite=new CountDownLatch(1),refundDone=new CountDownLatch(1);
  ExecutorService pool=Executors.newFixedThreadPool(2);List<Future<?>> work=new ArrayList<>();
  try{
   // The one application dispatch thread submits the actual poll list in E01/E02 order.
   for(var row:delivered){String event=id(row);observe("ASYNC_SUBMIT",Map.of("eventId",event,"offset",row.offset()));
    if(event.equals("E01"))work.add(pool.submit(()->{paymentStarted.countDown();if(!allowPaymentWrite.await(10,TimeUnit.SECONDS))throw new AssertionError("payment release timeout");projection.set(status(row));async.add(event);observe("ASYNC_COMPLETE",Map.of("eventId",event,"projection",projection.get()));return null;}));
    else work.add(pool.submit(()->{if(!paymentStarted.await(10,TimeUnit.SECONDS)||!allowRefundWrite.await(10,TimeUnit.SECONDS))throw new AssertionError("refund release timeout");projection.set(status(row));async.add(event);observe("ASYNC_COMPLETE",Map.of("eventId",event,"projection",projection.get()));refundDone.countDown();return null;}));
   }
   check("payment-started-before-writing",paymentStarted.await(5,TimeUnit.SECONDS)&&projection.get().equals("PENDING"),projection.get());
   allowRefundWrite.countDown();check("refund-completes-before-payment-write",refundDone.await(5,TimeUnit.SECONDS)&&projection.get().equals("REFUNDED"),Map.of("projection",projection.get(),"completionOrder",async));
   allowPaymentWrite.countDown();for(var f:work)f.get(5,TimeUnit.SECONDS);
   check("async-completion-reverses-despite-same-log",async.equals(List.of("E02","E01"))&&projection.get().equals("PAID"),Map.of("completionOrder",async,"finalProjection",projection.get()));
  }finally{allowPaymentWrite.countDown();allowRefundWrite.countDown();pool.shutdownNow();pool.awaitTermination(5,TimeUnit.SECONDS);}
  try(Admin a=Admin.create(adminProps())){var end=ends(a);check("log-unchanged-by-application-schedule",end.get(partition)==2&&end.get(1-partition)==0,end);observe("FINAL_LOG_ENDS",end);}
  observe("SCOPE",Map.of("realLog","Kafka4.4 orders,2 partitions,one producer/calling thread,key UTF8 7042","business","real Java AtomicReference status projection and deterministic CountDownLatch scheduling; no payment/refund service or database executed","benchmark",false));done("mq06");
 }
}
