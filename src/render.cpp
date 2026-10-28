#include "pet/render.hpp"
#include "pet/catalog.hpp"
#include "pet/sprite.hpp"
#include <algorithm>
#include <cstdio>
#include <cstring>

namespace pet {
namespace {
#include "font.inc"

constexpr std::uint16_t rgb(unsigned r, unsigned g, unsigned b) {
    return static_cast<std::uint16_t>(((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3));
}
// Retro paper palette shared by every screen.
constexpr auto paper = rgb(232,229,207), ink = rgb(49,58,50), banner = rgb(56,71,56);
constexpr auto header_text = rgb(241,236,212), muted = rgb(89,97,79), warn = rgb(161,65,49);
constexpr auto good = rgb(81,108,73), bar_bg = rgb(200,203,181), selected = rgb(61,89,64);
constexpr auto selected_text = rgb(243,237,213), disabled = rgb(115,119,96), footer_bg = rgb(212,214,189);
constexpr auto footer_text = rgb(55,71,53), positive = rgb(72,101,63), rule = rgb(200,203,184);
constexpr auto rule2 = rgb(195,199,176), light = rgb(248,239,210), cost = rgb(140,68,51);

enum class Align { Left, Center, Right };

std::uint32_t next_codepoint(const char*& p) {
    const auto c = static_cast<std::uint8_t>(*p++);
    if (c < 0x80) return c;
    const int extra = c >= 0xf0 ? 3 : c >= 0xe0 ? 2 : c >= 0xc0 ? 1 : 0;
    if (extra == 0) return '?';
    std::uint32_t cp = c & (0x3fu >> extra);
    for (int i = 0; i < extra; ++i) {
        if ((static_cast<std::uint8_t>(*p) & 0xc0) != 0x80) return '?';
        cp = (cp << 6) | (static_cast<std::uint8_t>(*p++) & 0x3f);
    }
    return cp;
}
const Glyph* glyph(std::uint32_t cp) {
    const auto* end = glyphs + sizeof(glyphs) / sizeof(glyphs[0]);
    const auto* found = std::lower_bound(glyphs, end, cp, [](const Glyph& g, std::uint32_t v) { return g.codepoint < v; });
    return found != end && found->codepoint == cp ? found : nullptr;
}
int length(const char* text) {
    int count = 0;
    while (*text) { next_codepoint(text); ++count; }
    return count;
}
// ASCII and German umlauts to capitals; result lives in the caller's buffer.
const char* upper(const char* text, char* out, std::size_t size) {
    std::size_t i = 0;
    for (; *text && i + 1 < size; ++text) {
        auto c = static_cast<unsigned char>(*text);
        if (c >= 'a' && c <= 'z') c = static_cast<unsigned char>(c - 32);
        else if (c >= 0xa4 && i > 0 && static_cast<unsigned char>(out[i-1]) == 0xc3 &&
            (c == 0xa4 || c == 0xb6 || c == 0xbc)) c = static_cast<unsigned char>(c - 0x20);
        out[i++] = static_cast<char>(c);
    }
    out[i] = 0;
    return out;
}

class Painter {
public:
    explicit Painter(Band band) : band_(band) { unclip(); }
    void unclip() { x0_ = 0; y0_ = band_.top; x1_ = screen_width; y1_ = band_.top + band_.rows; }
    void clip(int x, int y, int w, int h) {
        x0_ = std::max(0, x); y0_ = std::max(band_.top, y);
        x1_ = std::min(screen_width, x + w); y1_ = std::min(band_.top + band_.rows, y + h);
    }
    bool visible(int y, int h) const { return y < y1_ && y + h > y0_; }
    void rect(int x, int y, int w, int h, std::uint16_t color) {
        const int left = std::max(x, x0_), right = std::min(x + w, x1_);
        const int top = std::max(y, y0_), bottom = std::min(y + h, y1_);
        for (int row = top; row < bottom; ++row) {
            auto* line = band_.pixels + (row - band_.top) * screen_width;
            for (int col = left; col < right; ++col) line[col] = color;
        }
    }
    void sprite(const Sprite& s, int x, int y, int scale, bool flip) {
        for (int sy = 0; sy < s.height; ++sy) {
            if (!visible(y + sy * scale, scale)) continue;
            for (int sx = 0; sx < s.width; ++sx) {
                const auto index = s.at(static_cast<unsigned>(flip ? s.width - 1 - sx : sx), static_cast<unsigned>(sy));
                if (index != 0) rect(x + sx * scale, y + sy * scale, scale, scale, s.palette[index]);
            }
        }
    }
    // Opaque copy of a scene region; palette index zero is a real color here.
    void scene(const Sprite& s, int sx, int sy, int w, int h, int dx, int dy) {
        for (int row = 0; row < h; ++row) {
            const int y = dy + row;
            if (y < y0_ || y >= y1_ || sy + row >= s.height) continue;
            auto* line = band_.pixels + (y - band_.top) * screen_width;
            for (int col = 0; col < w; ++col) {
                const int x = dx + col;
                if (x >= x0_ && x < x1_)
                    line[x] = s.palette[s.at(static_cast<unsigned>(sx + col), static_cast<unsigned>(sy + row))];
            }
        }
    }
    // Baseline coordinates like the earlier canvas UI; capitals are 7 * scale tall.
    void text(const char* value, int x, int baseline, int scale, std::uint16_t color, Align align = Align::Left) {
        const int width = text_width(value, scale);
        if (align == Align::Center) x -= width / 2;
        if (align == Align::Right) x -= width;
        const int top = baseline - 7 * scale;
        if (!visible(top, 9 * scale)) return;
        for (const char* p = value; *p; x += 6 * scale) {
            const auto* g = glyph(next_codepoint(p));
            if (!g) g = glyph('?');
            for (int row = 0; row < 9; ++row)
                for (int col = 0; col < 5; ++col)
                    if (g->rows[row] & (0x10 >> col)) rect(x + col * scale, top + row * scale, scale, scale, color);
        }
    }
    // Centered word wrap; returns the baseline after the last line.
    int wrap(const char* value, int baseline, int max_chars, std::uint16_t color, int line_height = 14) {
        char line[96] = "";
        int used = 0;
        const char* p = value;
        while (*p) {
            while (*p == ' ') ++p;
            const char* start = p;
            while (*p && *p != ' ') ++p;
            const auto bytes = static_cast<std::size_t>(p - start);
            if (bytes == 0) break;
            char word[64];
            std::snprintf(word, sizeof(word), "%.*s", static_cast<int>(std::min<std::size_t>(bytes, 63)), start);
            const int chars = length(word);
            if (used > 0 && used + 1 + chars > max_chars) {
                text(line, screen_width / 2, baseline, 1, color, Align::Center);
                baseline += line_height; line[0] = 0; used = 0;
            }
            if (used > 0) std::strncat(line, " ", sizeof(line) - std::strlen(line) - 1);
            std::strncat(line, word, sizeof(line) - std::strlen(line) - 1);
            used += (used > 0 ? 1 : 0) + chars;
        }
        if (used > 0) text(line, screen_width / 2, baseline, 1, color, Align::Center);
        return baseline + line_height;
    }
private:
    Band band_;
    int x0_ = 0, y0_ = 0, x1_ = 0, y1_ = 0;
};

const char* need_labels[] = {"Satt", "Froh", "Energie", "Sauber", "Gesund", "Bindung"};
std::uint8_t need_value(const State& s, int i) {
    const std::uint8_t values[] = {s.fullness, s.happiness, s.energy, s.hygiene, s.health, s.friendship};
    return values[i];
}
std::uint8_t pet_shrink(Stage stage) { return stage == Stage::Baby ? 2 : stage == Stage::Child ? 1 : 0; }

class Screen_ {
public:
    Screen_(const RenderInput& in, Band band) : in_(in), g_(in.game), s_(in.game.state()), p_(band) {}
    void draw();
private:
    const RenderInput& in_;
    const Game& g_;
    const State& s_;
    Painter p_;
    void bar(int x, int y, int width, int value, int low, int height = 8) {
        p_.rect(x, y, width, height, bar_bg);
        p_.rect(x, y, width * value / 100, height, value < low ? warn : good);
        for (int i = 1; i < 5; ++i) p_.rect(x + width * i / 5, y, 1, height, paper);
    }
    void centered_pet(int y, Species species, int height) {
        const auto sprite = animation_frame(species, Motion::Idle, 0).sprite;
        const int base = species == Species::Egg ? 4 : static_cast<int>(species_scale(species));
        const int scale = std::max(1, std::min({base, height / sprite.height, 184 / sprite.width}));
        p_.sprite(sprite, (screen_width - sprite.width * scale) / 2, y + (height - sprite.height * scale) / 2, scale, false);
    }
    void small_pet(int y, Species species, int height) {
        p_.clip(0, y, screen_width, height);
        p_.scene(forest_scene(false), 0, 60, screen_width, height, 0, y);
        centered_pet(y, species, height);
        p_.unclip();
    }
    void change_text(char* out, std::size_t size) const {
        const auto& f = g_.feedback();
        const int values[] = {f.fullness, f.happiness, f.energy, f.hygiene, f.health, f.friendship, f.experience};
        const char* labels[] = {"Satt", "Froh", "Energie", "Sauber", "Gesund", "Bindung", "EP"};
        out[0] = 0;
        for (int i = 0; i < 7; ++i) {
            if (!values[i]) continue;
            char part[24];
            std::snprintf(part, sizeof(part), "%s%s %+d", out[0] ? "  " : "", labels[i], values[i]);
            std::strncat(out, part, size - std::strlen(out) - 1);
        }
    }
    void header();
    void footer();
    void home();
    void starter();
    void menu();
    void guide();
    void stats();
    void intro();
    void catch_game();
    void memory_game();
    void result();
    void clock();
    void evolved();
};

void Screen_::header() {
    char name[48], line[48];
    p_.rect(0, 0, screen_width, 33, banner);
    const auto shown = g_.screen() == Screen::Starter ? Species::Egg : s_.species;
    p_.text(upper(species_name(shown), name, sizeof(name)), 12, 23, 2, header_text);
    if (shown != Species::Egg) {
        std::snprintf(line, sizeof(line), "Lv %u", g_.level());
        p_.text(line, 16 + text_width(name, 2), 23, 1, header_text);
    }
    std::snprintf(line, sizeof(line), "%02u:%02u", s_.minute_of_day / 60u, s_.minute_of_day % 60u);
    p_.text(line, 228, 23, 2, header_text, Align::Right);
}

void Screen_::footer() {
    p_.rect(0, 301, screen_width, 19, footer_bg);
    const char* text = "BELIEBIGE TASTE: ZURÜCK";
    switch (g_.screen()) {
    case Screen::Home: text = "◀ STATUS    OK: MENÜ    STATUS ▶"; break;
    case Screen::Menu: text = "▲ HOCH      OK: WAHL      RUNTER ▼"; break;
    case Screen::Game: text = "◀ LINKS    OK: FANGEN    RECHTS ▶"; break;
    case Screen::Starter: text = "◀ VORHER    OK: WAHL    WEITER ▶"; break;
    case Screen::Instructions: text = "◀ ZURÜCK    OK: START    ZURÜCK ▶"; break;
    case Screen::Memory: text = "◀ LINKS       OK       RECHTS ▶"; break;
    case Screen::Clock: text = "◀ WENIGER    OK: WEITER    MEHR ▶"; break;
    case Screen::Evolved: text = "BELIEBIGE TASTE: WEITER"; break;
    default: break;
    }
    p_.text(text, 120, 314, 1, footer_text, Align::Center);
}

void Screen_::home() {
    const bool dark = s_.sleeping || g_.night();
    p_.clip(0, 34, screen_width, 178);
    p_.scene(forest_scene(dark), 0, 0, screen_width, 178, 0, 34);
    if (s_.species == Species::Egg) centered_pet(115, Species::Egg, 96);
    else {
        const auto pose = in_.pose;
        const auto frame = animation_frame(s_.species, pose.motion, pose.frame);
        const auto place = place_frame(s_.species, pose, pet_shrink(g_.stage()));
        p_.sprite(frame.sprite, place.x, place.y, place.scale, pose.flip);
    }
    if (in_.trainer_name && *in_.trainer_name) {
        char greeting[48];
        std::snprintf(greeting, sizeof(greeting), "Hallo, %s!", in_.trainer_name);
        p_.rect(8, 36, std::min(224, length(greeting) * 6 + 8), 17, banner);
        p_.text(greeting, 12, 48, 1, light);
    }
    if (s_.sleeping) p_.text("Z z", 175, 109, 2, light);
    for (int i = 0; i < s_.waste; ++i) {
        p_.rect(15 + i * 13, 196, 9, 5, rgb(102,83,55)); p_.rect(18 + i * 13, 193, 4, 4, rgb(102,83,55));
    }
    if (s_.sick) { p_.rect(17, 58, 8, 22, warn); p_.rect(10, 65, 22, 8, warn); }
    if (g_.calling() && (in_.uptime_ms / 500) % 2 == 0) {
        // Attention bubble: the pet calls; ignoring it for 15 minutes is a care mistake.
        p_.rect(198, 40, 32, 26, ink); p_.rect(200, 42, 28, 22, paper); p_.rect(206, 66, 6, 4, ink);
        p_.text("!", 214, 61, 2, warn, Align::Center);
    }
    p_.unclip();
    if (s_.species == Species::Egg) {
        p_.text("Ein neuer Freund wartet.", 120, 241, 1, ink, Align::Center);
        char line[40];
        std::snprintf(line, sizeof(line), "Schlüpft in %u Min.", 10u - s_.age_minutes);
        p_.text(line, 120, 263, 1, muted, Align::Center);
        return;
    }
    for (int i = 0; i < 3; ++i) {
        const int x = 8 + i * 78, value = need_value(s_, i), low = Game::need_low[i];
        char upper_label[16], number[8];
        p_.text(upper(need_labels[i], upper_label, sizeof(upper_label)), x, 228, 1, ink);
        std::snprintf(number, sizeof(number), "%d", value);
        p_.text(number, x + 68, 228, 1, value < low ? warn : ink, Align::Right);
        bar(x, 236, 68, value, low);
    }
    if (g_.feedback().remaining_ms > 0) {
        char changes[96];
        change_text(changes, sizeof(changes));
        p_.text(changes, 120, 260, 1, positive, Align::Center);
    } else {
        const char* status = s_.sleeping ? "ERHOLT SICH" : g_.calling() ? "! RUFT DICH !" :
            g_.needs_attention() ? "ZEIT FÜR PFLEGE" : "FÜHLT SICH WOHL";
        p_.text(status, 120, 260, 1, g_.needs_attention() ? warn : muted, Align::Center);
    }
    p_.wrap(g_.needs_attention() ? g_.care_hint() : g_.message(), 280, 38, ink);
}

void Screen_::starter() {
    unsigned index = 0;
    while (index < starter_count() && starter_at(index) != s_.starter) ++index;
    char line[64], name[48];
    p_.text("DEIN ERSTER BEGLEITER", 120, 54, 1, ink, Align::Center);
    std::snprintf(line, sizeof(line), "%u / %u", index + 1, starter_count());
    p_.text(line, 120, 70, 1, muted, Align::Center);
    p_.clip(0, 78, screen_width, 128);
    p_.scene(forest_scene(false), 0, 32, screen_width, 128, 0, 78);
    centered_pet(78, s_.starter, 128);
    p_.unclip();
    // Paper tabs keep the browse arrows readable on the dark forest edges.
    p_.rect(6, 130, 22, 28, paper); p_.rect(212, 130, 22, 28, paper);
    p_.text("◀", 9, 153, 2, ink); p_.text("▶", 231, 153, 2, ink, Align::Right);
    upper(species_name(s_.starter), name, sizeof(name));
    p_.text(name, 120, 228, length(name) <= 16 ? 2 : 1, ink, Align::Center);
    const char* form = species_form(s_.starter);
    p_.text(*form ? form : "Neugierig auf dein Abenteuer.", 120, 246, 1, muted, Align::Center);
    const auto evolution = Game::evolution_of(s_.starter);
    if (evolution != Species::Egg) {
        std::snprintf(line, sizeof(line), "★ Kann zu %s werden", species_name(evolution));
        p_.text(line, 120, 266, 1, positive, Align::Center);
    } else p_.text("Seitentaste halten: blättern", 120, 266, 1, muted, Align::Center);
    p_.text("OK: Dieses Ei wählen", 120, 287, 1, ink, Align::Center);
}

void Screen_::menu() {
    char line[32];
    const auto sel = g_.selection();
    const auto action = Game::menu_action(sel);
    const bool enabled = !g_.blocked_reason(action);
    p_.text(Game::menu_section(sel), 12, 54, 1, ink);
    std::snprintf(line, sizeof(line), "%u / %u", sel + 1u, unsigned{Game::menu_count});
    p_.text(line, 226, 54, 1, muted, Align::Right);
    for (int row = 0; row < Game::menu_rows; ++row) {
        const auto index = static_cast<std::uint8_t>(g_.menu_start() + row);
        const auto item = Game::menu_action(index);
        const bool on = index == sel, ok = !g_.blocked_reason(item);
        const int y = 64 + row * 31;
        if (on) p_.rect(8, y, 218, 29, selected);
        else p_.rect(12, y + 29, 210, 1, rule);
        p_.text(on ? "▶" : ok ? "" : "-", 12, y + 21, 2, on ? selected_text : disabled);
        const char* label = item == Action::Sleep ? (s_.sleeping ? "Aufwecken" : "Schlafen") : action_name(item);
        p_.text(label, 30, y + 21, 2, on ? selected_text : ok ? ink : disabled);
    }
    const int track = 153, thumb = track * Game::menu_rows / Game::menu_count;
    p_.rect(232, 64, 2, track, rgb(194,199,173));
    p_.rect(231, 64 + g_.menu_start() * (track - thumb) / (Game::menu_count - Game::menu_rows), 4, thumb, rgb(101,119,86));
    p_.text(enabled ? "OK: AUSWÄHLEN" : "GERADE NICHT MÖGLICH", 12, 242, 1, enabled ? positive : warn);
    p_.wrap(g_.action_hint(action), 262, 38, ink);
    p_.text("OK halten: zurück", 120, 292, 1, muted, Align::Center);
}

void Screen_::guide() {
    p_.text("WAS BRAUCHE ICH?", 120, 58, 2, ink, Align::Center);
    p_.wrap(g_.care_hint(), 84, 38, ink);
    const char* tips[][2] = {{"! RUFT DICH", "Binnen 15 Min. kümmern, sonst Fehler"},
        {"HUNGER / LANGEWEILE", "Füttern, streicheln oder spielen"},
        {"MÜDE / NACHT", "Ab 21 Uhr schlafen lassen"},
        {"SCHMUTZIG / KRANK", "Saubermachen oder Medizin"}};
    for (int i = 0; i < 4; ++i) {
        p_.text(tips[i][0], 14, 124 + i * 42, 1, ink);
        p_.text(tips[i][1], 14, 140 + i * 42, 1, muted);
    }
}

void Screen_::stats() {
    p_.text("SO GEHT ES MIR", 14, 56, 2, ink);
    for (int i = 0; i < 6; ++i) {
        const int y = 76 + i * 25, value = need_value(s_, i), low = Game::need_low[i];
        char number[12];
        p_.text(need_labels[i], 14, y, 1, ink);
        p_.text(value < low && i < 5 ? "BRAUCHT PFLEGE" : value == 100 ? "VOLL" : "", 154, y, 1, value < low && i < 5 ? warn : muted, Align::Right);
        std::snprintf(number, sizeof(number), "%d/100", value);
        p_.text(number, 226, y, 1, ink, Align::Right);
        bar(14, y + 4, 212, value, i < 5 ? low : 0, 7);
    }
    char line[64];
    const unsigned day = (s_.age_minutes - std::min<std::uint32_t>(s_.age_minutes, 10)) / 1440 + 1;
    std::snprintf(line, sizeof(line), "★ Level %u  ·  %s  ·  Tag %u", g_.level(), stage_name(g_.stage()), day);
    p_.text(line, 14, 236, 1, ink);
    std::snprintf(line, sizeof(line), "%lu EP  ·  Pflegefehler %u", static_cast<unsigned long>(s_.experience), s_.care_mistakes);
    p_.text(line, 14, 251, 1, s_.care_mistakes > 3 ? warn : muted);
    const auto target = Game::evolution_of(s_.species);
    if (target == Species::Egg) {
        p_.text("Entwickelt sich nicht weiter.", 14, 272, 1, muted);
        p_.text("Pflegehilfe findest du im Menü.", 14, 288, 1, muted);
        return;
    }
    if (g_.can_evolve()) {
        p_.text("Bereit zur Entwicklung!", 14, 272, 1, positive);
        p_.text("Menü ▶ Entwickeln", 14, 288, 1, positive);
        return;
    }
    std::snprintf(line, sizeof(line), "Entwicklung zu %s:", species_name(target));
    p_.text(line, 14, 272, 1, ink);
    const unsigned need_bond = s_.species == static_cast<Species>(100) ? 90 : 70;
    char bond[12];
    std::snprintf(bond, sizeof(bond), "♥%u", need_bond);
    const struct { const char* label; bool met; } parts[] = {
        {"1 Tag", s_.age_minutes >= 1440}, {bond, s_.friendship >= need_bond}, {"60 EP", s_.experience >= 60},
        {"max 3 Fehler", s_.care_mistakes <= 3}, {"gesund", s_.health >= 60 && !s_.sick}};
    int x = 14;
    for (const auto& part : parts) {
        p_.text(part.label, x, 288, 1, part.met ? positive : warn);
        x += text_width(part.label, 1) + 8;
    }
}

void Screen_::intro() {
    const bool memory = g_.mini().memory;
    p_.text(memory ? "ENTONS DENKPAUSE" : "BEERENFANG", 120, 56, 2, ink, Align::Center);
    small_pet(66, memory ? Species::Psyduck : s_.species, 80);
    p_.text(memory ? "HINSEHEN. MERKEN. NACHSPIELEN." : "DREI SPUREN. FÜNF BEEREN.", 120, 164, 1, ink, Align::Center);
    p_.wrap(memory ? "Die Folge wächst: 2, 3, dann 4 Zeichen." : "Links / Rechts bewegt den Korb.", 185, 38, ink);
    p_.wrap(memory ? "Spiele sie mit Links, OK und Rechts nach." : "Drücke OK, wenn die Beere im Fangfeld ist.", 210, 38, ink);
    p_.rect(8, 240, 224, 1, rule2);
    p_.text("START: -5 SATT  /  -8 ENERGIE", 120, 258, 1, cost, Align::Center);
    p_.text(memory ? "Pro Runde: bis +4 froh, +2 Bindung" : "Pro Fang: bis +4 froh, +2 Bindung", 120, 276, 1, muted, Align::Center);
    p_.text("Dazu je +3 EP. Abbruch ohne Gewinn.", 120, 291, 1, muted, Align::Center);
}

void berry(Painter& p, int x, int y) {
    p.rect(x-7, y-5, 14, 12, rgb(101,61,45)); p.rect(x-9, y-2, 18, 7, rgb(101,61,45));
    p.rect(x-6, y-4, 12, 10, rgb(180,74,57)); p.rect(x-4, y-3, 4, 3, rgb(242,187,129));
    p.rect(x-2, y-9, 3, 5, rgb(73,105,60)); p.rect(x+1, y-9, 5, 3, rgb(124,148,80));
}

void Screen_::catch_game() {
    const auto& m = g_.mini();
    char line[32];
    p_.text("BEERENFANG", 12, 56, 2, ink);
    std::snprintf(line, sizeof(line), "%u/5", m.phase == MiniPhase::Feedback ? m.round : std::min(5, m.round + 1));
    p_.text(line, 228, 56, 2, ink, Align::Right);
    std::snprintf(line, sizeof(line), "%u gefangen", m.score);
    p_.text(line, 12, 72, 1, muted);
    p_.clip(0, 79, screen_width, 179);
    p_.scene(forest_scene(false), 0, 0, screen_width, 178, 0, 79);
    const int zone = 92 + static_cast<int>(130 * Game::catch_open_ms / Game::berry_duration_ms);
    p_.rect(8, zone, 224, 230 - zone, rgb(196,209,162));
    for (int lane = 0; lane < 3; ++lane) {
        const int x = 40 + lane * 80;
        p_.rect(x - 30, zone, 60, 2, rgb(92,120,73));
        p_.rect(x - 30, 230, 60, 2, rgb(92,120,73));
        p_.rect(x, 103, 1, zone - 108, rgb(145,160,118));
    }
    p_.text("FANGFELD", 120, zone - 6, 1, rgb(48,69,54), Align::Center);
    const int x = 40 + m.lane * 80;
    p_.rect(x-26, 239, 52, 17, rgb(106,77,49)); p_.rect(x-22, 240, 44, 13, rgb(186,137,80));
    p_.rect(x-30, 235, 60, 5, rgb(81,62,45)); p_.rect(x-19, 245, 38, 2, rgb(128,92,53));
    for (int i = -14; i <= 14; i += 14) p_.rect(x + i, 240, 2, 13, rgb(128,92,53));
    if (m.phase == MiniPhase::Falling)
        berry(p_, 40 + m.target * 80, 92 + static_cast<int>(130 * m.elapsed_ms / Game::berry_duration_ms));
    if (m.phase == MiniPhase::Ready || m.phase == MiniPhase::Feedback) {
        p_.rect(12, 122, 216, 47, paper);
        p_.text(m.phase == MiniPhase::Ready ? "BEREIT?" : m.success ? "GEFANGEN!" : "KNAPP DANEBEN", 120, 145, 2, ink, Align::Center);
        p_.text(m.phase == MiniPhase::Ready ? "Gleich fällt die erste Beere." : g_.message(), 120, 161, 1, muted, Align::Center);
    }
    p_.unclip();
    p_.rect(0, 258, screen_width, 43, paper);
    const char* hint = m.phase == MiniPhase::Falling && m.elapsed_ms >= Game::catch_open_ms ? "JETZT OK!" :
        m.phase == MiniPhase::Falling ? "Korb unter die Beere bewegen" : m.phase == MiniPhase::Ready ? "Tasten gleich aktiv" :
        m.round == 5 ? "Ergebnis folgt ..." : "Nächste Beere kommt ...";
    p_.text(hint, 120, 277, m.phase == MiniPhase::Falling && m.elapsed_ms >= Game::catch_open_ms ? 2 : 1, ink, Align::Center);
    p_.text("OK halten: Spiel verlassen", 120, 293, 1, muted, Align::Center);
}

void Screen_::memory_game() {
    const auto& m = g_.mini();
    char line[48];
    p_.text("ENTONS DENKPAUSE", 120, 56, 2, ink, Align::Center);
    std::snprintf(line, sizeof(line), "Runde %d / 3", std::min(3, m.phase == MiniPhase::Feedback && m.success ? m.round : m.round + 1));
    p_.text(line, 120, 71, 1, muted, Align::Center);
    small_pet(80, Species::Psyduck, 68);
    const char* phase = m.phase == MiniPhase::Ready ? "BEREIT?" : m.phase == MiniPhase::Watch ? "NUR ANSEHEN" :
        m.phase == MiniPhase::Recall ? "JETZT DU" : m.success ? "GUT GEMERKT!" : "NOCHMAL ÜBEN";
    p_.text(phase, 120, 169, 2, ink, Align::Center);
    const int active = m.phase == MiniPhase::Watch ? g_.memory_cue() :
        m.phase == MiniPhase::Recall && m.input_ms > 0 ? m.last_button : -1;
    const char* symbols[] = {"◀", "OK", "▶"};
    const char* names[] = {"LINKS", "MITTE", "RECHTS"};
    for (int i = 0; i < 3; ++i) {
        const bool lit = i == active;
        p_.rect(12 + i * 76, 179, 64, 46, lit ? rgb(61,89,64) : rgb(206,210,185));
        p_.text(symbols[i], 44 + i * 76, 212, 3, lit ? rgb(245,239,213) : rgb(83,96,71), Align::Center);
        p_.text(names[i], 44 + i * 76, 239, 1, muted, Align::Center);
    }
    for (int i = 0; i < m.length; ++i)
        p_.rect(120 - m.length * 12 + i * 24, 250, 16, 9, i < m.entered ? positive : rgb(195,201,173));
    if (m.phase == MiniPhase::Recall) {
        const auto duration = g_.mini_duration();
        p_.rect(12, 270, 216, 3, rgb(195,201,173));
        p_.rect(12, 270, static_cast<int>(216 * (duration - m.elapsed_ms) / duration), 3, rgb(89,111,72));
        std::snprintf(line, sizeof(line), "%u / %u Zeichen   %u s", m.entered, m.length, (duration - m.elapsed_ms + 999) / 1000);
        p_.text(line, 120, 290, 1, ink, Align::Center);
    } else if (m.phase == MiniPhase::Watch) {
        std::snprintf(line, sizeof(line), "%u Zeichen merken. Dann bist du dran.", m.length);
        p_.text(line, 120, 287, 1, muted, Align::Center);
    } else p_.text(m.phase == MiniPhase::Feedback ? g_.message() : "Gleich beginnt die Folge.", 120, 287, 1, muted, Align::Center);
}

void Screen_::result() {
    const auto& m = g_.mini();
    const auto& f = g_.feedback();
    char line[32];
    p_.text(m.score ? "GUT GESPIELT!" : "WEITER ÜBEN", 120, 56, 2, ink, Align::Center);
    small_pet(66, m.memory ? Species::Psyduck : s_.species, 88);
    std::snprintf(line, sizeof(line), "%u / %u %s", m.score, m.memory ? 3u : 5u, m.memory ? "Runden" : "Beeren");
    p_.text(line, 120, 180, 2, ink, Align::Center);
    const char* labels[] = {"Froh", "Bindung", "Erfahrung"};
    const int values[] = {f.happiness, f.friendship, f.experience};
    for (int i = 0; i < 3; ++i) {
        p_.text(labels[i], 20, 207 + i * 24, 1, ink);
        std::snprintf(line, sizeof(line), "+%d%s", values[i], i == 2 ? " EP" : "");
        p_.text(line, 220, 207 + i * 24, 1, positive, Align::Right);
        p_.rect(20, 213 + i * 24, 200, 1, rgb(198,203,180));
    }
    p_.text("Dein tatsächlich erhaltener Zuwachs.", 120, 287, 1, muted, Align::Center);
}

void Screen_::clock() {
    char line[8];
    p_.text("UHR STELLEN", 120, 58, 2, ink, Align::Center);
    const auto value = g_.clock_edit();
    std::snprintf(line, sizeof(line), "%02u:%02u", value / 60u, value % 60u);
    p_.text(line, 120, 150, 5, ink, Align::Center);
    const int left = 120 - text_width(line, 5) / 2;
    const int field_x = g_.clock_field() == 0 ? left : left + 18 * 5;
    p_.rect(field_x, 160, 11 * 5, 4, selected);
    p_.text(g_.clock_field() == 0 ? "STUNDE" : "MINUTE", field_x + 27, 180, 1, positive, Align::Center);
    p_.wrap("Links / Rechts ändern, halten blättert schnell. OK übernimmt.", 212, 38, ink);
    p_.text("Tag ab 07:00  ·  Nachtruhe ab 21:00", 120, 258, 1, muted, Align::Center);
    p_.text("OK halten: ohne Änderung zurück", 120, 278, 1, muted, Align::Center);
}

void Screen_::evolved() {
    char line[64];
    p_.text("ENTWICKLUNG!", 120, 58, 2, ink, Align::Center);
    small_pet(70, s_.species, 120);
    std::snprintf(line, sizeof(line), "%s wurde zu", species_name(g_.evolved_from()));
    p_.text(line, 120, 214, 1, ink, Align::Center);
    char name[48];
    p_.text(upper(species_name(s_.species), name, sizeof(name)), 120, 238, 2, positive, Align::Center);
    if (*species_form(s_.species)) p_.text(species_form(s_.species), 120, 256, 1, muted, Align::Center);
    p_.text("Eure Pflege hat sich gelohnt.", 120, 280, 1, muted, Align::Center);
}

void Screen_::draw() {
    p_.rect(0, 0, screen_width, screen_height, paper);
    header();
    switch (g_.screen()) {
    case Screen::Home: home(); break;
    case Screen::Starter: starter(); break;
    case Screen::Menu: menu(); break;
    case Screen::Guide: guide(); break;
    case Screen::Stats: stats(); break;
    case Screen::Instructions: intro(); break;
    case Screen::Game: catch_game(); break;
    case Screen::Memory: memory_game(); break;
    case Screen::Result: result(); break;
    case Screen::Clock: clock(); break;
    case Screen::Evolved: evolved(); break;
    }
    footer();
}
}

int text_width(const char* utf8, int scale) {
    const int count = length(utf8);
    return count ? count * 6 * scale - scale : 0;
}

bool text_supported(const char* utf8) {
    while (*utf8) if (!glyph(next_codepoint(utf8))) return false;
    return true;
}

void render(const RenderInput& input, Band band) {
    if (!band.pixels || band.rows <= 0) return;
    Screen_(input, band).draw();
}
}
