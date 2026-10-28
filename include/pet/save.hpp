#pragma once
#include "pet/game.hpp"
#include <array>
#include <cstddef>

namespace pet {
using SaveBytes = std::array<std::uint8_t, 48>;
SaveBytes encode(const State& state);
bool decode(const std::uint8_t* bytes, std::size_t size, State& state);
} // namespace pet
