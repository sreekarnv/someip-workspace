#include <iostream>
#include <thread>

#include <CommonAPI/CommonAPI.hpp>
#include "DoorControlStubImpl.hpp"

using namespace std;

int main() {
    CommonAPI::Runtime::setProperty("LogContext", "DoorControlService");
    CommonAPI::Runtime::setProperty("LogApplication", "door-control-service");

    std::shared_ptr<CommonAPI::Runtime> runtime = CommonAPI::Runtime::get();

    std::string domain = "local";
    std::string instance = "vehicle.doors.DoorControl";
    std::string connection = "door-control-service";

    std::shared_ptr<DoorControlStubImpl> myService = std::make_shared<DoorControlStubImpl>();
    bool successfullyRegistered = runtime->registerService(domain, instance, myService, connection);

    while (!successfullyRegistered) {
        std::cout << "Register Service failed, trying again in 100ms..." << std::endl;
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        successfullyRegistered = runtime->registerService(domain, instance, myService, connection);
    }

    std::cout << "Door Control Service registered!" << std::endl;

    while (true) {
        std::this_thread::sleep_for(std::chrono::seconds(60));
    }

    return 0;
}
