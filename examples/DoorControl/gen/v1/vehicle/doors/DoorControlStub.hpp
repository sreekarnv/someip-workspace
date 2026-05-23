#ifndef V1_VEHICLE_DOORS_DOOR_CONTROL_STUB_HPP_
#define V1_VEHICLE_DOORS_DOOR_CONTROL_STUB_HPP_

#if !defined (COMMONAPI_INTERNAL_COMPILATION)
#define COMMONAPI_INTERNAL_COMPILATION
#define UNDEF_COMMONAPI_INTERNAL_COMPILATION_HERE
#endif

#include <v1/vehicle/doors/DoorControl.hpp>
#include <CommonAPI/Stub.hpp>

#if defined (UNDEF_COMMONAPI_INTERNAL_COMPILATION_HERE)
#undef COMMONAPI_INTERNAL_COMPILATION
#undef UNDEF_COMMONAPI_INTERNAL_COMPILATION_HERE
#endif

#include <functional>
#include <memory>
#include <vector>

namespace v1 {
namespace vehicle {
namespace doors {

class DoorControlStubAdapter : public virtual CommonAPI::StubAdapter {
public:
    virtual ~DoorControlStubAdapter() {}
};

class DoorControlStubRemoteEvent {
public:
    virtual ~DoorControlStubRemoteEvent() {}
};

class DoorControlStub
    : public virtual CommonAPI::Stub<DoorControlStubAdapter, DoorControlStubRemoteEvent> {
public:
    virtual ~DoorControlStub() {}

    typedef DoorControlStubAdapter StubAdapterType;
    typedef DoorControlStubRemoteEvent RemoteEventHandlerType;
    typedef DoorControlStubRemoteEvent RemoteEventType;

    typedef std::function<void(bool)> unlockDoorReply_t;
    typedef std::function<void(DoorControl::DoorStatus)> getDoorStatusReply_t;
    typedef std::function<void(std::vector<DoorControl::DoorStatus>)> getAllDoorStatusReply_t;

    struct StubInterface {
        static const char* getInterface() {
            return "vehicle.doors.DoorControl:v1_0";
        }
    };

    void lockInterfaceVersionAttribute(bool _lockAccess) { static_cast<void>(_lockAccess); }
    virtual const CommonAPI::Version& getInterfaceVersion(const std::shared_ptr<CommonAPI::ClientId>) {
        static CommonAPI::Version version(1, 0);
        return version;
    }

    DoorControlStubRemoteEvent* initStubAdapter(const std::shared_ptr<DoorControlStubAdapter>& _stubAdapter) override {
        stubAdapter_ = _stubAdapter;
        return nullptr;
    }

    virtual void lockAllDoors(const std::shared_ptr<CommonAPI::ClientId> _client) = 0;
    virtual void unlockDoor(const std::shared_ptr<CommonAPI::ClientId> _client,
            uint32_t _door, unlockDoorReply_t _reply) = 0;
    virtual void getDoorStatus(const std::shared_ptr<CommonAPI::ClientId> _client,
            uint32_t _door, getDoorStatusReply_t _reply) = 0;
    virtual void getAllDoorStatus(const std::shared_ptr<CommonAPI::ClientId> _client,
            getAllDoorStatusReply_t _reply) = 0;

    virtual void fireOnDoorStateChangedEvent(const uint32_t& _door,
            const DoorControl::DoorStatus& _status) = 0;

    bool hasElement(const uint32_t _id) const override {
        return (_id < 4);
    }
};

}
}
}

#endif
