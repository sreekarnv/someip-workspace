#ifndef DOOR_CONTROL_STUB_IMPL_HPP
#define DOOR_CONTROL_STUB_IMPL_HPP

#include <v1/vehicle/doors/DoorControlStub.hpp>
#include <map>

using namespace v1::vehicle::doors;

class DoorControlStubImpl : public DoorControlStub {
public:
    DoorControlStubImpl();
    virtual ~DoorControlStubImpl();

    virtual void lockAllDoors(const std::shared_ptr<CommonAPI::ClientId> _client);

    virtual void unlockDoor(const std::shared_ptr<CommonAPI::ClientId> _client,
            uint32_t _door, unlockDoorReply_t _reply);

    virtual void getDoorStatus(const std::shared_ptr<CommonAPI::ClientId> _client,
            uint32_t _door, getDoorStatusReply_t _reply);

    virtual void getAllDoorStatus(const std::shared_ptr<CommonAPI::ClientId> _client,
            getAllDoorStatusReply_t _reply);

    virtual void fireOnDoorStateChangedEvent(const uint32_t& _door,
            const DoorControl::DoorStatus& _status);

private:
    struct DoorInfo {
        DoorControl::DoorState state;
        bool childLock;
        uint8_t windowPercent;
    };

    std::map<int, DoorInfo> doors_;

    void updateDoorState(DoorControl::DoorPosition door, DoorControl::DoorState newState);
};

#endif
