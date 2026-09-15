#include "pet/animation.hpp"
#include <algorithm>

namespace pet {
namespace {
struct Clip { const SpriteFrame* frames; unsigned count; };
#include "eevee_frames.inc"
Motion condition(const State& s) {
    if (s.species == Species::Egg) return Motion::Idle;
    if (s.sleeping) return Motion::Sleep;
    if (s.sick || s.health < 40) return Motion::Sick;
    if (s.energy < 25) return Motion::Tired;
    return Motion::Idle;
}
}
// Authored procedural poses of the existing project art, defined beside its palette.
Sprite authored_pose(Species species, Motion motion, unsigned frame);
std::size_t authored_pose_bytes();
unsigned frame_count(Species species, Motion motion) {
    const auto i = static_cast<unsigned>(motion);
    if (i >= motion_count) return 1;
    if (species == Species::Eevee) return imported_clips[i].count;
    return species == Species::Egg ? 1 : 4;
}
SpriteFrame animation_frame(Species species, Motion motion, unsigned frame) {
    const auto i = static_cast<unsigned>(motion);
    if (species == Species::Eevee && i < motion_count) {
        const auto& clip = imported_clips[i];
        return clip.frames[frame % clip.count];
    }
    const auto sprite = authored_pose(species,motion,frame % 4);
    const auto duration = motion==Motion::Idle ? (frame%4==3 ? 140 : 800) : motion==Motion::Sleep ? 600 : 180;
    return {sprite,static_cast<std::int8_t>(-sprite.width/2),static_cast<std::int8_t>(-sprite.height/2),
            static_cast<std::uint16_t>(duration)};
}
std::size_t animation_storage_bytes() {
    std::size_t bytes = imported_pixel_bytes + sizeof(imported_clips) + authored_pose_bytes();
    for (const auto& clip : imported_clips) bytes += clip.count * sizeof(SpriteFrame);
    return bytes;
}
const char* motion_name(Motion motion) {
    constexpr const char* names[] = {"idle","walk","hop","happy","sleep","eat","tired","sick","look"};
    const auto i = static_cast<unsigned>(motion);
    return i < motion_count ? names[i] : "idle";
}
std::uint32_t Animator::random() {
    rng_ ^= rng_ << 13; rng_ ^= rng_ >> 17; rng_ ^= rng_ << 5;
    return rng_;
}
void Animator::start(Motion motion, std::uint32_t duration) {
    motion_ = motion; elapsed_ = 0; duration_ = duration;
}
void Animator::choose(const State& state) {
    resting_ = !resting_;
    if (resting_) { start(Motion::Idle,2000 + random()%3000); return; }
    const Motion active[] = {Motion::Walk,Motion::Look,Motion::Hop,Motion::Happy};
    // A hungry or sad pet still moves but does not celebrate without reason.
    auto next = active[random() % ((state.fullness < 25 || state.happiness < 30) ? 2 : 4)];
    flip_ = (random() & 1) != 0;
    start(next, 1600 + random()%1800);
}
void Animator::advance(const State& state, std::uint32_t ms) {
    if (species_ != state.species) {
        species_ = state.species; resting_ = true; start(Motion::Idle,2500);
    }
    const auto forced = condition(state);
    if (forced != Motion::Idle) {
        if (motion_ != forced) start(forced,60000);
        elapsed_ = (elapsed_ + std::min(ms,60000u)) % 60000;
        return;
    }
    if (motion_ == Motion::Sleep || motion_ == Motion::Sick || motion_ == Motion::Tired) {
        resting_ = true; start(Motion::Idle,2500);
    }
    if ((state.fullness < 25 || state.happiness < 30) && (motion_==Motion::Hop || motion_==Motion::Happy)) {
        resting_ = true; start(Motion::Idle,2500);
    }
    if (state.species == Species::Egg) return;
    ms = std::min(ms,60000u);
    while (ms > 0) {
        const auto step = std::min(ms,duration_ - elapsed_);
        elapsed_ += step; ms -= step;
        if (elapsed_ == duration_) choose(state);
    }
}
void Animator::fed(const State& state) {
    advance(state,0);
    if (condition(state) == Motion::Idle && state.species != Species::Egg) {
        resting_ = false; start(Motion::Eat,2200);
    }
}
AnimationView Animator::view(const State& state) const {
    AnimationView result;
    result.motion = condition(state) != Motion::Idle ? condition(state) : motion_;
    const auto count = frame_count(state.species,result.motion);
    std::uint32_t cycle = 0;
    for (unsigned i = 0; i < count; ++i) cycle += animation_frame(state.species,result.motion,i).duration_ms;
    auto time = elapsed_ % cycle;
    for (unsigned i = 0; i < count; ++i) {
        const auto duration = animation_frame(state.species,result.motion,i).duration_ms;
        if (time < duration) { result.frame = static_cast<std::uint8_t>(i); break; }
        time -= duration;
    }
    result.flip = flip_ && result.motion == Motion::Walk;
    if (result.motion == Motion::Walk) {
        // Return to the center before the next clip; no accumulated position drift.
        const auto phase = elapsed_ * 4 / duration_;
        const auto fraction = elapsed_ * 48 / duration_;
        const int x = phase < 2 ? static_cast<int>(fraction) : 48 - static_cast<int>(fraction);
        result.x = static_cast<std::int8_t>(flip_ ? -x : x);
        result.flip = (phase >= 2) != flip_;
    }
    if (state.species != Species::Eevee && result.motion == Motion::Hop) {
        constexpr std::int8_t heights[] = {0,-4,-8,-10,-8,-4,0,0};
        result.y = heights[(elapsed_/100)%8];
    }
    if (state.species == Species::Eevee && result.motion == Motion::Hop) {
        // Halve the source jump's vertical travel at 4x display scale so the ears
        // stay below the header. The sprite's own registration remains intact.
        const auto source = animation_frame(state.species,result.motion,result.frame);
        result.y = static_cast<std::int8_t>((-15-source.y)*2);
    }
    if (state.species != Species::Eevee && (result.motion==Motion::Happy || result.motion==Motion::Sleep))
        result.y=static_cast<std::int8_t>((elapsed_/600)%2 ? -1 : 0);
    return result;
}
}
