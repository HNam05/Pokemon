#include "pet/input.hpp"

namespace pet {
namespace {
// Wrap-safe: true when `now` has reached `deadline` on a 32-bit millisecond clock.
bool reached(std::uint32_t now, std::uint32_t deadline) {
    return static_cast<std::int32_t>(now - deadline) >= 0;
}
}

InputEvents InputDecoder::update(std::uint8_t raw, std::uint32_t now_ms, bool side_repeat) {
    InputEvents events;
    raw &= 7;
    for (unsigned b = 0; b < 3; ++b) {
        const std::uint8_t bit = static_cast<std::uint8_t>(1u << b);
        if ((raw ^ raw_) & bit) changed_at_[b] = now_ms;
        const bool level = raw & bit;
        if (level != static_cast<bool>(stable_ & bit) && now_ms - changed_at_[b] >= debounce_ms) {
            stable_ ^= bit;
            if (level) {
                pressed_at_[b] = now_ms;
                if (b == 1) hold_fired_ = false;
                else { events.presses |= bit; next_repeat_[b] = now_ms + repeat_delay_ms; }
            } else if (b == 1 && !hold_fired_) events.presses |= bit;
        }
        if (!(stable_ & bit)) continue;
        if (b == 1) {
            if (!hold_fired_ && now_ms - pressed_at_[b] >= hold_ms) { hold_fired_ = true; events.back = true; }
        } else if (!side_repeat) {
            next_repeat_[b] = now_ms + repeat_delay_ms;
        } else if (reached(now_ms, next_repeat_[b]) && !(events.presses & bit)) {
            events.presses |= bit;
            // A late caller gets one step, never a burst of queued repeats.
            next_repeat_[b] = reached(now_ms, next_repeat_[b] + repeat_ms) ? now_ms + repeat_ms : next_repeat_[b] + repeat_ms;
        }
    }
    raw_ = raw;
    return events;
}
}
