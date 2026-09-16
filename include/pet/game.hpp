#pragma once
#include <cstdint>

namespace pet {
enum class Species : std::uint8_t { Egg, Eevee, Espeon, Umbreon, Psyduck };
enum class Screen : std::uint8_t { Home, Menu, Stats, Game, Result, Starter, Guide, Memory, Instructions };
enum class MiniPhase : std::uint8_t { Ready, Falling, Watch, Recall, Feedback };
enum class Button : std::uint8_t { Left, Confirm, Right };
enum class Action : std::uint8_t { Feed, Clean, Sleep, Medicine, Play, Stats, Evolve, Back, Think, Guide };

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
    Species starter = Species::Eevee;
    bool starter_chosen = false;
};

struct MiniGame {
    std::uint32_t elapsed_ms = 0;
    std::uint8_t lane = 1;
    std::uint8_t target = 1;
    std::uint8_t round = 0;
    std::uint8_t score = 0;
    std::uint8_t pattern[4]{};
    std::uint16_t input_ms = 0;
    std::uint8_t length = 2;
    std::uint8_t last_button = 3;
    MiniPhase phase = MiniPhase::Ready;
    bool success = false;
    std::uint8_t entered = 0;
    bool recalling = false;
    bool memory = false;
};
struct CareChange {
    std::int8_t fullness=0, happiness=0, energy=0, hygiene=0, health=0, friendship=0;
    std::uint8_t experience=0;
    std::uint16_t remaining_ms=0;
};

class Game {
public:
    static constexpr std::uint32_t max_age = 52560000; // 100 years; bounded saves.
    const State& state() const { return state_; }
    Screen screen() const { return screen_; }
    std::uint8_t selection() const { return selection_; }
    const MiniGame& mini() const { return mini_; }
    const CareChange& feedback() const { return feedback_; }
    static constexpr unsigned catch_open_ms=1200, berry_duration_ms=1800;
    static constexpr unsigned symbol_ms=900, symbol_on_ms=650;
    static constexpr std::uint8_t need_low[6]={25,30,25,25,40,0};
    unsigned mini_duration() const;
    int memory_cue() const;
    static const char* menu_section(std::uint8_t index);
    const char* message() const { return message_; }
    const char* care_hint() const;
    static constexpr std::uint8_t menu_count = 10;
    static constexpr std::uint8_t menu_rows = 5;
    static Action menu_action(std::uint8_t index);
    std::uint8_t menu_start() const;
    const char* action_hint(Action action) const;
    const char* blocked_reason(Action action) const;
    void advance(std::uint32_t real_ms, std::uint32_t speed = 1);
    void button(Button button);
    void back();
    bool restore(const State& state);
    bool can_evolve() const;
    bool needs_attention() const;
    static bool valid(const State& state);
private:
    State state_{};
    Screen screen_ = Screen::Starter;
    std::uint8_t selection_ = 0;
    MiniGame mini_{};
    CareChange feedback_{};
    const char* message_ = "Ein Ei wartet auf dich.";
    void minute();
    void act(Action action);
    void next_round(bool caught);
    void memory_pattern();
    void finish_memory(bool success);
    void begin_game();
    void finish_game();
    void step_minigame();
    void record_change(const State& before);
    std::uint32_t random();
};
const char* species_name(Species species);
const char* action_name(Action action);
} // namespace pet
