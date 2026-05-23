#include "DoorControlStubImpl.hpp"
#include <iostream>

DoorControlStubImpl::DoorControlStubImpl() {
    for (int i = 0; i < 4; i++) {
        doors_[i].state = DoorControl::DoorState::CLOSED;
        doors_[i].childLock = false;
        doors_[i].windowPercent = 0;
    }
}

DoorControlStubImpl::~DoorControlStubImpl() {
}

void DoorControlStubImpl::lockAllDoors(const std::shared_ptr<CommonAPI::ClientId> _client) {
    std::cout << "lockAllDoors: Locking all doors" << std::endl;
    for (int i = 0; i < 4; i++) {
        updateDoorState(static_cast<DoorControl::DoorPosition>(i), DoorControl::DoorState::LOCKED);
    }
}

void DoorControlStubImpl::unlockDoor(const std::shared_ptr<CommonAPI::ClientId> _client,
        uint32_t _door, unlockDoorReply_t _reply) {

    std::cout << "unlockDoor: door=" << _door << std::endl;
    bool success = (doors_[_door].state == DoorControl::DoorState::LOCKED);
    if (success) {
        updateDoorState(static_cast<DoorControl::DoorPosition>(_door), DoorControl::DoorState::UNLOCKED);
    }
    _reply(success);
}

void DoorControlStubImpl::getDoorStatus(const std::shared_ptr<CommonAPI::ClientId> _client,
        uint32_t _door, getDoorStatusReply_t _reply) {

    DoorControl::DoorStatus status;
    status.setDoorState(doors_[_door].state);
    status.setChildLock(doors_[_door].childLock);
    status.setWindowPercent(doors_[_door].windowPercent);

    std::cout << "getDoorStatus: door=" << _door
              << " state=" << static_cast<int>(status.getDoorState()) << std::endl;
    _reply(status);
}

void DoorControlStubImpl::getAllDoorStatus(const std::shared_ptr<CommonAPI::ClientId> _client,
        getAllDoorStatusReply_t _reply) {

    std::vector<DoorControl::DoorStatus> allDoors;
    for (int i = 0; i < 4; i++) {
        DoorControl::DoorStatus status;
        status.setDoorState(doors_[i].state);
        status.setChildLock(doors_[i].childLock);
        status.setWindowPercent(doors_[i].windowPercent);
        allDoors.push_back(status);
    }
    _reply(allDoors);
}

void DoorControlStubImpl::fireOnDoorStateChangedEvent(const uint32_t& _door,
        const DoorControl::DoorStatus& _status) {
    // Implemented by generated stub adapter
}

void DoorControlStubImpl::updateDoorState(DoorControl::DoorPosition door, DoorControl::DoorState newState) {
    int idx = static_cast<int>(door);
    doors_[idx].state = newState;

    DoorControl::DoorStatus status;
    status.setDoorState(doors_[idx].state);
    status.setChildLock(doors_[idx].childLock);
    status.setWindowPercent(doors_[idx].windowPercent);

    std::cout << "Door state changed: door=" << idx
              << " state=" << static_cast<int>(newState) << std::endl;

    fireOnDoorStateChangedEvent(static_cast<uint32_t>(door), status);
}
