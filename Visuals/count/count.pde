int width = 220;
int height = 360;
float theScale = 1;

int segmentCount = 0;
int maxAnimation = 60;
int frames = 30;

PFont font;

boolean firstDraw = true;

int count = 0; 

int colorCounter = 0;

color[] colors = new color[4];

color the_color = color(255,0,0);

PrintWriter logger;

//MQTT Parameters
private MQTTLib m;
private String MQTT_BROKER ="tcp://localhost:1883";
private String CLIENT_ID = "Processing-Count";
private int[] QOS = {1};
private String[] TOPICS = {"smiles"};
private boolean CLEAN_START = true;
private short KEEP_ALIVE = 30;


void setup(){

 size(width, height);
 background(0);
 frameRate(frames);
 
 font = loadFont("HelveticaNeue-CondensedBold-80.vlw");
 
  //colour choices - https://kuler.adobe.com/#themeID/2362707
colors[0] = color(0,161,154);
colors[1] = color(4,191,157);
colors[2] = color(242,232,92);
colors[3] = color(245,61,84);
 
 m = new MQTTLib(MQTT_BROKER, new MessageHandler());
 m.connect(CLIENT_ID, CLEAN_START, KEEP_ALIVE);
 m.subscribe(TOPICS, QOS);
 
 logger = createWriter(year() + "-" + month()  + "-" + day() + "/" + hour() + "_" + minute() + "_log.txt");

 
}

void draw(){

  background(39,39,38);
  smooth();
  //stroke(210, 123, 34);
  fill(the_color);
  textFont(font, 80);
  textAlign(CENTER);
  text(str(count), ((width/2)), (height/2));
        
  }

void keyPressed() {

    createSmile();
}



void createSmile(){
    count++;
    
    colorCounter++;
       if (colorCounter == colors.length){
           colorCounter = 0;
       }
    
       the_color = colors[colorCounter];
       
   logger.println(hour() + ":" + minute() + ":" + second() + "." + millis());
   logger.flush();
}

private class MessageHandler implements MqttSimpleCallback {
public void connectionLost() throws Exception {
 System.out.println( "Connection has been lost." );
 //do something here
 }
public void publishArrived( String topicName, byte[] payload, int QoS, boolean retained ){
 String s = new String(payload);
 //Display the string
 createSmile();
 } 

 }

void stop() {
  logger.close();
  super.stop();
} 
