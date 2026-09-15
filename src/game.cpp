#include "pet/game.hpp"
#include "pet/catalog.hpp"
#include <algorithm>

namespace pet {
namespace {
void change(std::uint8_t& value, int delta) {
    value = static_cast<std::uint8_t>(std::clamp(static_cast<int>(value) + delta, 0, 100));
}
}

const char* species_name(Species species) {
    switch (species) {
    case Species::Egg: return "Ei";
    case Species::Eevee: return "Evoli";
    case Species::Espeon: return "Psiana";
    case Species::Umbreon: return "Nachtara";
    case Species::Psyduck: return "Enton";
    }
    return roster_name(species);
}

const char* action_name(Action action) {
    switch (action) {
    case Action::Feed: return "Fuettern";
    case Action::Clean: return "Saubermachen";
    case Action::Sleep: return "Schlafen / Wecken";
    case Action::Medicine: return "Medizin";
    case Action::Play: return "Beeren fangen";
    case Action::Stats: return "Status";
    case Action::Evolve: return "Entwickeln";
    case Action::Back: return "Zurueck";
    case Action::Think: return "Entons Denkpause";
    case Action::Guide: return "Pflegehilfe";
    }
    return "Unbekannt";
}

bool Game::valid(const State& s) {
    return s.age_minutes <= max_age && s.remainder_ms < 60000 && s.rng != 0 &&
        s.experience <= 1000000 && s.minute_of_day < 1440 && s.neglect_minutes <= 120 &&
        s.fullness <= 100 && s.happiness <= 100 && s.energy <= 100 && s.hygiene <= 100 &&
        s.health <= 100 && s.friendship <= 100 && s.waste <= 4 &&
        species_valid(s.species) && starter_valid(s.starter) &&
        (s.starter_chosen || (s.species == Species::Egg && s.age_minutes == 0 && s.remainder_ms == 0)) &&
        (s.species == Species::Egg || s.species==s.starter ||
            (s.starter==Species::Eevee && (s.species==Species::Espeon || s.species==Species::Umbreon))) &&
        (s.species != Species::Egg || (s.age_minutes < 10 && !s.sleeping && !s.sick)) &&
        (s.species == Species::Egg || s.age_minutes >= 10);
}

bool Game::restore(const State& state) {
    if (!valid(state)) return false;
    state_ = state;
    screen_ = state_.starter_chosen ? Screen::Home : Screen::Starter;
    selection_ = 0;
    mini_ = {};
    message_ = "Willkommen zurueck.";
    return true;
}

Action Game::menu_action(std::uint8_t index) {
    static constexpr Action entries[] = {Action::Feed, Action::Clean, Action::Sleep, Action::Medicine,
        Action::Play, Action::Think, Action::Stats, Action::Evolve, Action::Guide, Action::Back};
    return index < menu_count ? entries[index] : Action::Back;
}

std::uint8_t Game::menu_start() const {
    return selection_ < menu_rows ? 0 : static_cast<std::uint8_t>(selection_ - menu_rows + 1);
}

const char* Game::care_hint() const {
    if (!state_.starter_chosen) return "Waehle deinen ersten Begleiter.";
    if (state_.species == Species::Egg) return "Dein Ei braucht zehn Minuten.";
    if (state_.sick || state_.health < 40) return "Medizin, dann weiter pflegen.";
    if (state_.waste > 0 || state_.hygiene < 25) return "Bitte saubermachen.";
    if (state_.sleeping) return "Schlafen fuellt Energie auf.";
    if (state_.fullness < 25) return "Zeit fuer eine Beere.";
    if (state_.energy < 25) return "Muede. Schlafen lassen.";
    if (state_.happiness < 30) return "Ein kleines Spiel tut gut.";
    if (can_evolve()) return "Bereit fuer die Entwicklung!";
    return "Alles gut. Zeit zusammen!";
}

const char* Game::blocked_reason(Action action) const {
    if (action == Action::Back || action == Action::Stats || action == Action::Guide) return nullptr;
    if (state_.species == Species::Egg) return "Zuerst muss dein Ei schluepfen.";
    if (action == Action::Medicine) return !state_.sick && state_.health >= 40 ? "Keine Medizin noetig." : nullptr;
    if (action == Action::Clean) return state_.waste == 0 && state_.hygiene == 100 ? "Alles sauber." : nullptr;
    if (state_.health == 0) return "Zuerst Medizin geben.";
    if (action == Action::Sleep) return nullptr;
    if (state_.sleeping) return "Bitte zuerst wecken.";
    if (action == Action::Feed && state_.fullness > 85) return "Noch satt. Spaeter wieder.";
    if ((action == Action::Play || action == Action::Think) &&
        (state_.energy < 15 || state_.fullness < 15 || state_.sick)) return "Erst essen, pflegen, ruhen.";
    if (action == Action::Evolve) {
        if (state_.species != Species::Eevee) return "Fuer diesen Begleiter spaeter.";
        if (!can_evolve()) return "1 Tag, 70 Bindung, 60 EP.";
    }
    return nullptr;
}

const char* Game::action_hint(Action action) const {
    if (const auto* reason = blocked_reason(action)) return reason;
    switch (action) {
    case Action::Feed: return "Beere: +25 satt, +3 froh.";
    case Action::Clean: return "Sauberkeit voll. Abfall weg.";
    case Action::Sleep: return state_.sleeping ? "Sanft wecken." : "Schlaf: +1 Energie / 2 Min.";
    case Action::Medicine: return "Kuriert. Mind. 40 Gesundheit.";
    case Action::Play: return "Fangen: Bindung und Erfahrung.";
    case Action::Think: return "Drei Zeichen merken. Enton?!";
    case Action::Stats: return "Alle Beduerfnisse ansehen.";
    case Action::Evolve: return "Dein Evoli ist bereit!";
    case Action::Guide: return care_hint();
    case Action::Back: return "Zurueck zu deinem Begleiter.";
    }
    return "";
}

bool Game::can_evolve() const {
    return state_.species == Species::Eevee && state_.age_minutes >= 1440 &&
        state_.friendship >= 70 && state_.experience >= 60 && state_.health >= 60 &&
        !state_.sick && !state_.sleeping;
}

bool Game::needs_attention() const {
    return state_.species != Species::Egg && (state_.fullness < 25 || state_.energy < 25 ||
        state_.happiness < 30 || state_.hygiene < 25 || state_.waste > 0 || state_.sick || state_.health < 40);
}

void Game::minute() {
    if (state_.age_minutes < max_age) ++state_.age_minutes;
    state_.minute_of_day = static_cast<std::uint16_t>((state_.minute_of_day + 1) % 1440);
    if (state_.species == Species::Egg) {
        if (state_.age_minutes >= 10) {
            state_.species = state_.starter;
            message_ = state_.species == Species::Psyduck ? "Enton ist geschluepft!" : state_.species==Species::Eevee ? "Evoli ist geschluepft!" : "Dein Begleiter ist geschluepft!";
        }
        return;
    }
    const auto age = state_.age_minutes;
    if (age % (state_.sleeping ? 12 : 6) == 0) change(state_.fullness, -1);
    if (age % 12 == 0) change(state_.happiness, state_.sleeping ? 0 : -1);
    if (age % 10 == 0) change(state_.hygiene, state_.waste > 0 ? -3 : -1);
    if (state_.sleeping) {
        if (age % 2 == 0) change(state_.energy, 1);
        if (state_.energy == 100) {
            state_.sleeping = false;
            message_ = "Ausgeschlafen!";
        }
    } else if (age % 6 == 0) change(state_.energy, -1);
    if (age % 180 == 0 && state_.waste < 4) ++state_.waste;
    const bool neglected = state_.fullness == 0 || state_.hygiene < 20 || state_.energy == 0;
    state_.neglect_minutes = neglected
        ? static_cast<std::uint16_t>(std::min(120, state_.neglect_minutes + 1)) : 0;
    if (state_.neglect_minutes >= 30) state_.sick = true;
    if (age % 10 == 0) {
        if (state_.sick || neglected) change(state_.health, -2);
        else if (state_.fullness >= 40 && state_.hygiene >= 40) change(state_.health, 1);
    }
    if (neglected && age % 60 == 0) change(state_.friendship, -1);
    if (state_.health == 0) {
        state_.sleeping = false;
        message_ = "Erschoepft. Medizin hilft.";
        if (screen_ == Screen::Game) screen_ = Screen::Home;
    }
}

void Game::advance(std::uint32_t real_ms, std::uint32_t speed) {
    // Keep calls bounded on small MCUs; callers split larger intervals.
    real_ms = std::min(real_ms, 60000u);
    speed = std::min(speed, 3600u);
    if (speed == 0) return;
    if (!state_.starter_chosen) return;
    if (screen_ == Screen::Memory) {
        while (real_ms > 0 && screen_ == Screen::Memory) {
            const auto deadline = mini_.recalling ? 10000u : 2400u;
            const auto step = std::min(real_ms, deadline - mini_.elapsed_ms);
            mini_.elapsed_ms += step;
            real_ms -= step;
            if (mini_.elapsed_ms == deadline) {
                if (mini_.recalling) finish_memory(false);
                else {
                    mini_.recalling = true;
                    mini_.elapsed_ms = 0;
                    message_ = "Jetzt du: drei Tasten.";
                }
            }
        }
        return;
    }
    // Care time is frozen during a short skill game, even in accelerated mode.
    if (screen_ == Screen::Game) {
        std::uint32_t remaining = real_ms;
        while (screen_ == Screen::Game && remaining > 0) {
            const auto step = std::min(remaining, 1800u - mini_.elapsed_ms);
            mini_.elapsed_ms += step;
            remaining -= step;
            if (mini_.elapsed_ms == 1800) next_round(false);
        }
        return;
    }
    const std::uint64_t total = state_.remainder_ms + static_cast<std::uint64_t>(real_ms) * speed;
    const auto minutes = total / 60000;
    state_.remainder_ms = static_cast<std::uint32_t>(total % 60000);
    for (std::uint64_t i = 0; i < minutes; ++i) minute();
}

std::uint32_t Game::random() {
    auto& x = state_.rng;
    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;
    return x;
}

void Game::next_round(bool caught) {
    if (caught) ++mini_.score;
    ++mini_.round;
    mini_.elapsed_ms = 0;
    if (mini_.round == 5) {
        change(state_.happiness, mini_.score * 4);
        change(state_.friendship, mini_.score * 2);
        state_.experience = std::min(1000000u, state_.experience + mini_.score * 3u);
        screen_ = Screen::Result;
        message_ = mini_.score >= 3 ? "Gut gefangen!" : "Naechstes Mal klappt es!";
    } else mini_.target = static_cast<std::uint8_t>(random() % 3);
}

void Game::act(Action action) {
    if (const auto* reason = blocked_reason(action)) { message_ = reason; return; }
    screen_ = Screen::Home;
    if (action == Action::Back) return;
    if (action == Action::Stats) { screen_ = Screen::Stats; return; }
    if (action == Action::Guide) { screen_ = Screen::Guide; return; }
    if (action == Action::Medicine) {
        state_.sick = false;
        state_.neglect_minutes = 0;
        state_.health = std::max<std::uint8_t>(40, state_.health);
        message_ = "Versorgt. Jetzt gut pflegen.";
        return;
    }
    if (action == Action::Clean) {
        state_.hygiene = 100;
        state_.waste = 0;
        message_ = "Wieder sauber!";
        return;
    }
    if (action == Action::Sleep) {
        state_.sleeping = !state_.sleeping;
        message_ = state_.sleeping ? "Gute Nacht." : "Guten Morgen.";
        return;
    }
    switch (action) {
    case Action::Feed:
        change(state_.fullness, 25);
        change(state_.happiness, 3);
        message_ = "Die Beere schmeckt!";
        break;
    case Action::Play:
    case Action::Think:
        change(state_.energy, -8);
        change(state_.fullness, -5);
        mini_ = {};
        if (action == Action::Think) {
            mini_.memory = true;
            screen_ = Screen::Memory;
            memory_pattern();
        } else {
            mini_.target = static_cast<std::uint8_t>(random() % 3);
            screen_ = Screen::Game;
            message_ = "Unter die Beere. OK: fangen.";
        }
        break;
    case Action::Evolve:
        if (can_evolve()) {
            const bool day = state_.minute_of_day >= 360 && state_.minute_of_day < 1200;
            state_.species = day ? Species::Espeon : Species::Umbreon;
            message_ = "Eine neue Entwicklung!";
        } else message_ = "1 Tag, 70 Bindung, 60 EP.";
        break;
    default: break;
    }
}

void Game::button(Button button) {
    if (screen_ == Screen::Starter) {
        if (button == Button::Confirm) {
            state_.starter_chosen = true;
            screen_ = Screen::Home;
            message_ = "Ein kleines Abenteuer beginnt.";
        } else state_.starter = next_starter(state_.starter,button==Button::Right);
        return;
    }
    if (screen_ == Screen::Memory) {
        if (!mini_.recalling) return;
        if (static_cast<std::uint8_t>(button) != mini_.pattern[mini_.entered]) { finish_memory(false); return; }
        ++mini_.entered;
        if (mini_.entered == 3) {
            ++mini_.round;
            if (mini_.round == 3) finish_memory(true);
            else memory_pattern();
        }
        return;
    }
    if (screen_ == Screen::Game) {
        if (button == Button::Left && mini_.lane > 0) --mini_.lane;
        if (button == Button::Right && mini_.lane < 2) ++mini_.lane;
        if (button == Button::Confirm) {
            next_round(mini_.lane == mini_.target && mini_.elapsed_ms >= 900 && mini_.elapsed_ms < 1800);
        }
        return;
    }
    if (screen_ == Screen::Guide) { screen_ = Screen::Menu; return; }
    if (screen_ == Screen::Stats || screen_ == Screen::Result) { screen_ = Screen::Home; return; }
    if (screen_ == Screen::Home) {
        if (button == Button::Confirm) screen_ = Screen::Menu;
        else screen_ = Screen::Stats;
        return;
    }
    if (button == Button::Left) selection_ = static_cast<std::uint8_t>((selection_ + menu_count - 1) % menu_count);
    if (button == Button::Right) selection_ = static_cast<std::uint8_t>((selection_ + 1) % menu_count);
    if (button == Button::Confirm) act(menu_action(selection_));
}

void Game::back() {
    if (screen_ == Screen::Starter || screen_ == Screen::Home) return;
    if (screen_ == Screen::Game || screen_ == Screen::Memory) message_ = "Spiel beendet. Keine Belohnung.";
    screen_ = screen_ == Screen::Guide ? Screen::Menu : Screen::Home;
}

void Game::memory_pattern() {
    mini_.elapsed_ms = 0;
    mini_.entered = 0;
    mini_.recalling = false;
    for (auto& symbol : mini_.pattern) symbol = static_cast<std::uint8_t>(random() % 3);
    message_ = "Enton denkt nach. Merke dir das!";
}

void Game::finish_memory(bool success) {
    mini_.score = success ? 3 : 0;
    if (success) {
        change(state_.happiness, 12); change(state_.friendship, 6);
        state_.experience = std::min(1000000u, state_.experience + 9u);
    }
    message_ = success ? "Enton: Hab ich auch gewusst!" : "Enton: Aeh... was war nochmal?";
    screen_ = Screen::Result;
}
} // namespace pet
