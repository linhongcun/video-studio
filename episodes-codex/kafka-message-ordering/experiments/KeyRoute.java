import java.util.HexFormat;
import org.apache.kafka.common.serialization.StringSerializer;
import org.apache.kafka.common.utils.Utils;
import org.apache.kafka.clients.producer.internals.BuiltInPartitioner;
public class KeyRoute {
 public static void main(String[] args) {
  var serializer=new StringSerializer();byte[] key=serializer.serialize("orders", "7042");
  int raw=Utils.murmur2(key),positive=Utils.toPositive(raw),partition=BuiltInPartitioner.partitionForKey(key,2);
  System.out.println("key=7042 utf8Hex="+HexFormat.of().formatHex(key)+" murmur2Signed="+raw+" positive="+positive+" partitions=2 selected="+partition);
  System.out.println("loaded="+BuiltInPartitioner.class.getProtectionDomain().getCodeSource().getLocation());
  if(partition!=positive%2)throw new AssertionError();
 }
}
