#include "pet/sprite.hpp"
#include <array>

namespace pet {
namespace {
// Authored here. Each hex digit is a palette index; zero is transparent.
// Packing happens at compile time: two pixels per byte, no heap or decoder buffer.
template<std::size_t N>
constexpr auto pack(const char (&source)[N]) {
    static_assert((N - 1) % 2 == 0, "Sprite pixel count must be even");
    std::array<std::uint8_t, (N - 1) / 2> result{};
    for (std::size_t i = 0; i < N - 1; ++i) {
        const auto value = static_cast<std::uint8_t>(source[i] <= '9' ? source[i] - '0' : source[i] - 'a' + 10);
        result[i / 2] |= static_cast<std::uint8_t>(value << (i % 2 == 0 ? 4 : 0));
    }
    return result;
}
constexpr std::uint16_t rgb(unsigned r, unsigned g, unsigned b) {
    return static_cast<std::uint16_t>(((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3));
}
constexpr std::uint16_t eevee_palette[] = {0,rgb(70,59,42),rgb(184,135,66),rgb(241,214,154),rgb(249,241,215),rgb(40,44,42)};
constexpr std::uint16_t espeon_palette[] = {0,rgb(70,59,42),rgb(167,125,136),rgb(217,178,173),rgb(249,241,215),rgb(40,44,42)};
constexpr std::uint16_t umbreon_palette[] = {0,rgb(37,47,48),rgb(74,80,80),rgb(199,163,72),rgb(249,241,215),rgb(40,44,42)};
constexpr std::uint16_t duck_palette[] = {0,rgb(88,66,30),rgb(228,180,47),rgb(250,213,81),rgb(249,243,218),rgb(32,39,32),rgb(211,159,67),rgb(245,218,150)};
constexpr std::uint16_t egg_palette[] = {0,rgb(55,71,53),rgb(244,237,207),rgb(173,132,74)};
constexpr auto eevee = pack(
    "000110000000000000110000"
    "000121000000000001210000"
    "000122100000000012210000"
    "000012221000000122100000"
    "000012221000001222100000"
    "000001222100012221000000"
    "000000121111112210000000"
    "000000122222222210000000"
    "000001222222222221000000"
    "000001244222244221000000"
    "000001215222215221000000"
    "000001215222215221000000"
    "000000122255222210000110"
    "000000012222221000012210"
    "000000133333331001222310"
    "000001333333333112223310"
    "000001233333322112333100"
    "000001222222222113110000"
    "000001222222222211100000"
    "000000122222222100000000"
    "000000122100012210000000"
    "000000111000001110000000");
constexpr auto duck = pack(
    "00000000000001001010000000000000"
    "00000000000001201210000000000000"
    "00000000000000111100000000000000"
    "00000000000011222211000000000000"
    "00000000001123333332211000000000"
    "00000000012333333333332100000000"
    "00000000123333333333333210000000"
    "00000001233333333333333321000000"
    "00000012333333333333333332100000"
    "00000012333444333334443332100000"
    "00000012334454433445444332100000"
    "00000012334454433445444332100000"
    "00000012333444333334443332100000"
    "00001112333333111113333321110000"
    "00012212333311777771133321221000"
    "00123312333177777777713321332100"
    "00123312233176777776713321232100"
    "00122312223177777777713221232100"
    "00012221222217777777122212321000"
    "00001222122221111111222122210000"
    "00000122212222222222221222100000"
    "00000012223333333333332221000000"
    "00000001233333333333333210000000"
    "00000001233333333333333210000000"
    "00000001233333333333332210000000"
    "00000001223333333333322210000000"
    "00000000122222222222222100000000"
    "00000000012222222222221000000000"
    "00000000116611111116611000000000"
    "00000001777610000167777100000000"
    "00000017777610000167777710000000"
    "00000011111100000011111100000000");
constexpr auto egg = pack(
    "000011110000" "000122221000" "001222222100" "012222222210"
    "012223322210" "122233222221" "122222223321" "122222233321"
    "122232222221" "012233222210" "001222222100" "000111111000");
static_assert(eevee.size() == 24 * 22 / 2 && duck.size() == 32 * 32 / 2 && egg.size() == 12 * 12 / 2);
}
Sprite sprite_for(Species species) {
    if (species == Species::Egg) return {egg.data(),egg_palette,12,12,4};
    if (species == Species::Psyduck) return {duck.data(),duck_palette,32,32,8};
    const auto* palette = species == Species::Espeon ? espeon_palette : species == Species::Umbreon ? umbreon_palette : eevee_palette;
    return {eevee.data(),palette,24,22,6};
}
std::size_t sprite_storage_bytes() {
    return sizeof(eevee) + sizeof(duck) + sizeof(egg) + sizeof(eevee_palette) + sizeof(espeon_palette) +
        sizeof(umbreon_palette) + sizeof(duck_palette) + sizeof(egg_palette);
}
}
