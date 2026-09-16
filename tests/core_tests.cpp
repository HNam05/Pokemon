#include "pet/game.hpp"
#include "pet/save.hpp"
#include "pet/sprite.hpp"
#include "pet/profile.hpp"
#include "pet/animation.hpp"
#include "pet/catalog.hpp"
#include <cstdlib>
#include <iostream>

namespace {
int checks = 0;
void check(bool success, const char* description) {
    ++checks;
    if (!success) { std::cerr << "FAIL: " << description << '\n'; std::exit(1); }
}
void select(pet::Game& game, pet::Action action) {
    if (game.screen() != pet::Screen::Home) game.back();
    game.button(pet::Button::Confirm);
    while (game.menu_action(game.selection()) != action) game.button(pet::Button::Right);
    game.button(pet::Button::Confirm);
    if(game.screen()==pet::Screen::Instructions) {game.button(pet::Button::Confirm);game.advance(900);}
}
pet::State hatched() {
    pet::State state;
    state.species = pet::Species::Eevee;
    state.age_minutes = 10;
    state.starter_chosen = true;
    return state;
}
}

int main() {
    using namespace pet;
    Game game;
    check(game.screen() == Screen::Starter, "fresh game asks for starter");
    game.advance(60000, 3600);
    check(game.state().age_minutes == 0, "starter selection cannot age unattended");
    game.button(Button::Confirm);
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
    check(game.screen() == Screen::Menu, "blocked action stays in menu and explains why");
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
        game.advance(1300, 3600);
        game.button(Button::Confirm);
        game.advance(450);
    }
    check(game.screen() == Screen::Result && game.mini().score == 5, "five catches complete game");
    check(game.state().experience == 15 && game.state().friendship == 30, "reward applied once");
    check(game.state().age_minutes == game_start_age, "care time frozen during minigame");
    const auto reward = game.state().experience;
    game.button(Button::Confirm);
    check(game.state().experience == reward, "closing result cannot duplicate reward");
    select(game, Action::Play);
    game.advance(12000);
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

    Game duck;
    duck.button(Button::Right);
    check(duck.state().starter == Species::Psyduck, "right selects Enton");
    const auto chosen = encode(duck.state());
    State choice;
    check(decode(chosen.data(), chosen.size(), choice), "unconfirmed choice can be saved");
    Game resumed;
    resumed.restore(choice);
    check(resumed.screen() == Screen::Starter && resumed.state().starter == Species::Psyduck, "restore unfinished selection");
    duck.button(Button::Confirm);
    duck.advance(10000, 60);
    check(duck.state().species == Species::Psyduck, "Enton hatches");
    select(duck, Action::Evolve);
    check(!duck.can_evolve() && duck.state().species == Species::Psyduck, "Enton never becomes Eevee evolution");
    select(duck, Action::Guide);
    check(duck.screen() == Screen::Guide && duck.menu_start() > 0, "scroll reaches last menu entries");
    duck.back(); check(duck.screen() == Screen::Menu, "back preserves menu context");
    check(duck.menu_action(duck.selection()) == Action::Guide, "selection retained");
    select(duck, Action::Think);
    const auto memory_age = duck.state().age_minutes;
    duck.button(Button::Left);
    check(duck.mini().entered == 0, "memory playback ignores input");
    for (int round = 0; round < 3; ++round) {
        duck.advance(duck.mini_duration(), 3600);
        check(duck.mini().recalling, "memory enters recall");
        const auto length=duck.mini().length;
        for (unsigned i = 0; i < length; ++i) duck.button(static_cast<Button>(duck.mini().pattern[i]));
        duck.advance(900);
    }
    check(duck.screen() == Screen::Result && duck.mini().score == 3 && duck.state().experience == 9, "memory success rewards once");
    check(duck.state().age_minutes == memory_age, "memory keeps care clock frozen");
    duck.back(); check(duck.state().experience == 9, "back cannot duplicate memory rewards");
    select(duck, Action::Think); duck.advance(60000);
    check(duck.screen() == Screen::Result && duck.mini().score == 0, "memory times out with long tick");
    select(duck, Action::Think); duck.advance(duck.mini_duration());
    duck.button(static_cast<Button>((duck.mini().pattern[0]+1)%3));
    duck.advance(900);
    check(duck.screen() == Screen::Result && duck.mini().score == 0, "wrong memory answer fails");
    select(duck, Action::Think);
    const auto paid_energy = duck.state().energy;
    duck.back(); check(duck.screen() == Screen::Home && duck.state().energy == paid_energy, "cancel keeps paid game cost");

    // Independently calculated care changes and clamped feedback.
    state=hatched();state.fullness=50;state.happiness=50;state.energy=50;state.hygiene=100;
    game.restore(state);game.advance(60000,60);
    check(game.state().fullness==40 && game.state().happiness==45 && game.state().energy==40 && game.state().hygiene==94,"one hour awake has expected need decay");
    state.sleeping=true;game.restore(state);game.advance(60000,60);
    check(game.state().fullness==45 && game.state().happiness==50 && game.state().energy==80,"sleep restores energy, slows hunger, preserves happiness");
    state=hatched();state.fullness=85;state.happiness=99;game.restore(state);select(game,Action::Feed);
    check(game.state().fullness==100 && game.state().happiness==100 && game.feedback().fullness==15 && game.feedback().happiness==1,"receipt reports actual clamped feeding gains");
    state=hatched();state.happiness=29;game.restore(state);check(game.needs_attention(),"happiness warning starts below 30");
    state.happiness=30;game.restore(state);check(!game.needs_attention(),"happiness at 30 is not low");
    game.button(Button::Confirm);
    while(game.menu_action(game.selection())!=Action::Play)game.button(Button::Right);
    const auto free_preview=encode(game.state());game.button(Button::Confirm);
    check(game.screen()==Screen::Instructions && encode(game.state())==free_preview,"instructions cost nothing");
    game.advance(60000,3600);check(encode(game.state())==free_preview,"instruction reading freezes care");
    game.back();check(game.screen()==Screen::Menu && encode(game.state())==free_preview,"cancel intro retains resources");
    game.button(Button::Confirm);game.button(Button::Confirm);
    check(game.state().fullness==70 && game.state().energy==77,"start deducts game costs exactly once");
    game.button(Button::Confirm);check(game.mini().round==0,"ready phase ignores accidental confirmation");
    game.advance(900);game.advance(1199);game.button(Button::Confirm);
    check(game.mini().score==0 && game.mini().phase==MiniPhase::Feedback,"catch before exact window rejected");
    game.restore(hatched());select(game,Action::Play);
    while(game.mini().lane>game.mini().target)game.button(Button::Left);
    while(game.mini().lane<game.mini().target)game.button(Button::Right);
    game.advance(1200);game.button(Button::Confirm);game.button(Button::Confirm);
    check(game.mini().score==1 && game.mini().round==1,"exact catch boundary and duplicate input during feedback");
    game.restore(hatched());select(game,Action::Play);game.advance(1800);game.button(Button::Confirm);
    check(game.mini().phase==MiniPhase::Feedback && game.mini().round==1 && game.mini().score==0,"berry expires at exact upper boundary");
    game.restore(hatched());select(game,Action::Think);
    const auto frozen=game.mini().elapsed_ms;game.advance(60000,0);
    check(game.mini().phase==MiniPhase::Watch && game.mini().elapsed_ms==frozen,"pause freezes active memory phase");
    Game partitioned=game;game.advance(1000,3600);
    for(unsigned i=0;i<10;++i)partitioned.advance(100,1);
    check(game.mini().elapsed_ms==partitioned.mini().elapsed_ms && game.memory_cue()==partitioned.memory_cue() &&
        encode(game.state())==encode(partitioned.state()),"memory timing independent of tick size and demo multiplier");
    state=hatched();state.happiness=99;state.friendship=99;state.experience=999999;
    game.restore(state);select(game,Action::Think);
    game.advance(game.mini_duration());
    for(unsigned i=0;i<2;++i)game.button(static_cast<Button>(game.mini().pattern[i]));
    game.advance(900);check(game.mini().length==3,"memory grows from two to three symbols");
    game.advance(game.mini_duration());game.button(static_cast<Button>((game.mini().pattern[0]+1)%3));game.advance(900);
    check(game.screen()==Screen::Result && game.mini().score==1,"completed memory rounds retained after mistake");
    check(game.state().happiness==100 && game.state().friendship==100 && game.state().experience==1000000 &&
        game.feedback().happiness==1 && game.feedback().friendship==1 && game.feedback().experience==1,"result reports clamped partial rewards exactly");
    const auto once=encode(game.state());game.button(Button::Confirm);check(encode(game.state())==once,"partial reward cannot duplicate");

    Profile profile;
    check(profile.set_name("Ada",3), "name accepted");
    check(!profile.set_name("X\nY",3) && std::string(profile.name()) == "Ada", "invalid name rejected transactionally");
    check(!profile.set_name("\xc0\xaf",2), "overlong UTF-8 rejected");
    check(!profile.set_name("\xed\xa0\x80",3), "UTF-8 surrogate rejected");
    check(!profile.set_name("\xf4\x90\x80\x80",4), "Unicode overflow rejected");
    check(profile.set_name("J\xc3\xb6rg",5), "UTF-8 name accepted");
    check(!profile.set_name("1234567890123456789012345",25), "name has fixed storage bound");
    check(profile.set_name("",0), "empty profile supported");
    check(sprite_storage_bytes() == 908, "all packed art and palettes total 908 bytes");
    for (unsigned species = 0; species <= 4; ++species) {
        const auto sprite = sprite_for(static_cast<Species>(species));
        for (unsigned y = 0; y < sprite.height; ++y)
            for (unsigned x = 0; x < sprite.width; ++x)
                check(sprite.at(x,y) < sprite.colors, "sprite index within palette");
        check(sprite.at(sprite.width,0) == 0, "out of bounds sprite pixel transparent");
    }
    static_assert(sizeof(Game) <= 128, "Core RAM budget exceeded");
    static_assert(sizeof(Profile) == 25, "Profile RAM budget exceeded");
    state = hatched(); state.health = 35; game.restore(state);
    check(game.needs_attention() && std::string(game.care_hint()) == "Medizin, dann weiter pflegen.", "low health has actionable care hint");
    state = hatched(); state.hygiene = 24; game.restore(state);
    check(game.needs_attention() && std::string(game.care_hint()) == "Bitte saubermachen.", "low hygiene attention matches recommendation");
    std::cout << "RAM host: Game=" << sizeof(Game) << " State=" << sizeof(State)
              << " Profile=" << sizeof(Profile) << "; sprites=" << sprite_storage_bytes() << " bytes\n";

    // Animation policy is cosmetic, bounded, and deterministic for a supplied seed.
    {
        Animator a(42), b(42);
        auto pet = hatched();
        const auto saved = encode(pet);
        bool seen[motion_count]{};
        for (unsigned step=0; step<3000; ++step) {
            a.advance(pet,100); b.advance(pet,100);
            const auto v=a.view(pet), other=b.view(pet);
            seen[static_cast<unsigned>(v.motion)]=true;
            check(v.motion==other.motion && v.frame==other.frame && v.x==other.x, "seeded animations repeat deterministically");
            check(v.frame<frame_count(pet.species,v.motion) && v.x>=-24 && v.x<=24, "animation frame and movement bounded");
        }
        check(seen[0] && seen[1] && seen[2] && seen[3] && seen[8], "idle schedule includes walk hop joy and look");
        check(saved==encode(pet), "animation never changes save or gameplay RNG");
        a.fed(pet); check(a.view(pet).motion==Motion::Eat,"feed triggers eating");
        a.advance(pet,2200); check(a.view(pet).motion==Motion::Idle,"eating settles into rest");
        pet.sleeping=true; a.advance(pet,0); check(a.view(pet).motion==Motion::Sleep,"sleep interrupts active clip");
        pet.sick=true; a.advance(pet,4000); check(a.view(pet).motion==Motion::Sleep,"sleep has priority while ill");
        pet.sleeping=false; a.advance(pet,0); check(a.view(pet).motion==Motion::Sick,"ill pet does not celebrate");
        pet.sick=false; pet.energy=10; a.advance(pet,0); check(a.view(pet).motion==Motion::Tired,"low energy rests");
        pet.energy=80; pet.fullness=10;
        for(unsigned i=0;i<200;++i) { a.advance(pet,500); check(a.view(pet).motion!=Motion::Happy && a.view(pet).motion!=Motion::Hop,"hungry pet avoids celebration"); }
        const auto paused=a.view(pet); a.advance(pet,0); check(a.view(pet).frame==paused.frame && a.view(pet).x==paused.x,"zero time freezes pose");
        pet=hatched(); Animator chunks(7), single(7); chunks.advance(pet,0); single.advance(pet,0);
        for(unsigned i=0;i<60;++i) chunks.advance(pet,1000);
        single.advance(pet,60000);
        check(chunks.view(pet).motion==single.view(pet).motion && chunks.view(pet).frame==single.view(pet).frame,"animation clock independent of chunk size");
        for(unsigned s=0;s<5;++s) for(unsigned m=0;m<motion_count;++m) {
            const auto species=static_cast<Species>(s); const auto motion=static_cast<Motion>(m);
            for(unsigned f=0;f<frame_count(species,motion);++f) {
                const auto frame=animation_frame(species,motion,f);
                check(frame.duration_ms>0 && frame.sprite.width>0 && frame.sprite.height>0,"valid frame geometry and duration");
                bool opaque=false;
                for(unsigned y=0;y<frame.sprite.height;++y) for(unsigned x=0;x<frame.sprite.width;++x) {
                    const auto pixel=frame.sprite.at(x,y); opaque|=pixel!=0;
                    check(pixel<frame.sprite.colors,"animation palette index valid");
                }
                check(opaque,"animation frame not blank");
            }
        }
        static_assert(sizeof(Animator)<=32,"animator RAM budget");
        check(animation_storage_bytes()<1024*1024,"complete roster animation budget below 1 MiB");
        std::cout << "Animation host: Animator=" << sizeof(Animator) << " asset bytes=" << animation_storage_bytes() << '\n';
    }
    {
        check(starter_count()==130,"all 129 imported sets plus project Enton selectable");
        bool ids[256]{};
        Game selection;
        selection.button(Button::Left);
        check(selection.state().starter==starter_at(starter_count()-1),"starter list wraps backward");
        selection.button(Button::Right);
        check(selection.state().starter==Species::Eevee,"starter list wraps forward");
        for(unsigned i=0;i<starter_count();++i) {
            const auto species=starter_at(i);const auto id=static_cast<unsigned>(species);
            check(!ids[id] && starter_valid(species),"catalog IDs unique and valid");ids[id]=true;
            State egg;egg.starter=species;
            Game pet;check(pet.restore(egg),"every starter selection restores");
            pet.button(Button::Confirm);pet.advance(60000,10);
            check(pet.state().species==species && Game::valid(pet.state()),"every starter hatches correctly");
            const auto bytes=encode(pet.state());State loaded;
            check(decode(bytes.data(),bytes.size(),loaded) && loaded.species==species && loaded.starter==species,"every catalog ID survives V3 save");
            if(species!=Species::Eevee) check(!pet.can_evolve(),"no invented evolution for new species");
            for(unsigned m=0;m<motion_count;++m) for(unsigned f=0;f<frame_count(species,static_cast<Motion>(m));++f) {
                const auto frame=animation_frame(species,static_cast<Motion>(m),f);
                check(frame.duration_ms>0 && frame.sprite.width>0 && frame.sprite.height>0,"catalog frame valid");
                bool visible=false;
                for(unsigned y=0;y<frame.sprite.height;++y) for(unsigned x=0;x<frame.sprite.width;++x) {
                    const auto pixel=frame.sprite.at(x,y);visible|=pixel!=0;
                    check(pixel<frame.sprite.colors,"catalog palette bounds");
                }
                check(visible,"catalog frame visible");
                for(const bool flip:{false,true}) for(const int travel:{-24,0,24}) {
                    const auto pos=place_frame(species,{static_cast<Motion>(m),static_cast<std::uint8_t>(f),static_cast<std::int8_t>(travel),-10,flip});
                    check(pos.x>=8 && pos.x+frame.sprite.width*pos.scale<=232 &&
                        pos.y>=42 && pos.y+frame.sprite.height*pos.scale<=210,"enlarged frames fit at both travel extremes and mirrored");
                }
            }
        }
        check(!species_valid(static_cast<Species>(255)) && !starter_valid(Species::Egg),"unknown species rejected");
        auto invalid=hatched();invalid.starter=starter_at(2);
        check(!Game::valid(invalid),"unrelated species ancestry rejected");
        check(species_scale(Species::Eevee)==5 && species_scale(Species::Psyduck)==4,"original companions visibly larger");
        const auto day=forest_scene(false),night=forest_scene(true);
        check(day.width==240 && day.height==178 && day.pixels==night.pixels,"day and night share scene pixels");
        check(scene_storage_bytes()==21424,"scene budget includes both palettes");
        unsigned changed=0;
        for(unsigned y=0;y<day.height;++y) for(unsigned x=0;x<day.width;++x) {
            const auto index=day.at(x,y);
            check(index<day.colors,"scene palette index in bounds");
            changed+=day.palette[index]!=night.palette[index];
        }
        check(changed==240*178,"night palette changes entire scene");
    }
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
