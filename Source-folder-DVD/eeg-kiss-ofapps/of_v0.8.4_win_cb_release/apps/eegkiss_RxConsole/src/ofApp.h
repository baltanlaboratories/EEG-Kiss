#pragma once

#include "ofMain.h"
#include "ofxOsc.h"

class ofApp : public ofBaseApp{

	public:
		void setup();
		void update();
		void draw();

		void keyPressed(int key);
		void keyReleased(int key);
		void mouseMoved(int x, int y );
		void mouseDragged(int x, int y, int button);
		void mousePressed(int x, int y, int button);
		void mouseReleased(int x, int y, int button);
		void windowResized(int w, int h);
		void dragEvent(ofDragInfo dragInfo);
		void gotMessage(ofMessage msg);
    private:

        float getOscArg(const ofxOscMessage& m, int argIndex);
        void  addValueToChannelBuffer(const string& pat, float value);
        //ofTrueTypeFont font;
		ofxOscReceiver receiver;

		int msgCounter;

        ofPolyline eeg0chan1_Polyline;
        ofPolyline eeg0chan2_Polyline;
        ofPolyline eeg0chan3_Polyline;
        ofPolyline eeg0chan4_Polyline;
        ofPolyline eeg1chan4_Polyline;

};
