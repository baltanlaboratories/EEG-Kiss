
import oscP5.*;
import netP5.*;
import java.util.ArrayList;
import java.util.LinkedList;


boolean bOSC = true;
boolean visualRadar = true;

float alpha           = 1.; //.9;
float fHeightFactor   = .15; //.15;

int scapes = 8;
int scape_length = 1024;

boolean bGaus     = true;
boolean bDouble   = false;
boolean bAngle    = true;

float[][] fft;
int[] offsets;
int[] count;

int counter = 0;

float move_speed = 0.;
long last_time = millis();

OscP5 oscP5;

void setup()
{
  if (bOSC)
    oscP5 = new OscP5(this, 7110);

  //size(displayWidth, displayHeight);//, OPENGL );
  //surface.setSize(displayWidth, displayHeight);
  fullScreen(3);
  //frame.setResizable(true);  
  
  move_speed = 2000 * 16 / scapes;

  last_time = millis();
  background(200, 200, 200, .1);
  smooth(4);
  hint(DISABLE_OPTIMIZED_STROKE);
  lights();

  reset();
}

void reset()
{
  fft = new float[scapes][scape_length];
  offsets = new int[scapes];
  count = new int[scapes];
  for (int i = 0; i < scape_length; i++) {
    for (int j = 0; j < scapes; j++) {
      float off = 0.;
      if (i>0) {
        off = fft[j][i-1]; 
        fft[j][i] = bOSC ? 0 : random(1.)*alpha + off*(1.-alpha);
      }
    }
  }
}

void draw()
{
  // achtergrond fade
  float alpha = 4; // dekking 0 - 255
  fill(0, 0, 0, alpha);
  stroke(0, 0, 0, 0);
  rect(0, 0, width, height);
  
  strokeWeight(1);
  fill(255);

  for (int i = 0; i < scapes; i++)
  {
    //push_data(i, random(1.));
    init_circle(i);
    draw_circle(i, count[i]);
    count[i] = 0;
  }
}

void init_circle(int index)
{
//  println("index: " + index + "  index/4: " + index / 4);
  
  switch (index / 4)
  {
    case 1:
      stroke(0,255,0);
      break;
    case 2:
      stroke(255,0,0);
      break;
    case 3:
      stroke(255,0,0);
      break;
    default:
      stroke(255);
      break;
  }
}

void draw_circle(int index, int count)
{
  float dx, dy, x_off, y_off, r_off, r_weight;

  dx        = 0;
  dy        = 0;
  x_off     = width / 2.;
  y_off     = height / 2.;
  //r_off     = 100 + (index % 4) * 100;
  r_off     = 20 + (index % 4) * 100;
  r_weight  = 75.;

  //  for (int i = 0; i < scape_length; i++) {
  for (int j = 0; j < count + 1; j++) {
    int i;
    float t, x, y, r;

    i = (offsets[index] + scape_length + j) % scape_length;

    // R cos ( w t )
    t = (float)i / scape_length * PI * 2;
    r = r_off + r_weight * fft[index][i];
    x = r * cos(t) + x_off;
    y = r * sin(t) + y_off;

    if (j > 0)
    {
      line(dx, dy, x, y);
      //ellipse(x, y, 1, 1);
    }
    dx = x;
    dy = y;
  }
}

float gauss(float x)
{
  float b = .5;
  float c = .25;
  float a = 1/(c*sqrt(2*PI));
  return a * exp(-pow( x - b, 2) / (2 * c * c) );
}

void push_data(int index, float value)
{
  if (index >= scapes)
  {
    return;
  }
  
  offsets[index] = (offsets[index] + scape_length - 1) % scape_length;
  fft[index][offsets[index]] = value;
  
  ++count[index];

  println("index: " + index + "  value: " + value + "  count: " + count[index]);
}

/* incoming osc message are forwarded to this oscEvent method. */
void oscEvent(OscMessage theOscMessage)
{
  String pat = theOscMessage.addrPattern(); 
  float value=0.;
  
  if (theOscMessage.typetag().equals("i"))
  {
    println("Type was int");
    value = (float)theOscMessage.get(0).intValue();
  }
  else if (theOscMessage.typetag().equals("f"))
  {
    println("Type was float");
    println("Value send: " + theOscMessage);
    value = theOscMessage.get(0).floatValue();
  }
  else
  {
    println("Type was: " + theOscMessage.typetag());
  }

  if (pat.startsWith("/EEG_0/channel_1"))
  { 
    push_data(0, value);
  }
  else if (pat.startsWith("/EEG_0/channel_2"))
  {
    push_data(1, value);
  }
  else if (pat.startsWith("/EEG_0/channel_3"))
  {
    push_data(2, value);
  }
  else if (pat.startsWith("/EEG_0/channel_4"))
  {
    push_data(3, value);
  }
  else if (pat.startsWith("/EEG_1/channel_1"))
  {
    push_data(4, value);
  }
  else if (pat.startsWith("/EEG_1/channel_2"))
  {
    push_data(5, value);
  }
  else if (pat.startsWith("/EEG_1/channel_3"))
  {
    push_data(6, value);
  }
  else if (pat.startsWith("/EEG_1/channel_4"))
  {
    push_data(7, value);
  }
}


void keyPressed() {
  switch(key)
  {
  case 'f':
    fullScreen(3);
    break;
  case ' ':
    saveFrame("EEG-landscape-######.jpg");
    return;
  case 'g':
    bGaus = !bGaus;
    break;
  case 'd':
    bDouble = !bDouble;
    break;
  case 'a':
    bAngle = !bAngle;
    break;
  case 's':
    scapes = scapes == 4 ? 8 : 4;
    break;
  case 'h':
    fHeightFactor = fHeightFactor < .1 ? .15 : .05;
    break;
  default:
    return;
  } 
  reset();
}

//boolean sketchFullScreen()
//{
//  return false;
//}