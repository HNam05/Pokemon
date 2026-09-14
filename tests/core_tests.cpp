#include "pet/game.hpp"
#include "pet/save.hpp"
#include <cstdlib>
#include <iostream>

namespace {
int checks = 0;
void check(bool success, const char* description) {
    ++checks;
    if (!success) { std::cerr << "FAIL: " << description << '\n'; std::exit(1); }
}
void select(pet::Game& game, pet::Action action) {
    while (game.screen() != pet::Screen::Home) game.button(pet::Button::Confirm);
    game.button(pet::Button::Confirm);
    while (game.selection() != static_cast<unsigned>(action)) game.button(pet::Button::Right);
    game.button(pet::Button::Confirm);
}
pet::State hatched() {
    pet::State state;
    state.species = pet::Species::Eevee;
    state.age_minutes = 10;
    return state;
}
}

int main() {
    using namespace pet;
    Game game;
    game.advance(9000, 60);
    check(game.state().species == Species::Egg, "not hatched before ten minutes");
    game.advance(1000, 60);
    check(game.state().species == Species::Eevee, "hatch at ten minutes");
    select(game, Action::Feed);
    check(game.state().fullness == 100, "feeding increases fullness");
    const auto full = encode(game.state());
    select(game, Action::Feed);
    check(full == encode(game.state()), "overfeeding rejected without rewards");
    select(game, Action::Sleep);
    check(game.state().sleeping, "sleep toggle");
    select(game, Action::Play);
    check(game.screen() == Screen::Home, "cannot play while asleep");
    game.advance(60000, 30);
    check(game.state().energy == 100 && !game.state().sleeping, "rest and automatic wake");

    Game a, b;
    a.restore(hatched()); b.restore(hatched());
    a.advance(60000, 60);
    for (int i = 0; i < 600; ++i) b.advance(100, 60);
    check(encode(a.state()) == encode(b.state()), "time partition invariant including remainders");
    const auto paused = encode(a.state());
    a.advance(60000, 0);
    check(paused == encode(a.state()), "pause leaves state unchanged");

    auto state = hatched();
    state.fullness = 0; state.energy = 0; state.hygiene = 0;
    game.restore(state);
    game.advance(60000, 30);
    check(game.state().sick, "sustained neglect causes illness");
    game.advance(60000, 1440);
    check(game.state().health == 0 && game.needs_attention(), "neglect causes recoverable exhaustion");
    select(game, Action::Feed);
    check(game.state().fullness == 0, "exhaustion requires medicine");
    select(game, Action::Medicine);
    select(game, Action::Clean);
    select(game, Action::Feed);
    check(game.state().health == 40 && !game.state().sick && game.state().hygiene == 100 &&
          game.state().fullness == 25, "complete recovery care flow");
    select(game, Action::Sleep);
    game.advance(60000, 10);
    check(game.state().energy > 0, "energy restored after rescue");

    game.restore(hatched());
    select(game, Action::Play);
    const auto game_start_age = game.state().age_minutes;
    for (int round = 0; round < 5; ++round) {
        while (game.mini().lane > game.mini().target) game.button(Button::Left);
        while (game.mini().lane < game.mini().target) game.button(Button::Right);
        game.advance(1000, 3600);
        game.button(Button::Confirm);
    }
    check(game.screen() == Screen::Result && game.mini().score == 5, "five catches complete game");
    check(game.state().experience == 15 && game.state().friendship == 30, "reward applied once");
    check(game.state().age_minutes == game_start_age, "care time frozen during minigame");
    const auto reward = game.state().experience;
    game.button(Button::Confirm);
    check(game.state().experience == reward, "closing result cannot duplicate reward");
    select(game, Action::Play);
    game.advance(9000);
    check(game.screen() == Screen::Result && game.mini().score == 0, "missed berries time out");
    game.restore(hatched()); select(game, Action::Play);
    game.button(Button::Confirm);
    check(game.mini().round == 1 && game.mini().score == 0, "early catch fails");

    state = hatched(); state.age_minutes = 1440; state.experience = 60; state.friendship = 70;
    state.minute_of_day = 360;
    game.restore(state); check(game.can_evolve(), "evolution ready at exact thresholds");
    select(game, Action::Evolve);
    check(game.state().species == Species::Espeon, "daytime evolution");
    state.minute_of_day = 1200; game.restore(state); select(game, Action::Evolve);
    check(game.state().species == Species::Umbreon, "nighttime evolution");
    state.friendship = 69; game.restore(state); select(game, Action::Evolve);
    check(game.state().species == Species::Eevee, "evolution threshold enforced");

    State decoded;
    auto save = encode(game.state());
    check(decode(save.data(), save.size(), decoded) && encode(decoded) == save, "save round trip");
    const auto unchanged = encode(decoded);
    for (std::size_t i = 0; i < save.size(); ++i) {
        auto corrupt = save; corrupt[i] ^= 0x80;
        check(!decode(corrupt.data(), corrupt.size(), decoded), "single byte corruption rejected");
        check(encode(decoded) == unchanged, "failed decode does not mutate output");
    }
    check(!decode(save.data(), 41, decoded), "truncated save rejected");
    check(!decode(nullptr, 42, decoded), "null save rejected");
    state = hatched(); state.fullness = 101;
    save = encode(state);
    check(!decode(save.data(), save.size(), decoded), "invalid state rejected even with correct CRC");
    const auto before = encode(game.state());
    check(!game.restore(state) && encode(game.state()) == before, "invalid restore is transactional");
    state = hatched(); state.rng = 0;
    check(!Game::valid(state), "invalid random state rejected");
    state = hatched(); state.minute_of_day = 1440;
    check(!Game::valid(state), "invalid clock rejected");

    // Long, deterministic adversarial sequence: invariants hold through care and time jumps.
    game.restore(hatched());
    std::uint32_t seed = 123456789;
    for (int i = 0; i < 20000; ++i) {
        seed = seed * 1664525u + 1013904223u;
        game.button(static_cast<Button>(seed % 3));
        game.advance(seed % 2000, (seed >> 16) % 61);
        check(Game::valid(game.state()), "state invariants under randomized interaction");
    }
    std::cout << "PASS: " << checks << " checks\n";
}
