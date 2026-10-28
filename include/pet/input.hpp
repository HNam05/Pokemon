#pragma once
#include <cstdint>

namespace pet {
// Debounced three-button contract shared by GPIO firmware and the simulator.
// Feed raw levels (bit 0 left, bit 1 OK, bit 2 right; 1 = pressed) with a monotonic
// millisecond clock. Short OK fires on release, holding OK fires one back(),
// side buttons fire on press and auto-repeat only where the game allows it.
struct InputEvents {
    std::uint8_t presses = 0; // bit per Button value
    bool back = false;
    bool any() const { return presses != 0 || back; }
};

class InputDecoder {
public:
    static constexpr std::uint32_t debounce_ms = 30, hold_ms = 700, repeat_delay_ms = 450, repeat_ms = 160;
    InputEvents update(std::uint8_t raw, std::uint32_t now_ms, bool side_repeat);
    std::uint8_t stable() const { return stable_; }
private:
    std::uint8_t raw_ = 0, stable_ = 0;
    bool hold_fired_ = false;
    std::uint32_t changed_at_[3]{};
    std::uint32_t pressed_at_[3]{};
    std::uint32_t next_repeat_[3]{};
};
}
