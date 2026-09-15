#pragma once
#include "pet/sprite.hpp"

namespace pet {
enum class Motion : std::uint8_t { Idle, Walk, Hop, Happy, Sleep, Eat, Tired, Sick, Look };
constexpr unsigned motion_count = 9;
struct SpriteFrame {
    Sprite sprite;
    std::int8_t x, y;
    std::uint16_t duration_ms;
};
unsigned frame_count(Species species, Motion motion);
SpriteFrame animation_frame(Species species, Motion motion, unsigned frame);
std::size_t animation_storage_bytes();
const char* motion_name(Motion motion);
struct AnimationView {
    Motion motion = Motion::Idle;
    std::uint8_t frame = 0;
    std::int8_t x = 0, y = 0;
    bool flip = false;
};
// Cosmetic state only. Its PRNG never consumes the gameplay PRNG or enters saves.
class Animator {
public:
    explicit Animator(std::uint32_t seed = 0xabc123u) : rng_(seed ? seed : 1) {}
    void advance(const State& state, std::uint32_t ms);
    void fed(const State& state);
    AnimationView view(const State& state) const;
private:
    Motion motion_ = Motion::Idle;
    std::uint32_t rng_;
    std::uint32_t elapsed_ = 0;
    std::uint32_t duration_ = 2500;
    Species species_ = Species::Egg;
    bool flip_ = false;
    bool resting_ = true;
    std::uint32_t random();
    void start(Motion motion, std::uint32_t duration);
    void choose(const State& state);
};
}
