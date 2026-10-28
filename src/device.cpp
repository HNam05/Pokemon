#include "pet/device.hpp"

namespace pet {
void Device::advance(std::uint32_t real_ms, std::uint32_t speed) {
    game.advance(real_ms, speed);
    animator_.advance(game.state(), speed && game.screen() == Screen::Home ? real_ms : 0);
    uptime_ms_ += real_ms;
    settle();
}

void Device::press(Button button) {
    game.button(button);
    settle();
}

void Device::back() {
    game.back();
    settle();
}

bool Device::input(std::uint8_t raw, std::uint32_t now_ms) {
    const auto events = decoder_.update(raw, now_ms, game.repeats_side_buttons());
    for (unsigned b = 0; b < 3; ++b)
        if (events.presses & (1u << b)) press(static_cast<Button>(b));
    if (events.back) back();
    return events.any();
}

bool Device::load(const State& state) {
    if (!game.restore(state)) return false;
    settle();
    return true;
}

void Device::settle() {
    animator_.advance(game.state(), 0);
    const auto event = game.take_event();
    if (event == Event::Fed) animator_.fed(game.state());
    if (event == Event::Petted) animator_.petted(game.state());
    if (event != Event::None) event_ = event;
}

AnimationView Device::pose(bool reduced_motion) const {
    auto view = animator_.view(game.state());
    if (reduced_motion) {
        const bool condition = view.motion == Motion::Sleep || view.motion == Motion::Tired || view.motion == Motion::Sick;
        view = {condition ? view.motion : Motion::Idle, 0, 0, 0, false};
    }
    return view;
}

void Device::render(Band band, bool reduced_motion) const {
    pet::render({game, pose(reduced_motion), profile.name(), uptime_ms_}, band);
}
}
