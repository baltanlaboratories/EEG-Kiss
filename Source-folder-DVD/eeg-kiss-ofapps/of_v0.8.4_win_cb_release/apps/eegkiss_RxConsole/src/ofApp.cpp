#include "ofApp.h"
#include <string>


const int kOscReceivePort = 7110;

//--------------------------------------------------------------
void ofApp::setup(){
    ofSetFrameRate(24);

    // listen on the given port
	cout << "listening for osc messages on port " << kOscReceivePort << endl;
	msgCounter = 0;
	receiver.setup(kOscReceivePort);
	ofBackground(30, 30, 130);


}

//--------------------------------------------------------------
void ofApp::update(){

    	// check for waiting messages
	while(receiver.hasWaitingMessages()){
		// get the next message
		ofxOscMessage m;
		receiver.getNextMessage(&m);

		msgCounter++;
		//cout << "msgCounter: " << msgCounter << endl;

        float value = getOscArg(m, 0);
        //cout << value << endl;

        string channelName = m.getAddress();
        addValueToChannelBuffer(channelName, value);
	}

}

//--------------------------------------------------------------
void ofApp::draw(){
    ofSetColor(255, 255, 255);
    ofDrawBitmapString(ofToString((int)ofGetFrameRate())+"fps", 10, 15);

    eeg0chan1_Polyline.draw();
    eeg0chan2_Polyline.draw();
    eeg0chan3_Polyline.draw();
    eeg0chan4_Polyline.draw();
    eeg1chan4_Polyline.draw();
}

//--------------------------------------------------------------
void ofApp::keyPressed(int key){

}

//--------------------------------------------------------------
void ofApp::keyReleased(int key){

}

//--------------------------------------------------------------
void ofApp::mouseMoved(int x, int y ){

}

//--------------------------------------------------------------
void ofApp::mouseDragged(int x, int y, int button){

}

//--------------------------------------------------------------
void ofApp::mousePressed(int x, int y, int button){

}

//--------------------------------------------------------------
void ofApp::mouseReleased(int x, int y, int button){

}

//--------------------------------------------------------------
void ofApp::windowResized(int w, int h){

}

//--------------------------------------------------------------
void ofApp::gotMessage(ofMessage msg){

}

//--------------------------------------------------------------
void ofApp::dragEvent(ofDragInfo dragInfo){

}

/***************************************************************
 * Read an argument from a received ofxOscMessage as float.
 **************************************************************/
float ofApp::getOscArg(const ofxOscMessage& m, int argIndex)
{
    float value=0.0;
    switch (m.getArgType(argIndex))
    {
    case OFXOSC_TYPE_INT32:
        //cout << "int32" << endl;
        value = m.getArgAsInt32(argIndex);
        break;
    case OFXOSC_TYPE_INT64:
        //cout << "int64" << endl;
        value = m.getArgAsInt64(argIndex);
        break;
    case OFXOSC_TYPE_FLOAT:
        //cout << "float" << endl;
        value = m.getArgAsFloat(argIndex);
        break;
    default:
        //cout << "unsupported type: " << m.getArgType(argIndex) << endl;
        break;
    }

    return value;

}

/***************************************************************
 * Checks if str start with startStr
 **************************************************************/
bool startsWith(const string& str, const string& startStr )
{
    return (str.compare(0, startStr.length(), startStr) == 0);
}

void addToPolyline(float value, ofPolyline& pl, int yOffset)
{
   if (pl.size() >= ofGetWindowWidth())
   {
       pl.clear();
   }
   float yScale = ofGetWindowHeight() / 4; // set scale to 1/4th of window height
   pl.lineTo(pl.size(), yOffset + value * yScale);
}

/***************************************************************
 * Determines the channel and adds the value to the associated buffer
 **************************************************************/
void ofApp::addValueToChannelBuffer(const string& channel, float value)
{
    if (startsWith(channel, "/EEG_0/channel_1"))
    {
        // it's a match!
        // cout << pat << " starts with " << "/EEG_0/channel_1" << endl;
        //cout << value << endl; // show value for this channel

        /*
        if (eeg0chan1_Polyline.size() >= ofGetWindowWidth())
        {
            // line exceeds window width: clear it
            eeg0chan1_Polyline.clear();
        }
        // add x,y point to line where x is incremented every  sample, and y has and offset(50) plus some magic number scaling
        float yscale = ofGetWindowHeight() / 4; // set scale to 1/4th of window height
        eeg0chan1_Polyline.lineTo(eeg0chan1_Polyline.size(), 50 + value * yscale);
        */
        int wh = ofGetWindowHeight();
        int yOffset = wh/10;
        addToPolyline(value, eeg0chan1_Polyline, yOffset); //50);
    }

    if (startsWith(channel, "/EEG_0/channel_2"))
    {
        int wh = ofGetWindowHeight();
        int yOffset = wh/10 + wh/5;
        addToPolyline(value, eeg0chan2_Polyline, yOffset);
    }
    if (startsWith(channel, "/EEG_0/channel_3"))
    {
        int wh = ofGetWindowHeight();
        int yOffset = wh/10 + wh/5 * 2;
        addToPolyline(value, eeg0chan3_Polyline, yOffset);
    }
    if (startsWith(channel, "/EEG_0/channel_4"))
    {
        int wh = ofGetWindowHeight();
        int yOffset = wh/10 + wh/5 * 3;
        addToPolyline(value, eeg0chan4_Polyline, yOffset);
    }
    if (startsWith(channel, "/EEG_1/channel_4"))
    {
        int wh = ofGetWindowHeight();
        int yOffset = wh/10 + wh/5 * 4;
        addToPolyline(value, eeg1chan4_Polyline, yOffset);
    }

/*
  if (pat.startsWith("/EEG_0/channel_1"))
  {
    push_data(7, value);
    push_data(6, value);
  }
  else if (pat.startsWith("/EEG_0/channel_1"))
  {
    push_data(6, value);
  }
  else if (pat.startsWith("/EEG_0/channel_2"))
  {
    push_data(5, value);
    push_data(4, value);
  }
  else if (pat.startsWith("/EEG_0/channel_2"))
  {
    push_data(4, value);
  }
  else if (pat.startsWith("/EEG_0/channel_3"))
  {
    push_data(3, value);
    push_data(2, value);
  }
  else if (pat.startsWith("/EEG_0/channel_3"))
  {
    push_data(2, value);
  }
  else if (pat.startsWith("/EEG_0/channel_4"))
  {
    push_data(1, value);
    push_data(0, value);
  }
  else if (pat.startsWith("/EEG_1/channel_4"))
  {
    push_data(0, value);
  }
  */
}
