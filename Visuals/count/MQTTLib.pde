import com.ibm.mqtt.MqttClient;
import com.ibm.mqtt.MqttSimpleCallback;
import com.ibm.mqtt.MqttException;
 public class MQTTLib {
 private MqttSimpleCallback callback;
 private MqttClient client = null;

 MQTTLib(String broker, MqttSimpleCallback p) {
 callback = p;
 try {
 client = (MqttClient) MqttClient.createMqttClient(broker, null);
 //class to call on disconnect or data received
 client.registerSimpleHandler(callback);
 } catch (MqttException e) {
 System.out.println( e.getMessage() );
 }
 }

 public boolean connect(String client_id, boolean clean_start, short keep_alive) {

 try {
 //connect - clean_start=true drops all subscriptions, keep-alive is the heart-beat
 client.connect(client_id, clean_start, keep_alive);
 print("connected");
 //subscribe to TOPIC
 return true;
 } catch (MqttException e) {
 System.out.println( e.getMessage() );
 return false;
 }
 }

 public boolean subscribe(String[] topics, int[] qos ) {
 try {
 //subscribe to TOPIC
 client.subscribe(topics, qos);
 return true;
 } catch (MqttException e) {
 System.out.println( e.getMessage() );
 return false;
 }
 }

}
