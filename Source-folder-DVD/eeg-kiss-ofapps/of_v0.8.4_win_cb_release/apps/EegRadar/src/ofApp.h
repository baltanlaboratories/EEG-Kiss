#pragma once

#include "ofMain.h"
#include "ofxOsc.h"

class ofApp : public ofBaseApp{

	public:
		void setup();
		void update();
		void draw();
		void exit(ofEventArgs &args);

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
        struct ApplicationSettings{
            string windowTitle  = "EEG Radar v0.1";
            int magnification   = 1.0;
            int framerate       = 60;
            int circleResolution = 50;
        };

		struct EEGSettings {
		    int nrOfHeadsets = 2;
		    int nrOfChannels = 4;
		    int nrOfSamples  = 1024;

            string headsetPatternPrefix  = "/EEG_";
            string channelPatternPrefix  = "channel_";
            string markersPattern        = "/markers";
        };

        enum DataTypes{
            IMEC_EEG_DATA
        };

        ApplicationSettings appSettings;
        EEGSettings         eegSettings;

        int         width,height;
		bool	    bSmooth;
		int         iSampleCounter;
		int         iNrOfSamples;
		int         iNrOfHeadsets;
		int         iNrOfChannels;
		float***    fSamples;
		float       fRadius;
		float       fMinRadius;
//		bool        bKissing;       // True between the kissing markers
        bool        bStartKiss;
        int         iStartKissIndex;
        int         iStartKissCount;
        int         iCaptureStartKissCount;
        bool        bStopKiss;
        int         iStopKissIndex;
        int         iStopKissCount;
        int         iCaptureStopKissCount;
		bool        bInfoText;      // display text UI or not
		int         samplesToFade;  // number of samples to fadeout (these are skipped during draw())
		int         iFrameRate;     // max frame rate
		float       fMagnification; // magnification factor of the radar
		float       initialMagnification;

        float getOscArg(const ofxOscMessage& m, int argIndex);
        void  addValueToChannelBuffer(DataTypes dataType, const string& pat, float value);
        void  saveScreenshot(ofImage image, string filename);

		ofxOscReceiver receiver;
        ofImage screenImg;

        int iSampleCounters[2][4];
};
