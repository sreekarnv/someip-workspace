#ifndef V1_VEHICLE_DOORS_DOOR_CONTROL_HPP_
#define V1_VEHICLE_DOORS_DOOR_CONTROL_HPP_

#ifndef COMMONAPI_INTERNAL_COMPILATION
#define COMMONAPI_INTERNAL_COMPILATION
#endif

#include <CommonAPI/Types.hpp>
#include <CommonAPI/Deployment.hpp>
#include <CommonAPI/Struct.hpp>

#include <vector>
#include <cstdint>

namespace v1 {
namespace vehicle {
namespace doors {

class DoorControl {
public:
    virtual ~DoorControl() {}

    enum class DoorPosition: uint32_t {
        FRONT_LEFT = 0,
        FRONT_RIGHT = 1,
        REAR_LEFT = 2,
        REAR_RIGHT = 3
    };

    enum class DoorState: uint32_t {
        LOCKED = 0,
        UNLOCKED = 1,
        OPEN = 2,
        CLOSED = 3,
        JAMMED = 4
    };

    class DoorStatus: public CommonAPI::Struct<uint32_t, bool, uint8_t> {
    public:
        DoorStatus() {}

        DoorState getDoorState() const { return static_cast<DoorState>(std::get<0>(values_)); }
        void setDoorState(DoorState _value) { std::get<0>(values_) = static_cast<uint32_t>(_value); }

        bool getChildLock() const { return std::get<1>(values_); }
        void setChildLock(bool _value) { std::get<1>(values_) = _value; }

        uint8_t getWindowPercent() const { return std::get<2>(values_); }
        void setWindowPercent(uint8_t _value) { std::get<2>(values_) = _value; }
    };
};

namespace DoorControl_ {

typedef CommonAPI::EmptyDeployment DoorPositionDeployment_t;
typedef CommonAPI::EmptyDeployment DoorStateDeployment_t;
typedef CommonAPI::EmptyDeployment DoorStatusDeployment_t;

}

}
}
}

#endif
