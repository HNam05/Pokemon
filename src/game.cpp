#include "pet/game.hpp"
#include "pet/catalog.hpp"
#include <algorithm>

namespace pet {
namespace {
void change(std::uint8_t& value, int delta) {
    value = static_cast<std::uint8_t>(std::clamp(static_cast<int>(value) + delta, 0, 100));
}
constexpr std::uint8_t mistake_today = 1;

// Own evolution rules. Only lines whose every form has audited art are listed;
// IDs are stable catalog IDs from assets/roster.json.
enum class Rule : std::uint8_t { Fixed, DayNight, Dusk, Random };
struct Evolution { std::uint8_t from, first, last; Rule rule; std::uint8_t friendship; };
constexpr Evolution evolutions[] = {
    {1, 2, 3, Rule::DayNight, 70},    // Evoli -> Psiana (Tag) / Nachtara (Nacht)
    {48, 43, 43, Rule::Fixed, 70},    // Pichu -> Pikachu
    {18, 76, 76, Rule::Fixed, 70},    // Lilminip -> Dressella
    {28, 90, 90, Rule::Fixed, 70},    // Fynx -> Rutena
    {32, 92, 92, Rule::Fixed, 70},    // Psiau -> Psiaugon
    {36, 98, 99, Rule::Dusk, 70},     // Wuffels -> Wolwerock / Abendform 17-20 Uhr
    {100, 101, 118, Rule::Random, 90} // Typ:Null -> Amigento in einer zufaelligen Typform
};
const Evolution* evolution_rule(Species species) {
    for (const auto& rule : evolutions) if (rule.from == static_cast<std::uint8_t>(species)) return &rule;
    return nullptr;
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
    case Action::Feed: return "Füttern";
    case Action::Clean: return "Saubermachen";
    case Action::Sleep: return "Schlafen / Wecken";
    case Action::Medicine: return "Medizin";
    case Action::Play: return "Beeren fangen";
    case Action::Stats: return "Status";
    case Action::Evolve: return "Entwickeln";
    case Action::Back: return "Zurück";
    case Action::Think: return "Entons Denkpause";
    case Action::Guide: return "Pflegehilfe";
    case Action::Pet: return "Streicheln";
    case Action::Clock: return "Uhr stellen";
    }
    return "Unbekannt";
}

const char* stage_name(Stage stage) {
    switch (stage) {
    case Stage::Egg: return "Ei";
    case Stage::Baby: return "Baby";
    case Stage::Child: return "Kind";
    case Stage::Adult: return "Erwachsen";
    }
    return "";
}

Stage Game::stage_of(const State& s) {
    if (s.species == Species::Egg) return Stage::Egg;
    if (s.species != s.starter || s.age_minutes >= 4320) return Stage::Adult;
    return s.age_minutes < 1440 ? Stage::Baby : Stage::Child;
}

unsigned Game::level_of(std::uint32_t experience) {
    // Level 1 + sqrt(2 * EP), capped at 100: early levels come quickly, later ones slower.
    const std::uint32_t target = std::min<std::uint32_t>(experience, 10000u) * 2u;
    unsigned root = 0;
    while ((root + 1) * (root + 1) <= target) ++root;
    return std::min(100u, 1u + root);
}

Species Game::evolution_of(Species species) {
    const auto* rule = evolution_rule(species);
    return rule ? static_cast<Species>(rule->first) : Species::Egg;
}

bool Game::evolves_into(Species from, Species to) {
    const auto* rule = evolution_rule(from);
    const auto id = static_cast<std::uint8_t>(to);
    return rule && id >= rule->first && id <= rule->last;
}

bool Game::valid(const State& s) {
    const bool egg = s.species == Species::Egg;
    return s.age_minutes <= max_age && s.remainder_ms < 60000 && s.rng != 0 &&
        s.experience <= 1000000 && s.minute_of_day < 1440 && s.neglect_minutes <= 120 &&
        s.fullness <= 100 && s.happiness <= 100 && s.energy <= 100 && s.hygiene <= 100 &&
        s.health <= 100 && s.friendship <= 100 && s.waste <= 4 &&
        s.care_mistakes <= max_mistakes && s.call_minutes <= call_limit + call_repeat &&
        s.pet_cooldown <= pet_cooldown_minutes && s.flags <= mistake_today &&
        species_valid(s.species) && starter_valid(s.starter) &&
        (s.starter_chosen || (egg && s.age_minutes == 0 && s.remainder_ms == 0)) &&
        (egg || s.species == s.starter || evolves_into(s.starter, s.species)) &&
        (!egg || (s.age_minutes < 10 && !s.sleeping && !s.sick && s.care_mistakes == 0 &&
            s.call_minutes == 0 && s.pet_cooldown == 0 && s.flags == 0)) &&
        (egg || s.age_minutes >= 10);
}

bool Game::restore(const State& state) {
    if (!valid(state)) return false;
    state_ = state;
    screen_ = state_.starter_chosen ? Screen::Home : Screen::Starter;
    selection_ = 0;
    clock_field_ = 0;
    evolved_from_ = Species::Egg;
    event_ = Event::None;
    mini_ = {};
    feedback_ = {};
    message_ = "Willkommen zurück.";
    return true;
}

Action Game::menu_action(std::uint8_t index) {
    static constexpr Action entries[] = {Action::Feed, Action::Pet, Action::Clean, Action::Sleep, Action::Medicine,
        Action::Play, Action::Think, Action::Stats, Action::Evolve, Action::Guide, Action::Clock, Action::Back};
    static_assert(sizeof(entries) / sizeof(entries[0]) == menu_count, "menu table matches menu_count");
    return index < menu_count ? entries[index] : Action::Back;
}

std::uint8_t Game::menu_start() const {
    return selection_ < menu_rows ? 0 : static_cast<std::uint8_t>(selection_ - menu_rows + 1);
}

const char* Game::menu_section(std::uint8_t index) {
    return index<5?"PFLEGE":index<7?"SPIELZEIT":index<10?"MEIN BEGLEITER":index<11?"GERÄT":"ZURÜCK";
}

const char* Game::care_hint() const {
    if (!state_.starter_chosen) return "Wähle deinen ersten Begleiter.";
    if (state_.species == Species::Egg) return "Dein Ei braucht zehn Minuten.";
    if (state_.sick || state_.health < need_low[4]) return "Medizin, dann weiter pflegen.";
    if (state_.waste > 0 || state_.hygiene < need_low[3]) return "Bitte saubermachen.";
    if (state_.sleeping) return night() ? "Schläft bis zum Morgen." : "Schlafen füllt Energie auf.";
    if (state_.fullness < need_low[0]) return "Zeit für eine Beere.";
    if (night()) return "Schon spät. Schlafen lassen.";
    if (state_.energy < need_low[2]) return "Müde. Schlafen lassen.";
    if (state_.happiness < need_low[1]) return "Ein kleines Spiel tut gut.";
    if (state_.minute_of_day >= 19 * 60 && state_.fullness < 50) return "Vor der Nacht noch füttern.";
    if (can_evolve()) return "Bereit für die Entwicklung!";
    if (state_.pet_cooldown == 0) return "Streicheln stärkt die Bindung.";
    return "Alles gut. Zeit zusammen!";
}

const char* Game::blocked_reason(Action action) const {
    if (action == Action::Back || action == Action::Stats || action == Action::Guide || action == Action::Clock) return nullptr;
    if (state_.species == Species::Egg) return "Zuerst muss dein Ei schlüpfen.";
    if (action == Action::Medicine) return !state_.sick && state_.health >= 40 ? "Keine Medizin nötig." : nullptr;
    if (action == Action::Clean) return state_.waste == 0 && state_.hygiene == 100 ? "Alles sauber." : nullptr;
    if (state_.health == 0) return "Zuerst Medizin geben.";
    if (action == Action::Sleep) return nullptr;
    if (state_.sleeping) return action == Action::Pet ? "Schläft gerade. Psst!" : "Bitte zuerst wecken.";
    if (action == Action::Pet && state_.pet_cooldown > 0) return "Genug geschmust. Später wieder.";
    if (action == Action::Feed && state_.fullness > 85) return "Noch satt. Später wieder.";
    if ((action == Action::Play || action == Action::Think) &&
        (state_.energy < 15 || state_.fullness < 15 || state_.sick)) return "Erst essen, pflegen, ruhen.";
    if (action == Action::Evolve) {
        if (!evolution_rule(state_.species)) return "Entwickelt sich nicht weiter.";
        if (!can_evolve()) return "Noch nicht bereit. Siehe Status.";
    }
    return nullptr;
}

const char* Game::action_hint(Action action) const {
    if (const auto* reason = blocked_reason(action)) return reason;
    switch (action) {
    case Action::Feed: return "Beere: +25 satt, +3 froh.";
    case Action::Pet: return "Streicheln: +6 froh, +1 Bindung.";
    case Action::Clean: return "Sauberkeit voll. Abfall weg.";
    case Action::Sleep: return state_.sleeping ? (night() ? "Nachts wecken macht mürrisch." : "Sanft wecken.")
        : "Schlaf: +1 Energie / 2 Min.";
    case Action::Medicine: return "Kuriert. Mind. 40 Gesundheit.";
    case Action::Play: return "Spielstart: -5 satt, -8 Energie.";
    case Action::Think: return "2, 3, 4 Zeichen. Folge merken.";
    case Action::Stats: return "Werte, Level und Entwicklung.";
    case Action::Evolve: return "Bereit für die Entwicklung!";
    case Action::Guide: return care_hint();
    case Action::Clock: return "Uhrzeit für Tag und Nacht.";
    case Action::Back: return "Zurück zu deinem Begleiter.";
    }
    return "";
}

bool Game::can_evolve() const {
    const auto* rule = evolution_rule(state_.species);
    return rule && state_.age_minutes >= 1440 && state_.friendship >= rule->friendship &&
        state_.experience >= 60 && state_.health >= 60 && state_.care_mistakes <= 3 &&
        !state_.sick && !state_.sleeping;
}

bool Game::needs_attention() const {
    return state_.species != Species::Egg && (calling() || state_.fullness < need_low[0] || state_.energy < need_low[2] ||
        state_.happiness < need_low[1] || state_.hygiene < need_low[3] || state_.waste > 0 || state_.sick || state_.health < need_low[4]);
}

bool Game::wants_call() const {
    if (!state_.starter_chosen || state_.species == Species::Egg) return false;
    if (state_.sick || state_.health < need_low[4]) return true;
    if (state_.sleeping) return false;
    return state_.fullness < need_low[0] || state_.happiness < need_low[1] ||
        state_.energy < need_low[2] || night();
}

void Game::update_call(bool minute_passed) {
    if (!wants_call()) {
        // Answering in time strengthens the bond; calls that resolve by themselves do not.
        if (!minute_passed && state_.call_minutes > 0 && state_.call_minutes < call_limit) change(state_.friendship, 1);
        state_.call_minutes = 0;
        return;
    }
    if (!minute_passed) return;
    ++state_.call_minutes;
    if (state_.call_minutes == call_limit || state_.call_minutes == call_limit + call_repeat) {
        state_.care_mistakes = static_cast<std::uint8_t>(std::min<int>(max_mistakes, state_.care_mistakes + 1));
        state_.flags |= mistake_today;
        change(state_.friendship, -2);
        state_.call_minutes = call_limit;
        event_ = Event::Mistake;
        message_ = "Hat vergeblich gerufen.";
    }
}

void Game::minute() {
    if (state_.age_minutes < max_age) ++state_.age_minutes;
    state_.minute_of_day = static_cast<std::uint16_t>((state_.minute_of_day + 1) % 1440);
    if (state_.species == Species::Egg) {
        if (state_.age_minutes >= 10) {
            state_.species = state_.starter;
            event_ = Event::Hatched;
            message_ = "Dein Begleiter ist geschlüpft!";
        }
        return;
    }
    const auto age = state_.age_minutes;
    if (state_.species == state_.starter && (age == 1440 || age == 4320)) {
        event_ = Event::Grew;
        message_ = age == 1440 ? "Aus dem Baby wird ein Kind!" : "Jetzt ganz erwachsen!";
    }
    if (age % (state_.sleeping ? 20 : 6) == 0) change(state_.fullness, -1);
    if (age % 12 == 0) change(state_.happiness, state_.sleeping ? 0 : -1);
    if (age % 10 == 0) change(state_.hygiene, state_.waste > 0 ? -3 : -1);
    if (state_.sleeping) {
        if (age % 2 == 0) change(state_.energy, 1);
        if (state_.energy == 100 && !night()) {
            state_.sleeping = false;
            message_ = "Ausgeschlafen!";
        }
    } else if (age % 9 == 0) change(state_.energy, -1);
    if (age % 180 == 0 && state_.waste < 4) ++state_.waste;
    if (state_.pet_cooldown > 0) --state_.pet_cooldown;
    if (state_.minute_of_day == wake_time) {
        if (state_.sleeping) { state_.sleeping = false; message_ = "Guten Morgen!"; }
        // A day without ignored calls forgives one older mistake.
        if (!(state_.flags & mistake_today) && state_.care_mistakes > 0) --state_.care_mistakes;
        state_.flags = 0;
    }
    if (!state_.sleeping && state_.health > 0 &&
        (state_.minute_of_day == bedtime || state_.energy == 0)) {
        state_.sleeping = true;
        message_ = state_.energy == 0 ? "Vor Müdigkeit eingeschlafen." : "Müde. Gute Nacht!";
    }
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
        message_ = "Erschöpft. Medizin hilft.";
    }
    update_call(true);
}

void Game::advance(std::uint32_t real_ms, std::uint32_t speed) {
    // Keep calls bounded on small MCUs; callers split larger intervals.
    real_ms = std::min(real_ms, 60000u);
    speed = std::min(speed, 3600u);
    if (speed == 0) return;
    if (!state_.starter_chosen) return;
    if (screen_ != Screen::Result)
        feedback_.remaining_ms=static_cast<std::uint16_t>(real_ms>=feedback_.remaining_ms?0:feedback_.remaining_ms-real_ms);
    if (screen_ == Screen::Instructions) return;
    // Every game phase runs in real time; care never consumes the remaining tick.
    if (screen_ == Screen::Game || screen_ == Screen::Memory) {
        while(real_ms>0 && (screen_==Screen::Game || screen_==Screen::Memory)) {
            const auto step=std::min(real_ms,mini_duration()-mini_.elapsed_ms);
            mini_.elapsed_ms+=step;real_ms-=step;
            mini_.input_ms=static_cast<std::uint16_t>(step>=mini_.input_ms?0:mini_.input_ms-step);
            if(mini_.elapsed_ms==mini_duration()) step_minigame();
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

void Game::record_change(const State& before) {
    feedback_={};
    feedback_.fullness=static_cast<std::int8_t>(state_.fullness-before.fullness);
    feedback_.happiness=static_cast<std::int8_t>(state_.happiness-before.happiness);
    feedback_.energy=static_cast<std::int8_t>(state_.energy-before.energy);
    feedback_.hygiene=static_cast<std::int8_t>(state_.hygiene-before.hygiene);
    feedback_.health=static_cast<std::int8_t>(state_.health-before.health);
    feedback_.friendship=static_cast<std::int8_t>(state_.friendship-before.friendship);
    feedback_.experience=static_cast<std::uint8_t>(state_.experience-before.experience);
    if(feedback_.fullness || feedback_.happiness || feedback_.energy || feedback_.hygiene ||
        feedback_.health || feedback_.friendship || feedback_.experience) feedback_.remaining_ms=4000;
}

unsigned Game::mini_duration() const {
    switch(mini_.phase) {
    case MiniPhase::Ready:return 900;
    case MiniPhase::Falling:return berry_duration_ms;
    case MiniPhase::Watch:return mini_.length*symbol_ms;
    case MiniPhase::Recall:return 6000+mini_.length*2000;
    case MiniPhase::Feedback:return mini_.memory?900:450;
    }
    return 900;
}
int Game::memory_cue() const {
    if(mini_.phase!=MiniPhase::Watch || mini_.elapsed_ms%symbol_ms>=symbol_on_ms) return -1;
    const auto index=mini_.elapsed_ms/symbol_ms;
    return index<mini_.length?mini_.pattern[index]:-1;
}
void Game::begin_game() {
    const auto before=state_;
    change(state_.energy,-8);change(state_.fullness,-5);
    record_change(before);
    screen_=mini_.memory?Screen::Memory:Screen::Game;
    mini_.phase=MiniPhase::Ready;mini_.elapsed_ms=0;
    if(mini_.memory) {
        for(auto& symbol:mini_.pattern) symbol=static_cast<std::uint8_t>(random()%3);
    } else mini_.target=static_cast<std::uint8_t>(random()%3);
    message_="Bereit? Gleich geht es los.";
}
void Game::next_round(bool caught) {
    mini_.success=caught;
    if(caught) ++mini_.score;
    ++mini_.round;
    mini_.elapsed_ms=0;mini_.phase=MiniPhase::Feedback;
}
void Game::finish_game() {
    const auto before=state_;
    change(state_.happiness,mini_.score*4);
    change(state_.friendship,mini_.score*2);
    state_.experience=std::min(1000000u,state_.experience+mini_.score*3u);
    update_call(false);
    record_change(before);
    screen_=Screen::Result;
    message_=mini_.memory ? (mini_.score==3?"Enton: Hab ich auch gewusst!":"Enton: Üben wir nochmal?")
        : mini_.score>=3?"Gut gefangen!":"Nächstes Mal klappt es!";
}
void Game::step_minigame() {
    mini_.elapsed_ms=0;
    switch(mini_.phase) {
    case MiniPhase::Ready:
        if(mini_.memory) memory_pattern();
        else {mini_.phase=MiniPhase::Falling;message_="Im Fangfeld OK drücken.";}
        break;
    case MiniPhase::Watch:
        mini_.phase=MiniPhase::Recall;mini_.recalling=true;message_="Jetzt du. Gleiche Reihenfolge.";
        break;
    case MiniPhase::Recall:message_="Zeit vorbei.";finish_memory(false);break;
    case MiniPhase::Falling:message_="Beere verpasst.";next_round(false);break;
    case MiniPhase::Feedback:
        if(mini_.memory) {
            if(!mini_.success || mini_.round==3) finish_game();
            else memory_pattern();
        } else if(mini_.round==5) finish_game();
        else {mini_.target=static_cast<std::uint8_t>(random()%3);mini_.phase=MiniPhase::Falling;message_="Nächste Beere!";}
        break;
    }
}

void Game::evolve() {
    const auto* rule = evolution_rule(state_.species);
    const auto hour = state_.minute_of_day / 60;
    auto target = rule->first;
    if (rule->rule == Rule::DayNight && !(hour >= 6 && hour < 20)) target = rule->last;
    if (rule->rule == Rule::Dusk && hour >= 17 && hour < 20) target = rule->last;
    if (rule->rule == Rule::Random) target = static_cast<std::uint8_t>(rule->first + random() % (rule->last - rule->first + 1));
    evolved_from_ = state_.species;
    state_.species = static_cast<Species>(target);
    screen_ = Screen::Evolved;
    event_ = Event::Evolved;
    message_ = "Eine neue Entwicklung!";
}

void Game::act(Action action) {
    feedback_={};
    const auto before=state_;
    if (const auto* reason = blocked_reason(action)) { message_ = reason; return; }
    screen_ = Screen::Home;
    switch (action) {
    case Action::Back: return;
    case Action::Stats: screen_ = Screen::Stats; return;
    case Action::Guide: screen_ = Screen::Guide; return;
    case Action::Clock:
        screen_ = Screen::Clock; clock_edit_ = state_.minute_of_day; clock_field_ = 0;
        message_ = "Stunde, dann Minute stellen.";
        return;
    case Action::Medicine:
        state_.sick = false;
        state_.neglect_minutes = 0;
        state_.health = std::max<std::uint8_t>(40, state_.health);
        message_ = "Versorgt. Jetzt gut pflegen.";
        break;
    case Action::Clean:
        state_.hygiene = 100;
        state_.waste = 0;
        message_ = "Wieder sauber!";
        break;
    case Action::Sleep:
        state_.sleeping = !state_.sleeping;
        if (!state_.sleeping && night()) { change(state_.happiness, -5); message_ = "Gähn ... es ist doch Nacht."; }
        else message_ = state_.sleeping ? "Gute Nacht." : "Guten Morgen.";
        break;
    case Action::Feed:
        change(state_.fullness, 25);
        change(state_.happiness, 3);
        event_ = Event::Fed;
        message_ = "Die Beere schmeckt!";
        break;
    case Action::Pet:
        change(state_.happiness, 6);
        change(state_.friendship, 1);
        state_.pet_cooldown = pet_cooldown_minutes;
        event_ = Event::Petted;
        message_ = "Das tut gut!";
        break;
    case Action::Play:
    case Action::Think:
        mini_={};mini_.memory=action==Action::Think;
        screen_=Screen::Instructions;
        message_=mini_.memory?"Folge ansehen, dann nachspielen.":"Bewege den Korb. Fang mit OK.";
        return;
    case Action::Evolve:
        evolve();
        break;
    }
    update_call(false);
    record_change(before);
}

void Game::clock_button(Button button) {
    const int step = clock_field_ == 0 ? 60 : 1;
    int hour = clock_edit_ / 60, minute = clock_edit_ % 60;
    if (button == Button::Confirm) {
        if (clock_field_ == 0) { clock_field_ = 1; return; }
        state_.minute_of_day = clock_edit_;
        screen_ = Screen::Home;
        message_ = "Uhr gestellt.";
        update_call(false);
        return;
    }
    const int delta = button == Button::Right ? 1 : -1;
    if (step == 60) hour = (hour + 24 + delta) % 24;
    else minute = (minute + 60 + delta) % 60;
    clock_edit_ = static_cast<std::uint16_t>(hour * 60 + minute);
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
    if (screen_ == Screen::Clock) { clock_button(button); return; }
    if(screen_==Screen::Instructions) {
        if(button!=Button::Confirm) {screen_=Screen::Menu;return;}
        if(const auto* reason=blocked_reason(mini_.memory?Action::Think:Action::Play)) {message_=reason;screen_=Screen::Menu;return;}
        begin_game();return;
    }
    if (screen_ == Screen::Memory) {
        if(mini_.phase!=MiniPhase::Recall) return;
        mini_.last_button=static_cast<std::uint8_t>(button);mini_.input_ms=250;
        if (static_cast<std::uint8_t>(button) != mini_.pattern[mini_.entered]) {
            message_="Fast! Die Folge war anders.";finish_memory(false);return;
        }
        ++mini_.entered;
        if(mini_.entered==mini_.length) {message_="Richtig gemerkt!";finish_memory(true);}
        return;
    }
    if (screen_ == Screen::Game) {
        if(mini_.phase!=MiniPhase::Falling) return;
        if (button == Button::Left && mini_.lane > 0) --mini_.lane;
        if (button == Button::Right && mini_.lane < 2) ++mini_.lane;
        if (button == Button::Confirm) {
            const bool caught=mini_.lane==mini_.target && mini_.elapsed_ms>=catch_open_ms;
            message_=mini_.elapsed_ms<catch_open_ms?"Zu früh!":mini_.lane!=mini_.target?"Andere Spur!":"Gefangen!";
            next_round(caught);
        }
        return;
    }
    if (screen_ == Screen::Guide) { screen_ = Screen::Menu; return; }
    if (screen_ == Screen::Stats || screen_ == Screen::Result || screen_ == Screen::Evolved) { screen_ = Screen::Home; return; }
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
    screen_ = (screen_ == Screen::Guide || screen_==Screen::Instructions || screen_==Screen::Clock) ? Screen::Menu : Screen::Home;
}

void Game::memory_pattern() {
    mini_.elapsed_ms=0;mini_.entered=0;mini_.input_ms=0;mini_.last_button=3;
    mini_.recalling=false;mini_.phase=MiniPhase::Watch;
    mini_.length=static_cast<std::uint8_t>(2+mini_.round);
    message_="Gut hinsehen. Die Folge wächst.";
}
void Game::finish_memory(bool success) {
    mini_.success=success;mini_.recalling=false;
    if(success) {++mini_.round;++mini_.score;}
    mini_.elapsed_ms=0;mini_.phase=MiniPhase::Feedback;
}
} // namespace pet
