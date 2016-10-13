import oscP5.*;
import netP5.*;
import java.util.ArrayList;
import java.util.LinkedList;

boolean bOSC = true;

float alpha           = .9;
float fHeightFactor   = .15;

int scapes = 8;
int scape_length = 1024;

boolean bGaus     = true;
boolean bDouble   = false;
boolean bAngle    = true;

float[][] fft;
int[] offsets;

int counter = 0;

float depth_dif;
float move_speed = 0.;
long last_time = millis();

OscP5 oscP5;

void setup()
{
  //  frameRate(10);
  if (bOSC)
    oscP5 = new OscP5(this, 7110);

  //size(displayWidth, displayHeight);
  fullScreen(3);
  
  depth_dif = height * 1.4;

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
  for (int i = 0; i < scapes; i++) {
    fill(0, 255 / scapes);
    noStroke();
    rect(0, 0, width, height);
    float depth = 1. - i / (float)scapes; 
    draw_landscape( (counter + i ) % scapes, depth );
  }
}

float gauss(float x)
{
  float b = .5;
  float c = .25;
  float a = 1/(c*sqrt(2*PI));
  return a * exp(-pow( x - b, 2) / (2 * c * c) );
}

void tex(float x, float y)
{
   vertex(x,y);
//  curveVertex(x,y); 
}

void do_vertex(float xOff, int i, int index, float step_size, float depth, float depth_dif)
{
  float val = fft[index][(i + offsets[index]) % scape_length];
  //  float val = fft[index][(i)];
  if (bDouble)
    val -= .5;
  if (bGaus)
    val *= pow(gauss((float)i/scape_length), 2);

  val *= height * fHeightFactor * (pow(1. - depth, 4) + .2) / 1.2;

  val += (pow(depth, .25)) * depth_dif - height * .7;

  tex( 
  (float)xOff + i * step_size, 
  height * 1. - val 
    );
}

void draw_landscape(int index, float depth)
{

  float vis_width;
  if (bAngle)
    vis_width = width / (.5 + pow(depth, 2) * 2.);
  else
    vis_width = width / (.5 + pow(depth, 1/2) * 2.);
  float xOff = (width - vis_width) / 2.;
  float step_size = vis_width / scape_length;

  fill(0, 0, 0, 255);
  noStroke();
  beginShape();
  tex(0, height);
  tex(0, height);
  do_vertex(xOff, 0, index, step_size, depth, depth_dif);
  do_vertex(xOff, 0, index, step_size, depth, depth_dif);
  for (int i = 0; i < scape_length; i++) {
    do_vertex(xOff, i, index, step_size, depth, depth_dif);
  }
  do_vertex(xOff, scape_length-1, index, step_size, depth, depth_dif);
  do_vertex(xOff, scape_length-1, index, step_size, depth, depth_dif);
  tex(width, height);
  tex(width, height);
  endShape();

  strokeWeight((float)(2. + -1. * depth));
  noFill();
  stroke((1. + -.25 * depth) * 255.);

  beginShape();
  do_vertex(xOff, 0, index, step_size, depth, depth_dif);
  for (int i = 0; i < scape_length; i++) {
    do_vertex(xOff, i, index, step_size, depth, depth_dif);
  }
  do_vertex(xOff, scape_length-1, index, step_size, depth, depth_dif);
  endShape();
}

void push_data(int index, float value)
{
  offsets[index] = (offsets[index] + scape_length - 1) % scape_length;
  fft[index][offsets[index]] = value;
}

/* incoming osc message are forwarded to the oscEvent method. */
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
  else if (pat.startsWith("/EEG_1/channel_1"))
  {
    push_data(1, value);
  }
  else if (pat.startsWith("/EEG_0/channel_2"))
  {
    push_data(2, value);
  }
  else if (pat.startsWith("/EEG_1/channel_2"))
  {
    push_data(3, value);
  }
  else if (pat.startsWith("/EEG_0/channel_3"))
  {
    push_data(4, value);
  }
  else if (pat.startsWith("/EEG_1/channel_3"))
  {
    push_data(5, value);
  }
  else if (pat.startsWith("/EEG_0/channel_4"))
  {
    push_data(6, value);
  }
  else if (pat.startsWith("/EEG_1/channel_4"))
  {
    push_data(7, value);
  }
}


void keyPressed()
{
  switch(key)
  {
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