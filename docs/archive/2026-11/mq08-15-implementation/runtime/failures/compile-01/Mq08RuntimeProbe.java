import java.time.Duration;
import java.util.*;
import java.util.concurrent.TimeUnit;
import org.apache.kafka.clients.admin.*;
import org.apache.kafka.clients.consumer.*;
import org.apache.kafka.clients.producer.*;
import org.apache.kafka.common.TopicPartition;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.apache.kafka.common.serialization.StringSerializer;
import org.apache.kafka.common.utils.AppInfoParser;

/** Independent real-broker setup/inspection. Does not implement the worker's retry policy. */
public final class Mq08RuntimeProbe {
  static String esc(String x) { return "\""+x.replace("\\","\\\\").replace("\"","\\\"").replace("\n","\\n").replace("\r","\\r")+"\""; }
  static String json(Object x) {
    if(x==null)return "null";
    if(x instanceof Number || x instanceof Boolean)return x.toString();
    if(x instanceof Map<?,?> m){var a=new ArrayList<String>();m.forEach((k,v)->a.add(esc(k.toString())+":"+json(v)));return "{"+String.join(",",a)+"}";}
    if(x instanceof Collection<?> c){var a=new ArrayList<String>();c.forEach(v->a.add(json(v)));return "["+String.join(",",a)+"]";}
    return esc(x.toString());
  }
  static Map<String,Object> obj(Object... p){var m=new LinkedHashMap<String,Object>();for(int i=0;i<p.length;i+=2)m.put(p[i].toString(),p[i+1]);return m;}
  static Properties props(String bootstrap){var p=new Properties();p.put("bootstrap.servers",bootstrap);p.put("request.timeout.ms","3000");p.put("default.api.timeout.ms","15000");p.put("client.id","mq08-independent-runtime-probe");return p;}
  static void create(Admin a,String topic)throws Exception{a.createTopics(List.of(new NewTopic(topic,1,(short)1))).all().get(15,TimeUnit.SECONDS);}
  static void ready(Admin a,String topic)throws Exception{long until=System.nanoTime()+15_000_000_000L;while(true){var t=a.describeTopics(List.of(topic)).allTopicNames().get(5,TimeUnit.SECONDS).get(topic);if(t.partitions().get(0).leader()!=null&&t.partitions().get(0).leader().id()>=0)return;if(System.nanoTime()>until)throw new AssertionError("No leader");Thread.sleep(100);}}
  static void emit(Map<String,Object>x){System.out.println(json(x));}
  public static void main(String[] args)throws Exception{
    String mode=args[0],bootstrap=args[1];var p=props(bootstrap);
    try(Admin a=Admin.create(p)){
      if(mode.equals("ready")){
        var nodes=a.describeCluster().nodes().get(4,TimeUnit.SECONDS);var features=a.describeFeatures().featureMetadata().get(4,TimeUnit.SECONDS);var f=new TreeMap<String,Object>();features.finalizedFeatures().forEach((k,v)->f.put(k,obj("min",v.minVersionLevel(),"max",v.maxVersionLevel())));emit(obj("version",AppInfoParser.getVersion(),"commit",AppInfoParser.getCommitId(),"nodes",nodes.toString(),"features",f));return;
      }
      String topic=args[2],dlq=args[3],group=args[4];var tp=new TopicPartition(topic,0);
      if(mode.equals("seed")){
        create(a,topic);if(Boolean.parseBoolean(args[5]))create(a,dlq);ready(a,topic);
        var pp=props(bootstrap);pp.put("acks","all");pp.put("enable.idempotence","true");pp.put("key.serializer",StringSerializer.class);pp.put("value.serializer",StringSerializer.class);var sent=new ArrayList<Object>();
        try(var producer=new KafkaProducer<String,String>(pp)){for(String id:List.of("E01","E02")){var md=producer.send(new ProducerRecord<>(topic,0,"7042","{\"eventId\":\""+id+"\",\"orderId\":7042}")).get(10,TimeUnit.SECONDS);sent.add(obj("eventId",id,"partition",md.partition(),"offset",md.offset()));}}
        a.alterConsumerGroupOffsets(group,Map.of(tp,new OffsetAndMetadata(0))).all().get(15,TimeUnit.SECONDS);emit(obj("mode",mode,"sent",sent,"initialCommitted",0));return;
      }
      if(mode.equals("create-dlq")){create(a,dlq);ready(a,dlq);emit(obj("created",dlq));return;}
      if(mode.equals("wait-empty")){
        long start=System.nanoTime(),until=start+25_000_000_000L;int observations=0;var history=new ArrayList<Object>();
        while(true){var d=a.describeConsumerGroups(List.of(group)).all().get(5,TimeUnit.SECONDS).get(group);observations++;history.add(obj("state",d.groupState().toString(),"members",d.members().size()));if(d.members().isEmpty()){emit(obj("empty",true,"elapsedMs",(System.nanoTime()-start)/1_000_000,"observations",observations,"history",history));return;}if(System.nanoTime()>until)throw new AssertionError("Old halted member still active");Thread.sleep(200);}
      }
      if(!mode.equals("inspect"))throw new IllegalArgumentException(mode);
      var offsets=a.listConsumerGroupOffsets(group).partitionsToOffsetAndMetadata().get(10,TimeUnit.SECONDS);var names=a.listTopics().names().get(10,TimeUnit.SECONDS);boolean exists=names.contains(dlq);var parts=new ArrayList<TopicPartition>();parts.add(tp);if(exists)parts.add(new TopicPartition(dlq,0));var latest=new HashMap<TopicPartition,OffsetSpec>();for(var part:parts)latest.put(part,OffsetSpec.latest());var ends=a.listOffsets(latest).all().get(10,TimeUnit.SECONDS);var logs=new LinkedHashMap<String,Object>();
      var cp=props(bootstrap);cp.put("group.id",group+"-inspection-no-join");cp.put("enable.auto.commit","false");cp.put("auto.offset.reset","earliest");cp.put("allow.auto.create.topics","false");cp.put("key.deserializer",StringDeserializer.class);cp.put("value.deserializer",StringDeserializer.class);
      try(var consumer=new KafkaConsumer<String,String>(cp)){
        consumer.assign(parts);consumer.seekToBeginning(parts);var collected=new LinkedHashMap<String,List<Object>>();for(var part:parts)collected.put(part.topic(),new ArrayList<>());long until=System.nanoTime()+10_000_000_000L;
        while(true){boolean all=true;for(var part:parts)if(consumer.position(part)<ends.get(part).offset())all=false;if(all)break;if(System.nanoTime()>until)throw new AssertionError("Inspection timeout");for(var rec:consumer.poll(Duration.ofMillis(100)))collected.get(rec.topic()).add(obj("topic",rec.topic(),"partition",rec.partition(),"offset",rec.offset(),"key",rec.key(),"value",rec.value()));}
        for(var part:parts)logs.put(part.topic(),obj("endOffset",ends.get(part).offset(),"records",collected.get(part.topic())));
      }
      var desc=a.describeTopics(List.of(topic)).allTopicNames().get(10,TimeUnit.SECONDS).get(topic).partitions().get(0);emit(obj("mode",mode,"committed",offsets.containsKey(tp)?offsets.get(tp).offset():null,"dlqExists",exists,"leader",desc.leader().id(),"isr",desc.isr().stream().map(n->n.id()).toList(),"logs",logs));
    }
  }
}
