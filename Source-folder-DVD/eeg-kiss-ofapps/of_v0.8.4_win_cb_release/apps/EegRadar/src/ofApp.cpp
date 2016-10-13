#include "ofApp.h"
#include <math.h>
#include <assert.h>

const int kOscReceivePort = 7110;

//--------------------------------------------------------------
void ofApp::setup(){
	bSmooth         = true;
	bInfoText       = true;
	iSampleCounter  = 0;
    iFrameRate      = appSettings.framerate;
    width           = ofGetWidth();
    height          = ofGetHeight();

    ofBackground(0, 0, 0);
	ofSetCircleResolution(appSettings.circleResolution);
	ofSetWindowTitle(appSettings.windowTitle);
    ofSetVerticalSync(false);

	ofSetFrameRate(iFrameRate); // if vertical sync is off, we can go a bit fast... this caps the framerate

    ofEnableAntiAliasing();

    windowResized(width, height);

    // Adjust fMagnification to scale the entire radar image
    fMagnification = appSettings.magnification;

    // Initialize an multi-dimensional array to hold the EEG samples
    fSamples = new float**[eegSettings.nrOfHeadsets];

    for(int i = 0; i < eegSettings.nrOfHeadsets; i++){
        fSamples[i] = new float*[eegSettings.nrOfChannels];
        for( int j = 0; j < eegSettings.nrOfChannels; j++){
            fSamples[i][j] = new float[eegSettings.nrOfSamples] () ;
        }
    }

    // Listen on the given port
	cout << "Listening for osc messages on port " << kOscReceivePort << endl;
	receiver.setup(kOscReceivePort);
}

//--------------------------------------------------------------
void ofApp::exit(ofEventArgs &args){
    int i,j;
    for(i = 0; i < eegSettings.nrOfHeadsets; i++){
        for(j = 0; j < eegSettings.nrOfChannels; j++){
            delete[] fSamples[i][j];
            fSamples[i][j] = NULL;
        }
        delete[] fSamples[i];
        fSamples[i] = NULL;
    }
    delete[] fSamples;
}

//--------------------------------------------------------------
void ofApp::update()
{
//    iSampleCounter = (iSampleCounter + 1) % eegSettings.nrOfSamples;

    // Check for plotting full circle (sample-buffer size) from the moment the marker was plotted
//    if (bStartKiss)
//    {
//        if (++iStartKissCount >= eegSettings.nrOfSamples)
//        {
//            bStartKiss = false;
//        }
//    }
//    if (bStopKiss)
//    {
//        if (++iStopKissCount >= eegSettings.nrOfSamples)
//        {
//            bStopKiss = false;
//        }
//    }

    // check for waiting messages
	while(receiver.hasWaitingMessages()){
		// get the next message
		ofxOscMessage m;
		receiver.getNextMessage(&m);

        // get the current pattern
        string pattern = m.getAddress();

        // get the value of the pattern
        float value = getOscArg(m, 0);

        // Parse IMEC EEG data
        addValueToChannelBuffer(IMEC_EEG_DATA, pattern, value);
	}

//    if (bKissing)
//        ofBackground(ofColor::red);
//    else
//        ofBackground(ofColor::black);
}

//--------------------------------------------------------------
void ofApp::draw()
{
    for (int hs = 0; hs < eegSettings.nrOfHeadsets; hs++)
    {
        for (int channel = 0; channel < eegSettings.nrOfChannels; channel++)
        {
            float fInnerRadius = fMinRadius + channel * fRadius * 1.25;

            for (int i = samplesToFade; i < eegSettings.nrOfSamples; i++)
            {
                int alpha = (i-samplesToFade ) * 255 / (eegSettings.nrOfSamples - samplesToFade);

                if (hs)
//                    (bKissing) ? ofSetColor(ofColor::pink, alpha) : ofSetColor(ofColor::white, alpha);
                    ofSetColor(ofColor::white, alpha);
                else
//                    (bKissing) ? ofSetColor(ofColor::blue, alpha) : ofSetColor(ofColor::green,alpha);
                    ofSetColor(ofColor::green,alpha);

                int sampleIndex = (i + iSampleCounters[hs][channel] + eegSettings.nrOfSamples) % eegSettings.nrOfSamples;
                float s1 = fSamples[hs][channel][sampleIndex];
                float s2 = fSamples[hs][channel][(sampleIndex+1) % eegSettings.nrOfSamples];

                float amplitude1 = fInnerRadius + fRadius * s1;
                float amplitude2 = fInnerRadius + fRadius * s2;
                float x1,y1,x2,y2;

                float r1 = (((float)( sampleIndex)  / eegSettings.nrOfSamples)) * 2. * PI;
                float r2 = (((float)((sampleIndex+1)% eegSettings.nrOfSamples)) / eegSettings.nrOfSamples) * 2. * PI;

                x1 = width  / 2 + amplitude1 * sin(r1) * fMagnification;
                y1 = height / 2 + amplitude1 * cos(r1) * fMagnification;
                x2 = width  / 2 + amplitude2 * sin(r2) * fMagnification;
                y2 = height / 2 + amplitude2 * cos(r2) * fMagnification;

                ofLine(x1,y1,x2,y2);

                if (!hs && (channel == 3))
                {
                    if (bStartKiss && (sampleIndex == iStartKissIndex))
                    {
                        x1 = width/2;
                        y1 = height/2;
                        x2 = x1 + amplitude1 * sin(r1) * fMagnification * 1.5;
                        y2 = y1 + amplitude1 * cos(r1) * fMagnification * 1.5;

                        ofSetColor(ofColor::yellow, alpha);
                        ofSetLineWidth(2.0);
                        ofLine(x1, y1, x2, y2);
                        ofSetLineWidth(1.0);
                    }
                    if (bStopKiss && (sampleIndex == iStopKissIndex))
                    {
                        x1 = width/2;
                        y1 = height/2;
                        x2 = x1 + amplitude1 * sin(r1) * fMagnification * 1.5;
                        y2 = y1 + amplitude1 * cos(r1) * fMagnification * 1.5;

                        ofSetColor(ofColor::cyan, alpha);
                        ofSetLineWidth(2.0);
                        ofLine(x1, y1, x2, y2);
                        ofSetLineWidth(1.0);
                    }
                }
            }
        }
    }

    if (bStartKiss && (iCaptureStartKissCount > 0))
    {
        if (++iCaptureStartKissCount > 16)
        {
            screenImg.grabScreen(0, 0, width, height);
            saveScreenshot(screenImg, "startkiss.png");
            iCaptureStartKissCount = 0;
        }
    }
    if (bStopKiss && (iCaptureStopKissCount > 0))
    {
        if (++iCaptureStopKissCount > 16)
        {
            screenImg.grabScreen(0, 0, width, height);
            saveScreenshot(screenImg, "stopkiss.png");
            iCaptureStopKissCount = 0;
        }
    }

    // Draw UI
    if(bInfoText) {
        stringstream ss;
        ss << "Framerate: " << ofToString(ofGetFrameRate(),0)
           << " Fade: " << samplesToFade
           << " Magnification: " << ofToString(fMagnification, 2) << endl;
        ss << "(i) toggle this menu" << endl;
        ss << "(f) toggle full screen" << endl;
        ss << "(q) increase fade" << endl;
        ss << "(a) decrease fade" << endl;
        ss << "(w) increase max framerate" << endl;
        ss << "(s) decrease max framerate" << endl;
        ss << "(e) increase magnification" << endl;
        ss << "(d) decrease magnification" << endl;
        ss << "(r) reset magnification" << endl;
        ss << "(c) capture screenshot" << endl;

        ofSetColor(ofColor::white);
        ofDrawBitmapString(ss.str().c_str(), 20, 20);
    }
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
void ofApp::addValueToChannelBuffer(DataTypes dataType, const string& destination, float value)
{
    switch ( dataType )
    {
        case IMEC_EEG_DATA:
            //assert(eegSettings.nrOfHeadsets == 2);
            //assert(eegSettings.nrOfChannels == 4);

            int headsetId = -1;
            if (startsWith(destination, "/EEG_0/"))
            {
                headsetId = 0;
            } else if (startsWith(destination, "/EEG_1/"))
            {
                headsetId = 1;
            } else if (startsWith(destination, eegSettings.markersPattern))
            {
//                bKissing = bool(value); was used for changing background-color

                // Stop-kiss value = 0/4096 = 0.0
                // Start-kiss value = 1/4096 = 0.000244
                // Point-of-interest value = 2/4096 = 0.000488
                if ((value > 0.0) && (value < 0.0003))
                {
                    if (!bStartKiss)
                    {
                        bStartKiss = true;
                        iStartKissIndex = iSampleCounters[0][3];
                        iStartKissCount = 0;
                        iCaptureStartKissCount++;
                    }
                }
                else if (value == 0.0)
                {
                    if (!bStopKiss)
                    {
                        bStopKiss = true;
                        iStopKissIndex = iSampleCounters[0][3];
                        iStopKissCount = 0;
                        iCaptureStopKissCount++;
                    }
                }
            }
            // check if a valid headset was found
            if (headsetId != -1)
            {
                // now determine the channel
                string channel  = destination.substr(strlen("/EEG_0/"));
                int chanId      = -1;

                if (startsWith(channel, eegSettings.channelPatternPrefix))
                {
                    // read channel id using string stream
                    istringstream ( channel.substr(eegSettings.channelPatternPrefix.length(), 1) ) >> chanId;
                    chanId--; // decrement to get index
                }

                if (chanId >= 0 && chanId <= eegSettings.nrOfChannels)
                {
                    //fSamples[headsetId][chanId][iSampleCounter] = value;
                    iSampleCounters[headsetId][chanId] = (iSampleCounters[headsetId][chanId] + 1) % eegSettings.nrOfSamples;
                    fSamples[headsetId][chanId][iSampleCounters[headsetId][chanId]] = value;
                    if (!headsetId && (chanId == 3))
                    {
                        if (bStartKiss)
                        {
                            if (++iStartKissCount >= eegSettings.nrOfSamples)
                            {
                                bStartKiss = false;
                            }
                        }
                        if (bStopKiss)
                        {
                            if (++iStopKissCount >= eegSettings.nrOfSamples)
                            {
                                bStopKiss = false;
                            }
                        }
                    }
                    // TODO: return true -> then break from while-loop
//                    if (!(iSampleCounters[0][0] % eegSettings.nrOfChannels))
//                    {
//                        break;
//                    }
                }
                else
                {
                    cout << "got bad channel for :" << destination << " | " << channel.substr(eegSettings.channelPatternPrefix.length(), 1) <<  endl;
                }
            }
    }
}

void ofApp::saveScreenshot(ofImage image, string filename)
{
    ofFile file;
    ofDirectory dir;
    string timestamp;
    string path = "";

    if (file.doesFileExist("..\\Source\\subfolder.txt", false))
    {
        file.open("..\\..\\Source\\subfolder.txt");
        ofBuffer buff = file.readToBuffer();
        file.close();
        cout << buff << endl;
        path = "..\\..\\Source\\records\\";
        if (!dir.doesDirectoryExist(path, true))
        {
            dir.createDirectory(path, true);
            cout << path << endl;
        }
        path += buff;
        if (!dir.doesDirectoryExist(path, true))
        {
            dir.createDirectory(path, true);
            cout << path << endl;
        }
        path += "\\";
    }
    path += ofGetTimestampString("%y%m%d_%H%M%S_");
    path += filename;
    cout << path << endl;

    image.saveImage(path);
}

//--------------------------------------------------------------
void ofApp::keyPressed  (int key)
{
    switch (key)
    {
        case 'f':
            ofToggleFullscreen();
            break;
        case 'i':
            // toggle info on screen
            bInfoText = !bInfoText;
            break;
        case 'q':
            // increase fade
            if (samplesToFade <= eegSettings.nrOfSamples -10) samplesToFade+=10;
            break;
        case 'a':
            // decrease fade
            if (samplesToFade >= 10) samplesToFade -= 10;
            break;
        case 'w':
            // increase framerate
            iFrameRate++;
            ofSetFrameRate(iFrameRate);
            break;
        case 's':
            // decrease framerate
            iFrameRate--;
            ofSetFrameRate(iFrameRate);
            break;
        case 'e':
            // increase Magnification
            fMagnification += 0.01;
            break;
        case 'd':
            // decrease Magnification
            if (fMagnification>0.01) fMagnification -= 0.01;
            break;
        case 'r':
            // reset Magnification
            fMagnification = appSettings.magnification;
            break;
        case 'c':
            // capture screenshot
            screenImg.grabScreen(0, 0, width, height);
            saveScreenshot(screenImg, "screenshot.png");
            break;
    }
}

//--------------------------------------------------------------
void ofApp::keyReleased  (int key){

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
    width = w;
    height = h;

    float minVal = min(width, height);

    fMinRadius      = minVal * .15;
    fRadius         = ((minVal * .25) / (float)(eegSettings.nrOfChannels-1)) / 1.25;
}

//--------------------------------------------------------------
void ofApp::gotMessage(ofMessage msg){

}

//--------------------------------------------------------------
void ofApp::dragEvent(ofDragInfo dragInfo){

}
