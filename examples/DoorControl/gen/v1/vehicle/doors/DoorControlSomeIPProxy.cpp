#include <v1/vehicle/doors/DoorControlSomeIPProxy.hpp>

#if !defined (COMMONAPI_INTERNAL_COMPILATION)
#define COMMONAPI_INTERNAL_COMPILATION
#define HAS_DEFINED_COMMONAPI_INTERNAL_COMPILATION_HERE
#endif

#include <CommonAPI/SomeIP/AddressTranslator.hpp>

#if defined (HAS_DEFINED_COMMONAPI_INTERNAL_COMPILATION_HERE)
#undef COMMONAPI_INTERNAL_COMPILATION
#undef HAS_DEFINED_COMMONAPI_INTERNAL_COMPILATION_HERE
#endif

namespace v1 {
namespace vehicle {
namespace doors {

template<typename ... _AttributeExtensions>
std::shared_ptr<CommonAPI::SomeIP::Proxy> createDoorControlSomeIPProxy(
    const CommonAPI::SomeIP::Address &_address,
    const std::shared_ptr<CommonAPI::SomeIP::ProxyConnection> &_connection) {
    return std::make_shared< DoorControlSomeIPProxy<_AttributeExtensions...>>(_address, _connection);
}

template<typename ... _AttributeExtensions>
void initializeDoorControlSomeIPProxy() {
    CommonAPI::SomeIP::AddressTranslator::get()->insert(
        "local:vehicle.doors.DoorControl:v1_0:vehicle.doors.DoorControl",
        0x1001, 0x1, 1, 0);
    CommonAPI::SomeIP::Factory::get()->registerProxyCreateMethod(
        "vehicle.doors.DoorControl:v1_0",
        &createDoorControlSomeIPProxy<_AttributeExtensions...>);
}

INITIALIZER(registerDoorControlSomeIPProxy) {
    CommonAPI::SomeIP::Factory::get()->registerInterface(initializeDoorControlSomeIPProxy<>);
}

template<typename ... _AttributeExtensions>
DoorControlSomeIPProxy<_AttributeExtensions...>::DoorControlSomeIPProxy(
    const CommonAPI::SomeIP::Address &_address,
    const std::shared_ptr<CommonAPI::SomeIP::ProxyConnection> &_connection)
        : CommonAPI::SomeIP::Proxy(_address, _connection),
          onDoorStateChanged_(*this, 0x1, CommonAPI::SomeIP::event_id_t(0x8001), CommonAPI::SomeIP::event_type_e::ET_EVENT , CommonAPI::SomeIP::reliability_type_e::RT_UNRELIABLE, false, std::make_tuple(
              static_cast<uint32_t>(0),
              CommonAPI::Deployable< DoorControl::DoorStatus, CommonAPI::EmptyDeployment>(static_cast< CommonAPI::EmptyDeployment* >(nullptr))))
{
}

template<typename ... _AttributeExtensions>
DoorControlSomeIPProxy<_AttributeExtensions...>::DoorControlSomeIPProxy(
    const std::shared_ptr<CommonAPI::Proxy> &_proxy)
        : CommonAPI::SomeIP::Proxy(_proxy),
          onDoorStateChanged_(*this, 0x1, CommonAPI::SomeIP::event_id_t(0x8001), CommonAPI::SomeIP::event_type_e::ET_EVENT , CommonAPI::SomeIP::reliability_type_e::RT_UNRELIABLE, false, std::make_tuple(
              static_cast<uint32_t>(0),
              CommonAPI::Deployable< DoorControl::DoorStatus, CommonAPI::EmptyDeployment>(static_cast< CommonAPI::EmptyDeployment* >(nullptr))))
{
}

template<typename ... _AttributeExtensions>
DoorControlSomeIPProxy<_AttributeExtensions...>::~DoorControlSomeIPProxy() {
}

template<typename ... _AttributeExtensions>
DoorControlProxyBase::OnDoorStateChangedEvent& DoorControlSomeIPProxy<_AttributeExtensions...>::getOnDoorStateChangedEvent() {
    return onDoorStateChanged_;
}

template<typename ... _AttributeExtensions>
void DoorControlSomeIPProxy<_AttributeExtensions...>::lockAllDoors(CommonAPI::CallStatus &_internalCallStatus) {
    CommonAPI::SomeIP::ProxyHelper<
        CommonAPI::SomeIP::SerializableArguments<
        >,
        CommonAPI::SomeIP::SerializableArguments<
        >
    >::callMethod(
        *this,
        CommonAPI::SomeIP::method_id_t(0x100),
        false,
        false,
        _internalCallStatus);
}

template<typename ... _AttributeExtensions>
void DoorControlSomeIPProxy<_AttributeExtensions...>::unlockDoor(DoorControl::DoorPosition _door, CommonAPI::CallStatus &_internalCallStatus, bool &_success, const CommonAPI::CallInfo *_info) {
    uint32_t deploy_door = static_cast<uint32_t>(_door);
    CommonAPI::Deployable< bool, CommonAPI::EmptyDeployment> deploy_success(static_cast< CommonAPI::EmptyDeployment* >(nullptr));
    CommonAPI::SomeIP::ProxyHelper<
        CommonAPI::SomeIP::SerializableArguments<
            uint32_t
        >,
        CommonAPI::SomeIP::SerializableArguments<
            CommonAPI::Deployable<
                bool,
                CommonAPI::EmptyDeployment
            >
        >
    >::callMethodWithReply(
        *this,
        CommonAPI::SomeIP::method_id_t(0x101),
        true,
        false,
        (_info ? _info : &CommonAPI::SomeIP::defaultCallInfo),
        deploy_door,
        _internalCallStatus,
        deploy_success);
    _success = deploy_success.getValue();
}

template<typename ... _AttributeExtensions>
std::future<CommonAPI::CallStatus> DoorControlSomeIPProxy<_AttributeExtensions...>::unlockDoorAsync(DoorControl::DoorPosition _door, UnlockDoorAsyncCallback _callback, const CommonAPI::CallInfo *_info) {
    uint32_t deploy_door = static_cast<uint32_t>(_door);
    CommonAPI::Deployable< bool, CommonAPI::EmptyDeployment> deploy_success(static_cast< CommonAPI::EmptyDeployment* >(nullptr));
    return CommonAPI::SomeIP::ProxyHelper<
        CommonAPI::SomeIP::SerializableArguments<
            uint32_t
        >,
        CommonAPI::SomeIP::SerializableArguments<
            CommonAPI::Deployable<
                bool,
                CommonAPI::EmptyDeployment
            >
        >
    >::callMethodAsync(
        *this,
        CommonAPI::SomeIP::method_id_t(0x101),
        true,
        false,
        (_info ? _info : &CommonAPI::SomeIP::defaultCallInfo),
        deploy_door,
        [_callback] (CommonAPI::CallStatus _internalCallStatus, CommonAPI::Deployable< bool, CommonAPI::EmptyDeployment > _success) {
            if (_callback)
                _callback(_internalCallStatus, _success.getValue());
        },
        std::make_tuple(deploy_success));
}

template<typename ... _AttributeExtensions>
void DoorControlSomeIPProxy<_AttributeExtensions...>::getDoorStatus(DoorControl::DoorPosition _door, CommonAPI::CallStatus &_internalCallStatus, DoorControl::DoorStatus &_status, const CommonAPI::CallInfo *_info) {
    uint32_t deploy_door = static_cast<uint32_t>(_door);
    CommonAPI::Deployable< DoorControl::DoorStatus, CommonAPI::EmptyDeployment> deploy_status(static_cast< CommonAPI::EmptyDeployment* >(nullptr));
    CommonAPI::SomeIP::ProxyHelper<
        CommonAPI::SomeIP::SerializableArguments<
            uint32_t
        >,
        CommonAPI::SomeIP::SerializableArguments<
            CommonAPI::Deployable<
                DoorControl::DoorStatus,
                CommonAPI::EmptyDeployment
            >
        >
    >::callMethodWithReply(
        *this,
        CommonAPI::SomeIP::method_id_t(0x102),
        true,
        false,
        (_info ? _info : &CommonAPI::SomeIP::defaultCallInfo),
        deploy_door,
        _internalCallStatus,
        deploy_status);
    _status = deploy_status.getValue();
}

template<typename ... _AttributeExtensions>
std::future<CommonAPI::CallStatus> DoorControlSomeIPProxy<_AttributeExtensions...>::getDoorStatusAsync(DoorControl::DoorPosition _door, GetDoorStatusAsyncCallback _callback, const CommonAPI::CallInfo *_info) {
    uint32_t deploy_door = static_cast<uint32_t>(_door);
    CommonAPI::Deployable< DoorControl::DoorStatus, CommonAPI::EmptyDeployment> deploy_status(static_cast< CommonAPI::EmptyDeployment* >(nullptr));
    return CommonAPI::SomeIP::ProxyHelper<
        CommonAPI::SomeIP::SerializableArguments<
            uint32_t
        >,
        CommonAPI::SomeIP::SerializableArguments<
            CommonAPI::Deployable<
                DoorControl::DoorStatus,
                CommonAPI::EmptyDeployment
            >
        >
    >::callMethodAsync(
        *this,
        CommonAPI::SomeIP::method_id_t(0x102),
        true,
        false,
        (_info ? _info : &CommonAPI::SomeIP::defaultCallInfo),
        deploy_door,
        [_callback] (CommonAPI::CallStatus _internalCallStatus, CommonAPI::Deployable< DoorControl::DoorStatus, CommonAPI::EmptyDeployment > _status) {
            if (_callback)
                _callback(_internalCallStatus, _status.getValue());
        },
        std::make_tuple(deploy_status));
}

template<typename ... _AttributeExtensions>
void DoorControlSomeIPProxy<_AttributeExtensions...>::getAllDoorStatus(CommonAPI::CallStatus &_internalCallStatus, std::vector< DoorControl::DoorStatus > &_allDoors, const CommonAPI::CallInfo *_info) {
    CommonAPI::Deployable< std::vector< DoorControl::DoorStatus >, CommonAPI::SomeIP::ArrayDeployment< CommonAPI::EmptyDeployment >> deploy_allDoors(static_cast< CommonAPI::SomeIP::ArrayDeployment< CommonAPI::EmptyDeployment >* >(nullptr));
    CommonAPI::SomeIP::ProxyHelper<
        CommonAPI::SomeIP::SerializableArguments<
        >,
        CommonAPI::SomeIP::SerializableArguments<
            CommonAPI::Deployable<
                std::vector< DoorControl::DoorStatus >,
                CommonAPI::SomeIP::ArrayDeployment< CommonAPI::EmptyDeployment >
            >
        >
    >::callMethodWithReply(
        *this,
        CommonAPI::SomeIP::method_id_t(0x103),
        true,
        false,
        (_info ? _info : &CommonAPI::SomeIP::defaultCallInfo),
        _internalCallStatus,
        deploy_allDoors);
    _allDoors = deploy_allDoors.getValue();
}

template<typename ... _AttributeExtensions>
std::future<CommonAPI::CallStatus> DoorControlSomeIPProxy<_AttributeExtensions...>::getAllDoorStatusAsync(GetAllDoorStatusAsyncCallback _callback, const CommonAPI::CallInfo *_info) {
    CommonAPI::Deployable< std::vector< DoorControl::DoorStatus >, CommonAPI::SomeIP::ArrayDeployment< CommonAPI::EmptyDeployment >> deploy_allDoors(static_cast< CommonAPI::SomeIP::ArrayDeployment< CommonAPI::EmptyDeployment >* >(nullptr));
    return CommonAPI::SomeIP::ProxyHelper<
        CommonAPI::SomeIP::SerializableArguments<
        >,
        CommonAPI::SomeIP::SerializableArguments<
            CommonAPI::Deployable<
                std::vector< DoorControl::DoorStatus >,
                CommonAPI::SomeIP::ArrayDeployment< CommonAPI::EmptyDeployment >
            >
        >
    >::callMethodAsync(
        *this,
        CommonAPI::SomeIP::method_id_t(0x103),
        true,
        false,
        (_info ? _info : &CommonAPI::SomeIP::defaultCallInfo),
        [_callback] (CommonAPI::CallStatus _internalCallStatus, CommonAPI::Deployable< std::vector< DoorControl::DoorStatus >, CommonAPI::SomeIP::ArrayDeployment< CommonAPI::EmptyDeployment > > _allDoors) {
            if (_callback)
                _callback(_internalCallStatus, _allDoors.getValue());
        },
        std::make_tuple(deploy_allDoors));
}

template<typename ... _AttributeExtensions>
void DoorControlSomeIPProxy<_AttributeExtensions...>::getOwnVersion(uint16_t& ownVersionMajor, uint16_t& ownVersionMinor) const {
    ownVersionMajor = 1;
    ownVersionMinor = 0;
}

template<typename ... _AttributeExtensions>
std::future<void> DoorControlSomeIPProxy<_AttributeExtensions...>::getCompletionFuture() {
    return CommonAPI::SomeIP::Proxy::getCompletionFuture();
}

template class DoorControlSomeIPProxy<>;

}
}
}
