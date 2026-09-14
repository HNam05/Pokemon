#pragma once
#include <cstdint>

namespace pet {
enum class Species : std::uint8_t { Egg, Eevee, Espeon, Umbreon };
enum class Screen : std::uint8_t { Home, Menu, Stats, Game, Result };
enum class Button : std::uint8_t { Left, Confirm, Right };
enum class Action : std::uint8_t { Feed, Clean, Sleep, Medicine, Play, Stats, Evolve, Back };

struct State {
    std::uint32_t age_minutes = 0;
    std::uint32_t remainder_ms = 0;
    std::uint32_t rng = 0x50455431u;
    std::uint32_t experience = 0;
    std::uint16_t minute_of_day = 8 * 60;
    std::uint16_t neglect_minutes = 0;
    std::uint8_t fullness = 75;
    std::uint8_t happiness = 70;
    std::uint8_t energy = 85;
    std::uint8_t hygiene = 90;
    std::uint8_t health = 100;
    std::uint8_t friendship = 20;
    std::uint8_t waste = 0;
    Species species = Species::Egg;
    bool sleeping = false;
    bool sick = false;
};

struct MiniGame {
    std::uint32_t elapsed_ms = 0;
    std::uint8_t lane = 1;
    std::uint8_t target = 1;
    std::uint8_t round = 0;
    std::uint8_t score = 0;
};

class Game {
public:
    static constexpr std::uint32_t max_age = 52560000; // 100 years; bounded saves.
    const State& state() const { return state_; }
    Screen screen() const { return screen_; }
    std::uint8_t selection() const { return selection_; }
    const MiniGame& mini() const { return mini_; }
    const char* message() const { return message_; }
    void advance(std::uint32_t real_ms, std::uint32_t speed = 1);
    void button(Button button);
    bool restore(const State& state);
    bool can_evolve() const;
    bool needs_attention() const;
    static bool valid(const State& state);
private:
    State state_{};
    Screen screen_ = Screen::Home;
    std::uint8_t selection_ = 0;
    MiniGame mini_{};
    const char* message_ = "Ein Ei wartet auf dich.";
    void minute();
    void act(Action action);
    void next_round(bool caught);
    std::uint32_t random();
};
const char* species_name(Species species);
const char* action_name(Action action);
} // namespace pet
