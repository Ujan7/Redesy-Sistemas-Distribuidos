#ifndef NET
#define NET

#include <string.h>
#include <omnetpp.h>
#include <packet_m.h>

#include <vector>
using namespace omnetpp;

class Net: public cSimpleModule {
private:
    std::vector<int> nodesVector;
    bool netIsRecognized;

public:
    Net();
    virtual ~Net();
protected:
    virtual void initialize();
    virtual void finish();
    virtual void handleMessage(cMessage *msg);
    virtual void handleRecognitionMessage(cMessage *msg);
    virtual int chooseOutGate(Packet *pkt);
    virtual void handleNormalMessage(cMessage *msg);
    virtual void handleIncomingFromLnk(Packet *pkt);
    virtual void handleIncomingFromApp(Packet *pkt);
    virtual void sendRecognitionPacket();
};

Define_Module(Net);

#endif /* NET */

#define NORMAL_PACKET 0
#define RECOGNITION_PACKET 1

#define CLOCK_WISE 0
#define COUNTER_CLOCK_WISE 1

Net::Net() {
}

Net::~Net() {
}

void Net::initialize() {
    sendRecognitionPacket();
}

void Net::finish() {
}

void Net::sendRecognitionPacket() {
    int currentNode = getParentModule()->getIndex();
    Packet *recogPkt = new Packet("RecognitionPacket");
    recogPkt->setSource(currentNode);
    recogPkt->setDestination(currentNode);
    recogPkt->setKind(RECOGNITION_PACKET);
    send(recogPkt, "toLnk$o", CLOCK_WISE);
}

void Net::handleMessage(cMessage *msg) {

    // All msg (events) on net are packets
    Packet *pkt = (Packet *) msg;
    switch (pkt->getKind())
    {
        case (RECOGNITION_PACKET):
            handleRecognitionMessage(msg);
            break;
        case (NORMAL_PACKET):
            handleNormalMessage(msg);
            break;
        default:
            break;
    }
}

void Net::handleRecognitionMessage(cMessage *msg) {
    Packet *pkt = (Packet *) msg;
    if (pkt->getDestination() != this->getParentModule()->getIndex()) { // Packet isn't for this node --> add to vector
        nodesVector.insert(nodesVector.begin(), pkt->getDestination()); 
        send(msg, "toLnk$o", CLOCK_WISE);
    } else {
        // Packet has arrived again on the source --> Net already recognized
        delete msg;
        netIsRecognized = true;
        std::cout << "Node " << this->getParentModule()->getIndex() << " net Recognized" << endl;
    }
}

void Net::handleNormalMessage(cMessage *msg) {
    Packet *pkt = static_cast<Packet *>(msg);
    int destination = pkt->getDestination();
    int parentIndex = this->getParentModule()->getIndex();

    if (destination == parentIndex) { 
        // Packet is for this node
        send(msg, "toApp$o");
    } else {
        // Packet is not for this node
        pkt->setHopCount(pkt->getHopCount() + 1);

        if (pkt->arrivedOn("toApp$i")) {
            handleIncomingFromApp(pkt);
        } else {
            handleIncomingFromLnk(pkt);
        }
    }
}

void Net::handleIncomingFromApp(Packet *pkt) {
    if (netIsRecognized) {
        std::cout << "Pkt arrived from App: " << pkt->arrivedOn("toApp$i") << std::endl;
        int outGate = chooseOutGate(pkt);
        send(pkt, "toLnk$o", outGate);
    } else {
        // net isn't recognized, send in clockwise direction by default
        send(pkt, "toLnk$o", CLOCK_WISE);
    }
}

int Net::chooseOutGate(Packet *pkt){
    // Look for the destination node in nodesVector to choose the direction to send the packet
    int gate = CLOCK_WISE;

    for (int index = 0; index < nodesVector.size(); index++) {
        if (pkt->getDestination() == nodesVector[index]) {
            std::cout << "Direction Recognized" << endl;

            // nodes at the first half of vector are closer clockwise
            gate = (index < static_cast<int>(nodesVector.size()) / 2) ? CLOCK_WISE : COUNTER_CLOCK_WISE;
            break;
        }
    }
    return gate;
}

void Net::handleIncomingFromLnk(Packet *pkt) {
    int outGate = (pkt->arrivedOn("toLnk$i", 0)) ? 1 : 0;
    send(pkt, "toLnk$o", outGate);
}
