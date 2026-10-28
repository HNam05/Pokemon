#include "pet/device.hpp"
#include "pet/save.hpp"
#include "pet/sprite.hpp"
#include "pet/catalog.hpp"
#include <cstdio>
#include <cstring>
#include <new>

#if defined(_WIN32)
#define PET_EXPORT extern "C" __declspec(dllexport)
#else
#define PET_EXPORT extern "C" __attribute__((visibility("default")))
#endif

namespace {
bool valid_species_id(unsigned id) { return id<256 && pet::species_valid(static_cast<pet::Species>(id)); }
struct Session {
    pet::Device device;
    char animation_json[192]{};
    char json[2560]{};
};
}
PET_EXPORT Session* pp_create() { return new (std::nothrow) Session; }
PET_EXPORT void pp_destroy(Session* session) { delete session; }
PET_EXPORT bool pp_set_name(Session* session, const char* name, std::size_t size) {
    return session && session->device.profile.set_name(name, size);
}
PET_EXPORT const char* pp_name(Session* session) { return session ? session->device.profile.name() : ""; }
PET_EXPORT void pp_back(Session* session) { if (session) session->device.back(); }
PET_EXPORT void pp_animation_seed(Session* session, std::uint32_t seed) {
    if (session) session->device.reseed(seed);
}
PET_EXPORT const char* pp_animation(Session* session) {
    if (!session) return "{}";
    const auto& game = session->device.game;
    const auto a = session->device.pose(false);
    const unsigned shrink = game.stage() == pet::Stage::Baby ? 2 : game.stage() == pet::Stage::Child ? 1 : 0;
    const auto placement=pet::place_frame(game.state().species,a,shrink);
    std::snprintf(session->animation_json,sizeof(session->animation_json),
        "{\"clip\":%u,\"name\":\"%s\",\"frame\":%u,\"x\":%d,\"y\":%d,\"flip\":%s,\"draw_x\":%d,\"draw_y\":%d,\"scale\":%u}",
        static_cast<unsigned>(a.motion),pet::motion_name(a.motion),static_cast<unsigned>(a.frame),
        static_cast<int>(a.x),static_cast<int>(a.y),a.flip ? "true" : "false",
        static_cast<int>(placement.x),static_cast<int>(placement.y),static_cast<unsigned>(placement.scale));
    return session->animation_json;
}
// Device-identical screen: 240x320 native-endian RGB565, rendered by the shared C++ UI.
PET_EXPORT bool pp_render(Session* session, std::uint16_t* output, std::size_t count, bool reduced_motion) {
    if (!session || !output || count < static_cast<std::size_t>(pet::screen_width * pet::screen_height)) return false;
    session->device.render({output, 0, pet::screen_height}, reduced_motion);
    return true;
}
PET_EXPORT unsigned pp_menu_count() { return pet::Game::menu_count; }
PET_EXPORT const char* pp_menu_section(unsigned index) { return pet::Game::menu_section(static_cast<std::uint8_t>(index)); }
PET_EXPORT unsigned pp_need_low(unsigned index) { return index<6?pet::Game::need_low[index]:0; }
PET_EXPORT unsigned pp_starter_count() { return pet::starter_count(); }
PET_EXPORT unsigned pp_starter_at(unsigned index) { return static_cast<unsigned>(pet::starter_at(index)); }
PET_EXPORT const char* pp_species_name(unsigned id) { return valid_species_id(id)?pet::species_name(static_cast<pet::Species>(id)):"Unbekannt"; }
PET_EXPORT const char* pp_species_form(unsigned id) { return valid_species_id(id)?pet::species_form(static_cast<pet::Species>(id)):""; }
PET_EXPORT const char* pp_species_credit(unsigned id) { return valid_species_id(id)?pet::species_credit(static_cast<pet::Species>(id)):""; }
PET_EXPORT unsigned pp_species_scale(unsigned id) { return valid_species_id(id)?pet::species_scale(static_cast<pet::Species>(id)):1; }
PET_EXPORT unsigned pp_evolution_of(unsigned id) { return valid_species_id(id)?static_cast<unsigned>(pet::Game::evolution_of(static_cast<pet::Species>(id))):0; }
PET_EXPORT const char* pp_menu_label(unsigned index) {
    return index < pet::Game::menu_count ? pet::action_name(pet::Game::menu_action(static_cast<std::uint8_t>(index))) : "";
}
PET_EXPORT const char* pp_menu_hint(Session* session, unsigned index) {
    return session && index < pet::Game::menu_count ? session->device.game.action_hint(pet::Game::menu_action(static_cast<std::uint8_t>(index))) : "";
}
PET_EXPORT bool pp_menu_enabled(Session* session, unsigned index) {
    return session && index < pet::Game::menu_count && !session->device.game.blocked_reason(pet::Game::menu_action(static_cast<std::uint8_t>(index)));
}
PET_EXPORT const char* pp_care_hint(Session* session) { return session ? session->device.game.care_hint() : ""; }
PET_EXPORT unsigned pp_memory_bytes(unsigned kind) {
    switch (kind) {
    case 0: return sizeof(pet::Game);
    case 1: return sizeof(pet::State);
    case 2: return sizeof(pet::Profile);
    case 3: return static_cast<unsigned>(pet::sprite_storage_bytes());
    case 4: return static_cast<unsigned>(pet::animation_storage_bytes());
    case 5: return sizeof(pet::Animator);
    case 6: return sizeof(pet::Device);
    case 7: return static_cast<unsigned>(pet::scene_storage_bytes());
    default: return 0;
    }
}
PET_EXPORT void pp_advance(Session* session, std::uint32_t ms, std::uint32_t speed) {
    if (session) session->device.advance(ms, speed);
}
PET_EXPORT bool pp_button(Session* session, int button) {
    if (!session || button < 0 || button > 2) return false;
    session->device.press(static_cast<pet::Button>(button));
    return true;
}
// Raw levels (bit 0 left, bit 1 OK, bit 2 right) plus a monotonic clock in ms.
PET_EXPORT bool pp_input(Session* session, unsigned raw, std::uint32_t now_ms) {
    return session && raw < 8 && session->device.input(static_cast<std::uint8_t>(raw), now_ms);
}
PET_EXPORT const char* pp_view(Session* session) {
    if (!session) return "{}";
    const auto& g = session->device.game;
    const auto& s = g.state();
    const auto& m = g.mini();
    const auto& f = g.feedback();
    // All strings are controlled UTF-8 constants without JSON metacharacters.
    const int count = std::snprintf(session->json, sizeof(session->json),
        "{\"species\":%u,\"name\":\"%s\",\"screen\":%u,\"selection\":%u,"
        "\"age_minutes\":%u,\"minute_of_day\":%u,\"fullness\":%u,\"happiness\":%u,"
        "\"energy\":%u,\"hygiene\":%u,\"health\":%u,\"friendship\":%u,\"experience\":%u,"
        "\"waste\":%u,\"sleeping\":%s,\"sick\":%s,\"attention\":%s,\"can_evolve\":%s,"
        "\"message\":\"%s\",\"starter\":%u,\"starter_chosen\":%s,\"menu_start\":%u,"
        "\"care_mistakes\":%u,\"call_minutes\":%u,\"calling\":%s,\"pet_cooldown\":%u,\"night\":%s,"
        "\"stage\":%u,\"stage_name\":\"%s\",\"level\":%u,\"evolves_to\":%u,\"clock_edit\":%u,\"clock_field\":%u,\"evolved_from\":%u,"
        "\"mini\":{\"elapsed_ms\":%u,\"lane\":%u,\"target\":%u,\"round\":%u,\"score\":%u,"
        "\"memory\":%s,\"recalling\":%s,\"entered\":%u,\"pattern\":[%u,%u,%u,%u],"
        "\"phase\":%u,\"length\":%u,\"duration_ms\":%u,\"cue\":%d,\"last_button\":%u,\"input_ms\":%u,\"success\":%s,"
        "\"catch_open_ms\":%u,\"fall_ms\":%u},"
        "\"feedback\":{\"fullness\":%d,\"happiness\":%d,\"energy\":%d,\"hygiene\":%d,\"health\":%d,\"friendship\":%d,\"experience\":%u,\"remaining_ms\":%u}}",
        static_cast<unsigned>(s.species), pet::species_name(s.species), static_cast<unsigned>(g.screen()),
        static_cast<unsigned>(g.selection()), static_cast<unsigned>(s.age_minutes),
        static_cast<unsigned>(s.minute_of_day), static_cast<unsigned>(s.fullness),
        static_cast<unsigned>(s.happiness), static_cast<unsigned>(s.energy), static_cast<unsigned>(s.hygiene),
        static_cast<unsigned>(s.health), static_cast<unsigned>(s.friendship), static_cast<unsigned>(s.experience),
        static_cast<unsigned>(s.waste), s.sleeping ? "true" : "false", s.sick ? "true" : "false",
        g.needs_attention() ? "true" : "false", g.can_evolve() ? "true" : "false", g.message(),
        static_cast<unsigned>(s.starter), s.starter_chosen ? "true" : "false", static_cast<unsigned>(g.menu_start()),
        static_cast<unsigned>(s.care_mistakes), static_cast<unsigned>(s.call_minutes), g.calling() ? "true" : "false",
        static_cast<unsigned>(s.pet_cooldown), g.night() ? "true" : "false",
        static_cast<unsigned>(g.stage()), pet::stage_name(g.stage()), g.level(),
        static_cast<unsigned>(pet::Game::evolution_of(s.species)), static_cast<unsigned>(g.clock_edit()),
        static_cast<unsigned>(g.clock_field()), static_cast<unsigned>(g.evolved_from()),
        static_cast<unsigned>(m.elapsed_ms), static_cast<unsigned>(m.lane), static_cast<unsigned>(m.target),
        static_cast<unsigned>(m.round), static_cast<unsigned>(m.score), m.memory ? "true" : "false",
        m.recalling ? "true" : "false", static_cast<unsigned>(m.entered),
        static_cast<unsigned>(m.pattern[0]), static_cast<unsigned>(m.pattern[1]), static_cast<unsigned>(m.pattern[2]),static_cast<unsigned>(m.pattern[3]),
        static_cast<unsigned>(m.phase),static_cast<unsigned>(m.length),g.mini_duration(),g.memory_cue(),
        static_cast<unsigned>(m.last_button),static_cast<unsigned>(m.input_ms),m.success?"true":"false",
        pet::Game::catch_open_ms,pet::Game::berry_duration_ms,
        static_cast<int>(f.fullness),static_cast<int>(f.happiness),static_cast<int>(f.energy),static_cast<int>(f.hygiene),
        static_cast<int>(f.health),static_cast<int>(f.friendship),static_cast<unsigned>(f.experience),static_cast<unsigned>(f.remaining_ms));
    return count > 0 && static_cast<std::size_t>(count) < sizeof(session->json) ? session->json : "{}";
}
PET_EXPORT std::size_t pp_save(Session* session, std::uint8_t* output, std::size_t capacity) {
    if (!session || !output || capacity < pet::SaveBytes{}.size()) return 0;
    const auto bytes = pet::encode(session->device.game.state());
    std::memcpy(output, bytes.data(), bytes.size());
    return bytes.size();
}
PET_EXPORT bool pp_load(Session* session, const std::uint8_t* input, std::size_t size) {
    pet::State state;
    return session && pet::decode(input,size,state) && session->device.load(state);
}
