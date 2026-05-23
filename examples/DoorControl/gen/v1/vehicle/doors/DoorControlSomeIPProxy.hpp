#ifndef V1_VEHICLE_DOORS_DOOR_CONTROL_SOMEIP_PROXY_HPP_
#define V1_VEHICLE_DOORS_DOOR_CONTROL_SOMEIP_PROXY_HPP_

#include <v1/vehicle/doors/DoorControlProxyBase.hpp>

#if !defined (COMMONAPI_INTERNAL_COMPILATION)
#define COMMONAPI_INTERNAL_COMPILATION
#define HAS_DEFINED_COMMONAPI_INTERNAL_COMPILATION_HERE
#endif

#include <CommonAPI/SomeIP/Factory.hpp>
#include <CommonAPI/SomeIP/Proxy.hpp>
#include <CommonAPI/SomeIP/Types.hpp>
#include <CommonAPI/SomeIP/Event.hpp>
#include <CommonAPI/SomeIP/Deployment.hpp>

#if defined (HAS_DEFINED_COMMONAPI_INTERNAL_COMPILATION_HERE)
#undef COMMONAPI_INTERNAL_COMPILATION
#undef HAS_DEFINED_COMMONAPI_INTERNAL_COMPILATION_HERE
#endif

#include <string>

namespace v1 {
namespace vehicle {
namespace doors {

template<typename ... _AttributeExtensions>
class DoorControlSomeIPProxy
    : virtual public DoorControlProxyBase,
      virtual public CommonAPI::SomeIP::Proxy {
public:
    static const char* getInterface() {
        return "vehicle.doors.DoorControl:v1_0";
    }

    DoorControlSomeIPProxy(
        const CommonAPI::SomeIP::Address &_address,
        const std::shared_ptr<CommonAPI::SomeIP::ProxyConnection> &_connection);

    DoorControlSomeIPProxy(
        const std::shared_ptr<CommonAPI::Proxy> &_proxy);

    virtual ~DoorControlSomeIPProxy();

    virtual OnDoorStateChangedEvent& getOnDoorStateChangedEvent();

    virtual void lockAllDoors(CommonAPI::CallStatus &_internalCallStatus);

    virtual void unlockDoor(DoorControl::DoorPosition _door, CommonAPI::CallStatus &_internalCallStatus, bool &_success, const CommonAPI::CallInfo *_info);

    virtual std::future<CommonAPI::CallStatus> unlockDoorAsync(DoorControl::DoorPosition _door, UnlockDoorAsyncCallback _callback, const CommonAPI::CallInfo *_info) override;

    virtual void getDoorStatus(DoorControl::DoorPosition _door, CommonAPI::CallStatus &_internalCallStatus, DoorControl::DoorStatus &_status, const CommonAPI::CallInfo *_info);

    virtual std::future<CommonAPI::CallStatus> getDoorStatusAsync(DoorControl::DoorPosition _door, GetDoorStatusAsyncCallback _callback, const CommonAPI::CallInfo *_info) override;

    virtual void getAllDoorStatus(CommonAPI::CallStatus &_internalCallStatus, std::vector< DoorControl::DoorStatus > &_allDoors, const CommonAPI::CallInfo *_info);

    virtual std::future<CommonAPI::CallStatus> getAllDoorStatusAsync(GetAllDoorStatusAsyncCallback _callback, const CommonAPI::CallInfo *_info);

    virtual void getOwnVersion(uint16_t &_major, uint16_t &_minor) const;

    virtual std::future<void> getCompletionFuture();

private:
    CommonAPI::SomeIP::Event<OnDoorStateChangedEvent,
        uint32_t,
        CommonAPI::Deployable< DoorControl::DoorStatus, CommonAPI::EmptyDeployment >> onDoorStateChanged_;

};

}
}
}

#endif
