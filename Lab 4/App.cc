#ifndef APP
#define APP

#include <string.h>
#include <omnetpp.h>
#include <packet_m.h>

using namespace omnetpp;

class App: public cSimpleModule {
private:
    cMessage *sendMsgEvent;
    cStdDev delayStats;
    cOutVector delayVector;
    cOutVector receivedPacketsVector;
    cOutVector sentPacketsVector;
    int receivedPackets;
    int sentPackets;
    std::map<int, cOutVector*> hopCountVectors;
public:
    App();
    virtual ~App();
protected:
    virtual void initialize();
    virtual void finish();
    virtual void handleMessage(cMessage *msg);
};

Define_Module(App);

#endif /* APP */

#define NORMAL_PACKET 0

App::App() {
}

App::~App() {
}

void App::initialize() {

    // If interArrivalTime for this node is higher than 0
    // initialize packet generator by scheduling sendMsgEvent
    if (par("interArrivalTime").doubleValue() != 0) {
        sendMsgEvent = new cMessage("sendEvent");
        scheduleAt(par("interArrivalTime"), sendMsgEvent);
    }

    // Initialize statistics
    delayStats.setName("TotalDelay");
    delayVector.setName("Delay");
    receivedPacketsVector.setName("ReceivedPackets");
    sentPacketsVector.setName("SentPackets");
    sentPackets = 0;
    receivedPackets = 0;
}

void App::finish() {
    // Record statistics
    recordScalar("Average delay", delayStats.getMean());
    recordScalar("Number of packets", delayStats.getCount());
    recordScalar("Received packets per second", receivedPackets / simTime().dbl());
}

void App::handleMessage(cMessage *msg) {

    // if msg is a sendMsgEvent, create and send new packet
    if (msg == sendMsgEvent) {
        // create new packet
        Packet *pkt = new Packet("packet", this->getParentModule()->getIndex());
        pkt->setByteLength(par("packetByteSize"));
        pkt->setSource(this->getParentModule()->getIndex());
        pkt->setDestination(par("destination"));
        pkt->setKind(NORMAL_PACKET);
        pkt->setHopCount(0);

        // send to net layer
        send(pkt, "toNet$o");
        sentPackets++;
        sentPacketsVector.record(sentPackets); 

        // compute the new departure time and schedule next sendMsgEvent
        simtime_t departureTime = simTime() + par("interArrivalTime");
        scheduleAt(departureTime, sendMsgEvent);

    }
    // else, msg is a packet from net layer
    else {
        // compute delay and record statistics
        Packet *pkt = (Packet *) msg;
        simtime_t delay = simTime() - msg->getCreationTime();
        delayStats.collect(delay);
        delayVector.record(delay);
        receivedPackets++;
        receivedPacketsVector.record(receivedPackets);
        int sourceNode = pkt->getSource();
        // check if a vector has already been created for this node
        if (hopCountVectors.find(sourceNode) == hopCountVectors.end()) {
            // if not created yet, create a new vector and add it to the map
            std::string hopCountVectorName = "HopCount_" + std::to_string(sourceNode);
            hopCountVectors[sourceNode] = new cOutVector(hopCountVectorName.c_str());
        }
        // record the number of hops in the vector corresponding to the source node
        hopCountVectors[sourceNode]->record(pkt->getHopCount());
        // delete pkt
        delete pkt;
    }
}
