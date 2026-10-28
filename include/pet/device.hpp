#pragma once
#include "pet/animation.hpp"
#include "pet/game.hpp"
#include "pet/input.hpp"
#include "pet/profile.hpp"
#include "pet/render.hpp"

namespace pet {
// Everything one handheld runs, independent of the platform: rules, cosmetic animation,
// the three-button decoder, the profile and the screen renderer. Firmware wraps it with
// GPIO, LCD, NVS and clock drivers; the desktop bridge wraps it with a C ABI.
class Device {
public:
    explicit Device(std::uint32_t animation_seed = 0xabc123u) : animator_(animation_seed) {}
    Game game;
    Profile profile;
    void advance(std::uint32_t real_ms, std::uint32_t speed = 1);
    void press(Button button);
    void back();
    // Raw button levels from GPIO or simulator; returns true when the game reacted.
    bool input(std::uint8_t raw, std::uint32_t now_ms);
    bool load(const State& state);
    void reseed(std::uint32_t seed) { animator_ = Animator(seed); }
    AnimationView pose(bool reduced_motion) const;
    void render(Band band, bool reduced_motion) const;
    // Last cosmetic event for sound/vibration adapters; cleared when read.
    Event take_event() { const auto e = event_; event_ = Event::None; return e; }
    std::uint32_t uptime_ms() const { return uptime_ms_; }
private:
    Animator animator_;
    InputDecoder decoder_;
    std::uint32_t uptime_ms_ = 0;
    Event event_ = Event::None;
    void settle();
};
}
