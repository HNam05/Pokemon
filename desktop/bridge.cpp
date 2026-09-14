#include "pet/game.hpp"
#include "pet/save.hpp"
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
    char json[2048]{};
};
}
PET_EXPORT Session* pp_create() { return new (std::nothrow) Session; }
PET_EXPORT void pp_destroy(Session* session) { delete session; }
PET_EXPORT void pp_advance(Session* session, std::uint32_t ms, std::uint32_t speed) {
    if (session) session->game.advance(ms, speed);
}
PET_EXPORT bool pp_button(Session* session, int button) {
    if (!session || button < 0 || button > 2) return false;
    session->game.button(static_cast<pet::Button>(button));
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
        "\"message\":\"%s\",\"mini\":{\"elapsed_ms\":%u,\"lane\":%u,\"target\":%u,\"round\":%u,\"score\":%u}}",
        static_cast<unsigned>(s.species), pet::species_name(s.species), static_cast<unsigned>(g.screen()),
        static_cast<unsigned>(g.selection()), static_cast<unsigned>(s.age_minutes),
        static_cast<unsigned>(s.minute_of_day), static_cast<unsigned>(s.fullness),
        static_cast<unsigned>(s.happiness), static_cast<unsigned>(s.energy), static_cast<unsigned>(s.hygiene),
        static_cast<unsigned>(s.health), static_cast<unsigned>(s.friendship), static_cast<unsigned>(s.experience),
        static_cast<unsigned>(s.waste), s.sleeping ? "true" : "false", s.sick ? "true" : "false",
        g.needs_attention() ? "true" : "false", g.can_evolve() ? "true" : "false", g.message(),
        static_cast<unsigned>(m.elapsed_ms), static_cast<unsigned>(m.lane), static_cast<unsigned>(m.target),
        static_cast<unsigned>(m.round), static_cast<unsigned>(m.score));
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
    return session && pet::decode(input, size, state) && session->game.restore(state);
}
