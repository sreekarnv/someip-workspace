#include <iostream>
#include <string>
#include <thread>

#include <CommonAPI/CommonAPI.hpp>
#include <v1/vehicle/doors/DoorControlSomeIPProxy.hpp>

using namespace v1::vehicle::doors;

const char* doorName(DoorControl::DoorPosition door) {
    switch (door) {
        case DoorControl::DoorPosition::FRONT_LEFT:  return "Front-Left";
        case DoorControl::DoorPosition::FRONT_RIGHT: return "Front-Right";
        case DoorControl::DoorPosition::REAR_LEFT:   return "Rear-Left";
        case DoorControl::DoorPosition::REAR_RIGHT:  return "Rear-Right";
        default: return "Unknown";
    }
}

const char* stateName(DoorControl::DoorState state) {
    switch (state) {
        case DoorControl::DoorState::LOCKED:   return "LOCKED";
        case DoorControl::DoorState::UNLOCKED: return "UNLOCKED";
        case DoorControl::DoorState::OPEN:     return "OPEN";
        case DoorControl::DoorState::CLOSED:   return "CLOSED";
        case DoorControl::DoorState::JAMMED:   return "JAMMED";
        default: return "Unknown";
    }
}

void printDoorStatus(DoorControl::DoorPosition door, const DoorControl::DoorStatus& status) {
    std::cout << "  " << doorName(door) << ": "
              << stateName(status.getDoorState())
              << " | childLock=" << (status.getChildLock() ? "ON" : "OFF")
              << " | window=" << (int)status.getWindowPercent() << "%"
              << std::endl;
}

int main() {
    CommonAPI::Runtime::setProperty("LogContext", "DoorControlClient");
    CommonAPI::Runtime::setProperty("LogApplication", "door-control-client");

    std::shared_ptr<CommonAPI::Runtime> runtime = CommonAPI::Runtime::get();

    std::string domain = "local";
    std::string instance = "vehicle.doors.DoorControl";
    std::string connection = "door-control-client";

    std::shared_ptr<DoorControlSomeIPProxy<>> myProxy =
        runtime->buildProxy<DoorControlSomeIPProxy>(domain, instance, connection);

    if (!myProxy || !myProxy->init()) {
        std::cerr << "Failed to initialize DoorControl proxy." << std::endl;
        return 1;
    }

    std::cout << "Waiting for DoorControl service..." << std::endl;
    while (!myProxy->isAvailable())
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
    std::cout << "Service available!" << std::endl;

    // Subscribe to door state change events
    myProxy->getOnDoorStateChangedEvent().subscribe(
        [](uint32_t door, const DoorControl::DoorStatus& status) {
            std::cout << "[EVENT] " << doorName(static_cast<DoorControl::DoorPosition>(door)) << " -> "
                      << stateName(status.getDoorState()) << std::endl;
        });

    CommonAPI::CallStatus callStatus;
    CommonAPI::CallInfo info(3000);

    // Get all door status
    std::cout << "\n=== Initial Door Status ===" << std::endl;
    std::vector<DoorControl::DoorStatus> allDoors;
    myProxy->getAllDoorStatus(callStatus, allDoors, &info);
    if (callStatus == CommonAPI::CallStatus::SUCCESS) {
        for (size_t i = 0; i < allDoors.size(); i++) {
            printDoorStatus(static_cast<DoorControl::DoorPosition>(i), allDoors[i]);
        }
    }

    // Lock all doors
    std::cout << "\n=== Locking All Doors ===" << std::endl;
    myProxy->lockAllDoors(callStatus);
    std::this_thread::sleep_for(std::chrono::seconds(1));

    // Get status after lock
    std::cout << "\n=== Status After Lock ===" << std::endl;
    myProxy->getAllDoorStatus(callStatus, allDoors, &info);
    if (callStatus == CommonAPI::CallStatus::SUCCESS) {
        for (size_t i = 0; i < allDoors.size(); i++) {
            printDoorStatus(static_cast<DoorControl::DoorPosition>(i), allDoors[i]);
        }
    }

    // Unlock front-left door
    std::cout << "\n=== Unlocking Front-Left Door ===" << std::endl;
    bool success;
    myProxy->unlockDoor(DoorControl::DoorPosition::FRONT_LEFT, callStatus, success, &info);
    std::cout << "Unlock result: " << (success ? "SUCCESS" : "FAILED") << std::endl;
    std::this_thread::sleep_for(std::chrono::seconds(1));

    // Get single door status
    std::cout << "\n=== Front-Left Door Status ===" << std::endl;
    DoorControl::DoorStatus flStatus;
    myProxy->getDoorStatus(DoorControl::DoorPosition::FRONT_LEFT, callStatus, flStatus, &info);
    if (callStatus == CommonAPI::CallStatus::SUCCESS) {
        printDoorStatus(DoorControl::DoorPosition::FRONT_LEFT, flStatus);
    }

    std::cout << "\n=== Done ===" << std::endl;
    return 0;
}
