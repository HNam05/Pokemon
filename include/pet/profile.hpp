#pragma once
#include <array>
#include <cstddef>
#include <cstdint>
#include <cstring>

namespace pet {
// Configuration stays separate from save files and game rules. Names are rendered as data.
class Profile {
public:
    static constexpr std::size_t max_name_bytes = 24;
    bool set_name(const char* text, std::size_t size) {
        if (!text || size > max_name_bytes) return false;
        for (std::size_t i = 0; i < size;) {
            const auto c = static_cast<std::uint8_t>(text[i++]);
            if (c < 0x20 || c == 0x7f) return false;
            if (c < 0x80) continue;
            unsigned count = c >= 0xc2 && c <= 0xdf ? 1 : c >= 0xe0 && c <= 0xef ? 2 : c >= 0xf0 && c <= 0xf4 ? 3 : 0;
            if (count == 0 || size - i < count) return false;
            const auto next = static_cast<std::uint8_t>(text[i]);
            if ((c == 0xe0 && next < 0xa0) || (c == 0xed && next >= 0xa0) ||
                (c == 0xf0 && next < 0x90) || (c == 0xf4 && next >= 0x90)) return false;
            for (unsigned j = 0; j < count; ++j)
                if ((static_cast<std::uint8_t>(text[i++]) & 0xc0) != 0x80) return false;
        }
        name_.fill('\0');
        std::memcpy(name_.data(), text, size);
        return true;
    }
    const char* name() const { return name_.data(); }
private:
    std::array<char, max_name_bytes + 1> name_{};
};
}
