#pragma once
#include "pet/game.hpp"

namespace pet {
bool species_valid(Species species);
bool starter_valid(Species species);
unsigned starter_count();
Species starter_at(unsigned index);
Species next_starter(Species species, bool forward);
const char* roster_name(Species species);
const char* species_form(Species species);
const char* species_credit(Species species);
unsigned species_scale(Species species);
int species_anchor(Species species);
}
