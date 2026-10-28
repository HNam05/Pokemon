#pragma once
#include "pet/animation.hpp"
#include "pet/game.hpp"
#include <cstdint>

namespace pet {
constexpr int screen_width = 240, screen_height = 320;

// A horizontal stripe of the 240x320 RGB565 screen. Firmware renders small stripes
// into a reusable DMA buffer; the simulator renders one stripe covering the screen.
struct Band {
    std::uint16_t* pixels; // screen_width * rows native-endian RGB565 values
    int top;
    int rows;
};

struct RenderInput {
    const Game& game;
    AnimationView pose;        // already reduced for calm motion when requested
    const char* trainer_name;  // validated profile text, may be empty
    std::uint32_t uptime_ms;   // drives blinking, never gameplay
};

// Draws exactly what the device shows. Pure function of its input: rendering any band
// split yields identical pixels.
void render(const RenderInput& input, Band band);

// Text helpers are exposed for adapters and tests.
int text_width(const char* utf8, int scale);
// True when every codepoint of the UTF-8 text has a glyph in the device font.
bool text_supported(const char* utf8);
}
