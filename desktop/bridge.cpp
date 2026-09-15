#include "pet/game.hpp"
#include "pet/save.hpp"
#include "pet/profile.hpp"
#include "pet/sprite.hpp"
#include "pet/animation.hpp"
#include <cstdio>
#include <cstring>
#include <new>

#if defined(_WIN32)
#define PET_EXPORT extern "C" __declspec(dllexport)
#else
#define PET_EXPORT extern "C" __attribute__((visibility("default")))
#endif

namespace {
struct Session {
    pet::Game game;
    pet::Profile profile;
    pet::Animator animator;
    char animation_json[192]{};
    char json[2048]{};
};
}
PET_EXPORT Session* pp_create() { return new (std::nothrow) Session; }
PET_EXPORT void pp_destroy(Session* session) { delete session; }
PET_EXPORT bool pp_set_name(Session* session, const char* name, std::size_t size) {
    return session && session->profile.set_name(name, size);
}
PET_EXPORT const char* pp_name(Session* session) { return session ? session->profile.name() : ""; }
PET_EXPORT void pp_back(Session* session) { if (session) session->game.back(); }
PET_EXPORT void pp_animation_seed(Session* session, std::uint32_t seed) {
    if (session) session->animator = pet::Animator(seed);
}
PET_EXPORT const char* pp_animation(Session* session) {
    if (!session) return "{}";
    const auto a = session->animator.view(session->game.state());
    std::snprintf(session->animation_json,sizeof(session->animation_json),
        "{\"clip\":%u,\"name\":\"%s\",\"frame\":%u,\"x\":%d,\"y\":%d,\"flip\":%s}",
        static_cast<unsigned>(a.motion),pet::motion_name(a.motion),static_cast<unsigned>(a.frame),
        static_cast<int>(a.x),static_cast<int>(a.y),a.flip ? "true" : "false");
    return session->animation_json;
}
PET_EXPORT int pp_frame_info(unsigned species, unsigned motion, unsigned frame, unsigned property) {
    if (species>4 || motion>=pet::motion_count) return 0;
    const auto s=static_cast<pet::Species>(species);
    const auto m=static_cast<pet::Motion>(motion);
    const auto f=pet::animation_frame(s,m,frame);
    switch (property) {
    case 0: return f.sprite.width;
    case 1: return f.sprite.height;
    case 2: return f.x;
    case 3: return f.y;
    case 4: return f.duration_ms;
    case 5: return static_cast<int>(pet::frame_count(s,m));
    default: return 0;
    }
}
PET_EXPORT unsigned pp_frame_pixel(unsigned species,unsigned motion,unsigned frame,unsigned x,unsigned y) {
    if (species>4 || motion>=pet::motion_count) return 0x10000u;
    const auto s=pet::animation_frame(static_cast<pet::Species>(species),static_cast<pet::Motion>(motion),frame).sprite;
    const auto index=s.at(x,y);
    return index==0 ? 0x10000u : s.palette[index];
}
PET_EXPORT unsigned pp_menu_count() { return pet::Game::menu_count; }
PET_EXPORT const char* pp_menu_label(unsigned index) {
    return index < pet::Game::menu_count ? pet::action_name(pet::Game::menu_action(static_cast<std::uint8_t>(index))) : "";
}
PET_EXPORT const char* pp_menu_hint(Session* session, unsigned index) {
    return session && index < pet::Game::menu_count ? session->game.action_hint(pet::Game::menu_action(static_cast<std::uint8_t>(index))) : "";
}
PET_EXPORT bool pp_menu_enabled(Session* session, unsigned index) {
    return session && index < pet::Game::menu_count && !session->game.blocked_reason(pet::Game::menu_action(static_cast<std::uint8_t>(index)));
}
PET_EXPORT const char* pp_care_hint(Session* session) { return session ? session->game.care_hint() : ""; }
PET_EXPORT unsigned pp_sprite_size(unsigned species, bool height) {
    if (species > static_cast<unsigned>(pet::Species::Psyduck)) return 0;
    const auto sprite = pet::sprite_for(static_cast<pet::Species>(species));
    return height ? sprite.height : sprite.width;
}
PET_EXPORT unsigned pp_sprite_pixel(unsigned species, unsigned x, unsigned y) {
    if (species > static_cast<unsigned>(pet::Species::Psyduck)) return 0;
    const auto sprite = pet::sprite_for(static_cast<pet::Species>(species));
    const auto index = sprite.at(x, y);
    return index == 0 ? 0x10000u : sprite.palette[index]; // sentinel distinguishes transparency from black.
}
PET_EXPORT unsigned pp_memory_bytes(unsigned kind) {
    switch (kind) {
    case 0: return sizeof(pet::Game);
    case 1: return sizeof(pet::State);
    case 2: return sizeof(pet::Profile);
    case 3: return static_cast<unsigned>(pet::sprite_storage_bytes());
    case 4: return static_cast<unsigned>(pet::animation_storage_bytes());
    case 5: return sizeof(pet::Animator);
    default: return 0;
    }
}
PET_EXPORT void pp_advance(Session* session, std::uint32_t ms, std::uint32_t speed) {
    if (session) {
        session->game.advance(ms, speed);
        session->animator.advance(session->game.state(), speed && session->game.screen()==pet::Screen::Home ? ms : 0);
    }
}
PET_EXPORT bool pp_button(Session* session, int button) {
    if (!session || button < 0 || button > 2) return false;
    const auto fullness=session->game.state().fullness;
    session->game.button(static_cast<pet::Button>(button));
    session->animator.advance(session->game.state(),0);
    if (session->game.state().fullness > fullness) session->animator.fed(session->game.state());
    return true;
}
PET_EXPORT const char* pp_view(Session* session) {
    if (!session) return "{}";
    const auto& g = session->game;
    const auto& s = g.state();
    const auto& m = g.mini();
    // All strings are controlled constants without JSON metacharacters.
    const int count = std::snprintf(session->json, sizeof(session->json),
        "{\"species\":%u,\"name\":\"%s\",\"screen\":%u,\"selection\":%u,"
        "\"age_minutes\":%u,\"minute_of_day\":%u,\"fullness\":%u,\"happiness\":%u,"
        "\"energy\":%u,\"hygiene\":%u,\"health\":%u,\"friendship\":%u,\"experience\":%u,"
        "\"waste\":%u,\"sleeping\":%s,\"sick\":%s,\"attention\":%s,\"can_evolve\":%s,"
        "\"message\":\"%s\",\"starter\":%u,\"starter_chosen\":%s,\"menu_start\":%u,"
        "\"mini\":{\"elapsed_ms\":%u,\"lane\":%u,\"target\":%u,\"round\":%u,\"score\":%u,"
        "\"memory\":%s,\"recalling\":%s,\"entered\":%u,\"pattern\":[%u,%u,%u]}}",
        static_cast<unsigned>(s.species), pet::species_name(s.species), static_cast<unsigned>(g.screen()),
        static_cast<unsigned>(g.selection()), static_cast<unsigned>(s.age_minutes),
        static_cast<unsigned>(s.minute_of_day), static_cast<unsigned>(s.fullness),
        static_cast<unsigned>(s.happiness), static_cast<unsigned>(s.energy), static_cast<unsigned>(s.hygiene),
        static_cast<unsigned>(s.health), static_cast<unsigned>(s.friendship), static_cast<unsigned>(s.experience),
        static_cast<unsigned>(s.waste), s.sleeping ? "true" : "false", s.sick ? "true" : "false",
        g.needs_attention() ? "true" : "false", g.can_evolve() ? "true" : "false", g.message(),
        static_cast<unsigned>(s.starter), s.starter_chosen ? "true" : "false", static_cast<unsigned>(g.menu_start()),
        static_cast<unsigned>(m.elapsed_ms), static_cast<unsigned>(m.lane), static_cast<unsigned>(m.target),
        static_cast<unsigned>(m.round), static_cast<unsigned>(m.score), m.memory ? "true" : "false",
        m.recalling ? "true" : "false", static_cast<unsigned>(m.entered),
        static_cast<unsigned>(m.pattern[0]), static_cast<unsigned>(m.pattern[1]), static_cast<unsigned>(m.pattern[2]));
    return count > 0 && static_cast<std::size_t>(count) < sizeof(session->json) ? session->json : "{}";
}
PET_EXPORT std::size_t pp_save(Session* session, std::uint8_t* output, std::size_t capacity) {
    if (!session || !output || capacity < pet::SaveBytes{}.size()) return 0;
    const auto bytes = pet::encode(session->game.state());
    std::memcpy(output, bytes.data(), bytes.size());
    return bytes.size();
}
PET_EXPORT bool pp_load(Session* session, const std::uint8_t* input, std::size_t size) {
    pet::State state;
    if (!session || !pet::decode(input,size,state) || !session->game.restore(state)) return false;
    session->animator.advance(state,0);
    return true;
}
