#ifndef V1_VEHICLE_DOORS_DOOR_CONTROL_PROXY_BASE_HPP_
#define V1_VEHICLE_DOORS_DOOR_CONTROL_PROXY_BASE_HPP_

#if !defined (COMMONAPI_INTERNAL_COMPILATION)
#define COMMONAPI_INTERNAL_COMPILATION
#endif

#include <v1/vehicle/doors/DoorControl.hpp>
#include <CommonAPI/Event.hpp>
#include <CommonAPI/Proxy.hpp>

#if defined (COMMONAPI_INTERNAL_COMPILATION)
#undef COMMONAPI_INTERNAL_COMPILATION
#endif

#include <functional>
#include <future>
#include <vector>

namespace v1 {
namespace vehicle {
namespace doors {

class DoorControlProxyBase : public virtual CommonAPI::Proxy {
public:
    virtual ~DoorControlProxyBase() {}

    typedef CommonAPI::Event<uint32_t, DoorControl::DoorStatus> OnDoorStateChangedEvent;

    typedef std::function<void(CommonAPI::CallStatus, bool)> UnlockDoorAsyncCallback;
    typedef std::function<void(CommonAPI::CallStatus, const DoorControl::DoorStatus&)> GetDoorStatusAsyncCallback;
    typedef std::function<void(CommonAPI::CallStatus, const std::vector<DoorControl::DoorStatus>&)> GetAllDoorStatusAsyncCallback;

    virtual OnDoorStateChangedEvent& getOnDoorStateChangedEvent() = 0;

    virtual void lockAllDoors(CommonAPI::CallStatus& callStatus) = 0;

    virtual void unlockDoor(DoorControl::DoorPosition door, CommonAPI::CallStatus& callStatus,
            bool& success, const CommonAPI::CallInfo* info = nullptr) = 0;

    virtual std::future<CommonAPI::CallStatus> unlockDoorAsync(DoorControl::DoorPosition door,
            UnlockDoorAsyncCallback callback, const CommonAPI::CallInfo* info = nullptr) = 0;

    virtual void getDoorStatus(DoorControl::DoorPosition door, CommonAPI::CallStatus& callStatus,
            DoorControl::DoorStatus& status, const CommonAPI::CallInfo* info = nullptr) = 0;

    virtual std::future<CommonAPI::CallStatus> getDoorStatusAsync(DoorControl::DoorPosition door,
            GetDoorStatusAsyncCallback callback, const CommonAPI::CallInfo* info = nullptr) = 0;

    virtual void getAllDoorStatus(CommonAPI::CallStatus& callStatus,
            std::vector<DoorControl::DoorStatus>& allDoors, const CommonAPI::CallInfo* info = nullptr) = 0;

    virtual std::future<CommonAPI::CallStatus> getAllDoorStatusAsync(
            GetAllDoorStatusAsyncCallback callback, const CommonAPI::CallInfo* info = nullptr) = 0;
};

}
}
}

#endif
