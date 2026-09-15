#pragma once
#include "pet/game.hpp"
#include <cstddef>
#include <cstdint>

namespace pet {
struct Sprite {
    const std::uint8_t* pixels;
    const std::uint16_t* palette;
    std::uint8_t width;
    std::uint8_t height;
    std::uint8_t colors;
    std::uint8_t at(unsigned x, unsigned y) const {
        if (x >= width || y >= height) return 0;
        const unsigned index = y * width + x;
        return static_cast<std::uint8_t>((pixels[index / 2] >> (index % 2 == 0 ? 4 : 0)) & 15);
    }
};
Sprite sprite_for(Species species);
std::size_t sprite_storage_bytes();
}
