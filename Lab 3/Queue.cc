#ifndef QUEUE
#define QUEUE

#include <string.h>
#include <omnetpp.h>

using namespace omnetpp;

class Queue: public cSimpleModule {
private:
    cQueue buffer; // required to store packets
    // handle events such as receiving msgs
    cMessage *endServiceEvent;
    simtime_t serviceTime;
    // vectors to track metrics
    cOutVector bufferSizeVector;
    cOutVector packetDropVector;
    //utils to track vectors
    int packetsDropped;
public:
    Queue();
    virtual ~Queue();
protected:
    virtual void initialize();
    virtual void finish();
    virtual void handleMessage(cMessage *msg);
};

Define_Module(Queue);

Queue::Queue() {
    endServiceEvent = NULL;
}

Queue::~Queue() {
    cancelAndDelete(endServiceEvent);
}

void Queue::initialize() {
    buffer.setName("buffer");
    endServiceEvent = new cMessage("endService");
    packetsDropped = 0;
    //initialize vectors
    bufferSizeVector.setName("Buffer capacity");
    packetDropVector.setName("Quantity of dropped packets");
}

void Queue::finish() {
}

void Queue::handleMessage(cMessage *msg) {

    // if msg is signaling an endServiceEvent
    if (msg == endServiceEvent) {
        // if packet in buffer, send next one
        if (!buffer.isEmpty()) {
            // dequeue packet
            cPacket *pkt = (cPacket*) buffer.pop();
            // send packet
            send(pkt, "out");
            // start new service
            serviceTime = pkt->getDuration();
            scheduleAt(simTime() + serviceTime, endServiceEvent);
        }
    } else { // if msg is a data packet
        // par() is an Omnet function to get the params gave in the network
        const int maxBufferSize = par("bufferSize").intValue();
        if (buffer.getLength() < maxBufferSize) {
            //there is space on buffer, enqueue new message on it
            buffer.insert(msg);
            bufferSizeVector.record(buffer.getLength());
            // if the server is idle
            if (!endServiceEvent->isScheduled()) {
                // start the service
                scheduleAt(simTime() + 0, endServiceEvent);
            }
        } else {
            delete msg; // there is no space on buffer, delete the new message
            packetsDropped++;
            this->bubble("packet dropped");
            // record() will track the number of dropped packets. Omnet keeps a register of this metric, acumulating the values for each simulation run
            new cMessage("Buffer full. Dropping packet: ");
        }
    }
    packetDropVector.record(packetsDropped);
}

#endif /* QUEUE */
