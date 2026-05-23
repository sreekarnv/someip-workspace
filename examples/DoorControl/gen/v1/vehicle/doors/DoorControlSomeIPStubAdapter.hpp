#ifndef V1_VEHICLE_DOORS_DOOR_CONTROL_SOMEIP_STUB_ADAPTER_HPP_
#define V1_VEHICLE_DOORS_DOOR_CONTROL_SOMEIP_STUB_ADAPTER_HPP_

#include <v1/vehicle/doors/DoorControl.hpp>
#include <v1/vehicle/doors/DoorControlStub.hpp>

#if !defined (COMMONAPI_INTERNAL_COMPILATION)
#define COMMONAPI_INTERNAL_COMPILATION
#define HAS_DEFINED_COMMONAPI_INTERNAL_COMPILATION_HERE
#endif

#include <CommonAPI/SomeIP/AddressTranslator.hpp>
#include <CommonAPI/SomeIP/StubAdapterHelper.hpp>
#include <CommonAPI/SomeIP/StubAdapter.hpp>
#include <CommonAPI/SomeIP/Factory.hpp>
#include <CommonAPI/SomeIP/Types.hpp>
#include <CommonAPI/SomeIP/Deployment.hpp>

#if defined (HAS_DEFINED_COMMONAPI_INTERNAL_COMPILATION_HERE)
#undef COMMONAPI_INTERNAL_COMPILATION
#undef HAS_DEFINED_COMMONAPI_INTERNAL_COMPILATION_HERE
#endif

#include <memory>
#include <string>

namespace v1 {
namespace vehicle {
namespace doors {

class DoorControlSomeIPStubAdapterBase
    : public virtual CommonAPI::SomeIP::StubAdapter {
public:
    virtual ~DoorControlSomeIPStubAdapterBase() {}

    virtual void fireOnDoorStateChangedEvent(const uint32_t &_door, const ::v1::vehicle::doors::DoorControl::DoorStatus &_status) = 0;
    virtual void registerSelectiveEventHandlers() = 0;
    virtual void unregisterSelectiveEventHandlers() = 0;
};

template <typename _Stub = ::v1::vehicle::doors::DoorControlStub, typename... _Stubs>
class DoorControlSomeIPStubAdapterInternal
    : public virtual DoorControlSomeIPStubAdapterBase,
      public CommonAPI::SomeIP::StubAdapterHelper< _Stub, _Stubs...>,
      public std::enable_shared_from_this< DoorControlSomeIPStubAdapterInternal<_Stub, _Stubs...>>
{
public:
    typedef CommonAPI::SomeIP::StubAdapterHelper< _Stub, _Stubs...> BaseHelper;

    ~DoorControlSomeIPStubAdapterInternal() {
        deactivateManagedInstances();
        BaseHelper::deinit();
    }

    void fireOnDoorStateChangedEvent(const uint32_t &_door, const ::v1::vehicle::doors::DoorControl::DoorStatus &_status);

    void deactivateManagedInstances() {}

    CommonAPI::SomeIP::GetAttributeStubDispatcher<
        ::v1::vehicle::doors::DoorControlStub,
        CommonAPI::Version
    > getDoorControlInterfaceVersionStubDispatcher;

    CommonAPI::SomeIP::MethodStubDispatcher<
        ::v1::vehicle::doors::DoorControlStub,
        std::tuple< >,
        std::tuple< >
    > lockAllDoorsStubDispatcher;

    CommonAPI::SomeIP::MethodWithReplyStubDispatcher<
        ::v1::vehicle::doors::DoorControlStub,
        std::tuple< uint32_t >,
        std::tuple< bool >,
        std::tuple< CommonAPI::EmptyDeployment >,
        std::tuple< CommonAPI::EmptyDeployment >
    > unlockDoorStubDispatcher;

    CommonAPI::SomeIP::MethodWithReplyStubDispatcher<
        ::v1::vehicle::doors::DoorControlStub,
        std::tuple< uint32_t >,
        std::tuple< DoorControl::DoorStatus >,
        std::tuple< CommonAPI::EmptyDeployment >,
        std::tuple< CommonAPI::EmptyDeployment >
    > getDoorStatusStubDispatcher;

    CommonAPI::SomeIP::MethodWithReplyStubDispatcher<
        ::v1::vehicle::doors::DoorControlStub,
        std::tuple< >,
        std::tuple< std::vector<DoorControl::DoorStatus> >,
        std::tuple< >,
        std::tuple< CommonAPI::SomeIP::ArrayDeployment<CommonAPI::EmptyDeployment> >
    > getAllDoorStatusStubDispatcher;

    DoorControlSomeIPStubAdapterInternal(
        const CommonAPI::SomeIP::Address &_address,
        const std::shared_ptr<CommonAPI::SomeIP::ProxyConnection> &_connection,
        const std::shared_ptr<CommonAPI::StubBase> &_stub):
        CommonAPI::SomeIP::StubAdapter(_address, _connection),
        BaseHelper(_address, _connection, std::dynamic_pointer_cast< DoorControlStub>(_stub)),
        getDoorControlInterfaceVersionStubDispatcher(&DoorControlStub::lockInterfaceVersionAttribute, &DoorControlStub::getInterfaceVersion, false, true),
        lockAllDoorsStubDispatcher(&DoorControlStub::lockAllDoors, false, _stub->hasElement(0), std::make_tuple()),
        unlockDoorStubDispatcher(
            &DoorControlStub::unlockDoor,
            false,
            _stub->hasElement(1),
            std::make_tuple(static_cast< CommonAPI::EmptyDeployment* >(nullptr)),
            std::make_tuple(static_cast< CommonAPI::EmptyDeployment* >(nullptr))),
        getDoorStatusStubDispatcher(
            &DoorControlStub::getDoorStatus,
            false,
            _stub->hasElement(2),
            std::make_tuple(static_cast< CommonAPI::EmptyDeployment* >(nullptr)),
            std::make_tuple(static_cast< CommonAPI::EmptyDeployment* >(nullptr))),
        getAllDoorStatusStubDispatcher(
            &DoorControlStub::getAllDoorStatus,
            false,
            _stub->hasElement(3),
            std::make_tuple(),
            std::make_tuple(static_cast< CommonAPI::SomeIP::ArrayDeployment<CommonAPI::EmptyDeployment>* >(nullptr)))
    {
        BaseHelper::addStubDispatcher({ CommonAPI::SomeIP::method_id_t(0x100) }, &lockAllDoorsStubDispatcher);
        BaseHelper::addStubDispatcher({ CommonAPI::SomeIP::method_id_t(0x101) }, &unlockDoorStubDispatcher);
        BaseHelper::addStubDispatcher({ CommonAPI::SomeIP::method_id_t(0x102) }, &getDoorStatusStubDispatcher);
        BaseHelper::addStubDispatcher({ CommonAPI::SomeIP::method_id_t(0x103) }, &getAllDoorStatusStubDispatcher);

        std::set<CommonAPI::SomeIP::eventgroup_id_t> itsEventGroups;
        itsEventGroups.insert(CommonAPI::SomeIP::eventgroup_id_t(0x1));
        CommonAPI::SomeIP::StubAdapter::registerEvent(CommonAPI::SomeIP::event_id_t(0x8001), itsEventGroups, CommonAPI::SomeIP::event_type_e::ET_EVENT, CommonAPI::SomeIP::reliability_type_e::RT_UNRELIABLE);
    }

    void registerSelectiveEventHandlers();
    void unregisterSelectiveEventHandlers();
};

template <typename _Stub, typename... _Stubs>
void DoorControlSomeIPStubAdapterInternal<_Stub, _Stubs...>::fireOnDoorStateChangedEvent(const uint32_t &_door, const ::v1::vehicle::doors::DoorControl::DoorStatus &_status) {
    CommonAPI::Deployable< DoorControl::DoorStatus, CommonAPI::EmptyDeployment> deployed_status(_status, static_cast< CommonAPI::EmptyDeployment* >(nullptr));
    CommonAPI::SomeIP::StubEventHelper<CommonAPI::SomeIP::SerializableArguments<  uint32_t
    ,  CommonAPI::Deployable< ::v1::vehicle::doors::DoorControl::DoorStatus, CommonAPI::EmptyDeployment >
    >>
        ::sendEvent(
            *this,
            CommonAPI::SomeIP::event_id_t(0x8001),
            false,
             _door
            ,  deployed_status
    );
}

template <typename _Stub, typename... _Stubs>
void DoorControlSomeIPStubAdapterInternal<_Stub, _Stubs...>::registerSelectiveEventHandlers() {
}

template <typename _Stub, typename... _Stubs>
void DoorControlSomeIPStubAdapterInternal<_Stub, _Stubs...>::unregisterSelectiveEventHandlers() {
}

template <typename _Stub = ::v1::vehicle::doors::DoorControlStub, typename... _Stubs>
class DoorControlSomeIPStubAdapter
    : public DoorControlSomeIPStubAdapterInternal<_Stub, _Stubs...> {
public:
    DoorControlSomeIPStubAdapter(
        const CommonAPI::SomeIP::Address &_address,
        const std::shared_ptr<CommonAPI::SomeIP::ProxyConnection> &_connection,
        const std::shared_ptr<CommonAPI::StubBase> &_stub)
        : CommonAPI::SomeIP::StubAdapter(_address, _connection),
          DoorControlSomeIPStubAdapterInternal<_Stub, _Stubs...>(_address, _connection, _stub) {
    }
};

}
}
}

#endif
