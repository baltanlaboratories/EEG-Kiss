#include "ofApp.h"

//--------------------------------------------------------------
void ofApp::setup(){
    posB.X = 100;
    posB.Y = 100;

    ofSetFrameRate(60);
}

//--------------------------------------------------------------
void ofApp::update(){
    r++;
    if (r>=256)
    {
        r=0;
    }
    //posB.X >= 500 ? 0 : posB.X++;
    posB.X++;
    if (posB.X >= 500)
    {
        posB.X = 100;
    }
}

//--------------------------------------------------------------
void ofApp::draw(){
    ofSetColor(r, 0, 60);
    ofCircle(200, 300, 60);


    ofSetColor(0, 255, 255);
    ofCircle(posB.X, posB.Y, 100);


    ofSetColor(0, 0, 0);
    ofDrawBitmapString(ofToString((int)ofGetFrameRate())+"fps", 10, 15);
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
