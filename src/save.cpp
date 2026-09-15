#include "pet/save.hpp"

namespace pet {
namespace {
std::uint32_t crc32(const std::uint8_t* bytes, std::size_t size) {
    std::uint32_t crc = 0xffffffffu;
    for (std::size_t i = 0; i < size; ++i) {
        crc ^= bytes[i];
        for (int bit = 0; bit < 8; ++bit)
            crc = (crc >> 1) ^ (0xedb88320u & (0u - (crc & 1u)));
    }
    return ~crc;
}
}

SaveBytes encode(const State& s) {
    SaveBytes bytes{};
    std::size_t pos = 0;
    const auto put = [&](std::uint32_t value, unsigned count) {
        for (unsigned i = 0; i < count; ++i) bytes[pos++] = static_cast<std::uint8_t>(value >> (8 * i));
    };
    put(0x31544550, 4); // PET1, explicit little-endian, never raw struct memory.
    put(3, 2);
    put(44, 2);
    put(s.age_minutes, 4); put(s.remainder_ms, 4); put(s.rng, 4); put(s.experience, 4);
    put(s.minute_of_day, 2); put(s.neglect_minutes, 2);
    put(s.fullness, 1); put(s.happiness, 1); put(s.energy, 1); put(s.hygiene, 1);
    put(s.health, 1); put(s.friendship, 1); put(s.waste, 1);
    put(static_cast<std::uint8_t>(s.species), 1); put(s.sleeping ? 1 : 0, 1); put(s.sick ? 1 : 0, 1);
    put(static_cast<std::uint8_t>(s.starter), 1); put(s.starter_chosen ? 1 : 0, 1);
    put(crc32(bytes.data(), 40), 4);
    return bytes;
}

bool decode(const std::uint8_t* bytes, std::size_t size, State& state) {
    if (bytes == nullptr || (size != 42 && size != 44)) return false;
    std::size_t pos = 0;
    const auto get = [&](unsigned count) {
        std::uint32_t value = 0;
        for (unsigned i = 0; i < count; ++i) value |= static_cast<std::uint32_t>(bytes[pos++]) << (8 * i);
        return value;
    };
    if (get(4) != 0x31544550) return false;
    const auto version = get(2);
    if (!((version == 1 && size == 42) || ((version == 2 || version == 3) && size == 44)) || get(2) != size) return false;
    State candidate;
    candidate.age_minutes = get(4); candidate.remainder_ms = get(4);
    candidate.rng = get(4); candidate.experience = get(4);
    candidate.minute_of_day = static_cast<std::uint16_t>(get(2));
    candidate.neglect_minutes = static_cast<std::uint16_t>(get(2));
    candidate.fullness = static_cast<std::uint8_t>(get(1));
    candidate.happiness = static_cast<std::uint8_t>(get(1));
    candidate.energy = static_cast<std::uint8_t>(get(1));
    candidate.hygiene = static_cast<std::uint8_t>(get(1));
    candidate.health = static_cast<std::uint8_t>(get(1));
    candidate.friendship = static_cast<std::uint8_t>(get(1));
    candidate.waste = static_cast<std::uint8_t>(get(1));
    candidate.species = static_cast<Species>(get(1));
    const auto sleeping = get(1), sick = get(1);
    if (sleeping > 1 || sick > 1) return false;
    candidate.sleeping = sleeping == 1; candidate.sick = sick == 1;
    if (version >= 2) {
        candidate.starter = static_cast<Species>(get(1));
        const auto chosen = get(1);
        if (chosen > 1) return false;
        candidate.starter_chosen = chosen == 1;
        if (version==2 && (static_cast<unsigned>(candidate.species)>4 ||
            (candidate.starter!=Species::Eevee && candidate.starter!=Species::Psyduck))) return false;
    } else {
        if (static_cast<unsigned>(candidate.species) > static_cast<unsigned>(Species::Umbreon)) return false;
        candidate.starter = Species::Eevee;
        candidate.starter_chosen = true;
    }
    if (get(4) != crc32(bytes, size - 4) || !Game::valid(candidate)) return false;
    state = candidate;
    return true;
}
} // namespace pet
