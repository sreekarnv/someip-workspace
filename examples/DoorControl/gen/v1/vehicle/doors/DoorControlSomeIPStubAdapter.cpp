#include <v1/vehicle/doors/DoorControlSomeIPStubAdapter.hpp>

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

std::shared_ptr<CommonAPI::SomeIP::StubAdapter> createDoorControlSomeIPStubAdapter(
                   const CommonAPI::SomeIP::Address &_address,
                   const std::shared_ptr<CommonAPI::SomeIP::ProxyConnection> &_connection,
                   const std::shared_ptr<CommonAPI::StubBase> &_stub) {
    return std::make_shared< DoorControlSomeIPStubAdapter<::v1::vehicle::doors::DoorControlStub>>(_address, _connection, _stub);
}

void initializeDoorControlSomeIPStubAdapter() {
    CommonAPI::SomeIP::AddressTranslator::get()->insert(
        "local:vehicle.doors.DoorControl:v1_0:vehicle.doors.DoorControl",
         0x1001, 0x1, 1, 0);
    CommonAPI::SomeIP::Factory::get()->registerStubAdapterCreateMethod(
        "vehicle.doors.DoorControl:v1_0",
        &createDoorControlSomeIPStubAdapter);
}

INITIALIZER(registerDoorControlSomeIPStubAdapter) {
    CommonAPI::SomeIP::Factory::get()->registerInterface(initializeDoorControlSomeIPStubAdapter);
}

}
}
}
